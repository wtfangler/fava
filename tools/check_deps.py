#!/usr/bin/env python3
"""Offline, per-side Fabric dependency preflight (not a replacement for Loader).

Usage: python tools/check_deps.py <jar_dir> --side both --index <pack.mrpack>
       --fabric-loader-jar <fabric-loader-VERSION.jar>
No downloads happen unless --download is explicitly supplied. Hashes, manifest
environments, nested jars, aliases, Java/MC/Loader requirements and breaks are
checked. Nested alternatives use the highest version; unresolved ambiguity and
unsupported predicate syntax fail clearly, never silently pass.
"""
import argparse
from functools import cmp_to_key
import io
import json
from pathlib import Path
import re
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from server.build_server import BuildError, ensure_file, safe_relative, verify

# Fabric's superset accepts arbitrary build metadata after the FIRST '+',
# leading zeroes in numeric core components, and an empty prerelease. See:
# fabric-loader/0.19.5/.../impl/util/version/SemanticVersionImpl.java
CORE_VERSION = re.compile(r"[0-9]+(?:\.[0-9]+)*")
PRERELEASE = re.compile(r"(?:[-0-9A-Za-z]+(?:\.[-0-9A-Za-z]+)*)?")
NUMERIC_IDENTIFIER = re.compile(r"0|[1-9][0-9]*")


class PredicateError(ValueError):
    pass


def semantic(version):
    if not isinstance(version, str):
        return None
    before_build = version.partition("+")[0]
    numbers, marker, pre = before_build.partition("-")
    if not CORE_VERSION.fullmatch(numbers) or (marker and not PRERELEASE.fullmatch(pre)):
        return None
    # Loader uses Java Integer.parseInt for core components. Reject values that
    # Loader would fall back to StringVersion, without unbounded int parsing.
    normalized = [part.lstrip("0") or "0" for part in numbers.split(".")]
    if any(len(part) > 10 or (len(part) == 10 and part > "2147483647") for part in normalized):
        return None
    return tuple(map(int, normalized)), (pre.split(".") if pre else []) if marker else None


def compare(left, right):
    a, b = semantic(left), semantic(right)
    if a is None or b is None:
        raise PredicateError(f"Cannot order non-semantic versions: {left!r}, {right!r}")
    count = max(len(a[0]), len(b[0]))
    av, bv = a[0] + (0,) * (count - len(a[0])), b[0] + (0,) * (count - len(b[0]))
    if av != bv:
        return (av > bv) - (av < bv)
    if a[1] is None or b[1] is None:
        return (a[1] is None) - (b[1] is None)
    for aa, bb in zip(a[1], b[1]):
        if aa == bb:
            continue
        a_numeric = NUMERIC_IDENTIFIER.fullmatch(aa) is not None
        b_numeric = NUMERIC_IDENTIFIER.fullmatch(bb) is not None
        if a_numeric and b_numeric:
            # Numeric prerelease identifiers can exceed Python's int-digit
            # conversion limit; Fabric compares their lengths then text.
            if len(aa) != len(bb):
                return (len(aa) > len(bb)) - (len(aa) < len(bb))
        if a_numeric != b_numeric:
            return -1 if a_numeric else 1
        return (aa > bb) - (aa < bb)
    return (len(a[1]) > len(b[1])) - (len(a[1]) < len(b[1]))


def term(have, text):
    if text == "*":
        return True
    match = re.fullmatch(r"(>=|<=|>|<|=|~|\^)?([^\s]+)", text)
    if not match:
        raise PredicateError(f"Unsupported Fabric predicate: {text!r}")
    operator, wanted = match.group(1) or "=", match.group(2)
    before_build = wanted.partition("+")[0]
    if "," in before_build or "|" in before_build:
        raise PredicateError(f"Unsupported Fabric predicate: {text!r}")
    # Metadata such as 0.7.7+fix3+26.3 or 1.2.3+build.x is not an X-range.
    core, prerelease_marker, _ = before_build.partition("-")
    parts = core.split(".")
    wild = next((i for i, p in enumerate(parts) if p in ("x", "X", "*")), None)
    if wild is not None:
        if operator != "=" or wild == 0 or prerelease_marker or any(p not in ("x", "X", "*") for p in parts[wild:]) or not all(p.isdigit() for p in parts[:wild]):
            raise PredicateError(f"Unsupported wildcard predicate: {text!r}")
        parsed = semantic(have)
        if parsed is None:
            return False
        components = parsed[0] + (0,) * max(0, wild - len(parsed[0]))
        return components[:wild] == tuple(map(int, parts[:wild]))
    a, b = semantic(have), semantic(wanted)
    if a is None or b is None:
        if operator != "=":
            raise PredicateError(f"Ordered non-semantic predicate unsupported: {text!r} against {have!r}")
        return have == wanted
    c = compare(have, wanted)
    if operator == "^":
        return c >= 0 and a[0][0] == b[0][0]  # Fabric: no special rule for major 0.
    if operator == "~":
        return c >= 0 and (a[0] + (0,))[:2] == (b[0] + (0,))[:2]
    return {"=": c == 0, ">": c > 0, "<": c < 0, ">=": c >= 0, "<=": c <= 0}[operator]


def matches(have, constraint):
    alternatives = [constraint] if isinstance(constraint, str) else constraint
    if not isinstance(alternatives, list) or not alternatives or not all(isinstance(c, str) for c in alternatives):
        raise PredicateError(f"Invalid version constraint: {constraint!r}")
    # Evaluate every term/alternative even if another already matched, so invalid
    # metadata cannot hide behind '*' or an earlier successful OR alternative.
    results = [all([term(have, t) for t in c.split()]) for c in alternatives]
    return any(results)


def read_manifest(path):
    path = Path(path)
    if path.suffix == ".mrpack":
        with zipfile.ZipFile(path) as archive:
            return json.loads(archive.read("modrinth.index.json"))
    data = json.loads(path.read_text(encoding="utf8"))
    if "files" not in data:
        data["files"] = data.get("base", []) + data.get("added", [])
    return data


def scan(archive, owner, side, top_level=True, depth=0):
    if depth > 16:
        raise BuildError(f"Nested jar depth exceeded: {owner}")
    try:
        metadata = json.loads(archive.read("fabric.mod.json").decode("utf8"), strict=False)
    except KeyError:
        if top_level:
            raise BuildError(f"No fabric.mod.json: {owner}")
        return []  # Some declared nested libraries are plain Java jars.
    if not isinstance(metadata, dict) or metadata.get("schemaVersion", 0) != 1:
        raise BuildError(f"Unsupported Fabric metadata schema: {owner}")
    environment = metadata.get("environment", "*")
    if environment not in ("*", "client", "server"):
        raise BuildError(f"Unsupported environment {environment!r}: {owner}")
    if environment not in ("*", side):
        return []
    if not isinstance(metadata.get("id"), str) or not isinstance(metadata.get("version"), str):
        raise BuildError(f"Missing mod id/version: {owner}")
    metadata = dict(metadata, owner=owner, top_level=top_level)
    mods = [metadata]
    for nested in metadata.get("jars", []):
        name = safe_relative(nested["file"])
        try:
            data = archive.read(name)
        except KeyError as exc:
            raise BuildError(f"Declared nested jar missing: {owner}!{name}") from exc
        with zipfile.ZipFile(io.BytesIO(data)) as child:
            mods.extend(scan(child, owner + "!" + name, side, False, depth + 1))
    return mods


def loader_builtins(path, loader, side):
    """Read actual Loader-bundled mod metadata, never invent library versions."""
    path = Path(path)
    with zipfile.ZipFile(path) as archive:
        metadata = json.loads(archive.read("fabric.mod.json"))
        if metadata.get("id") != "fabricloader" or metadata.get("version") != loader:
            raise BuildError(f"Fabric Loader jar does not match requested {loader}: {path}")
        entries = scan(archive, str(path), side)
    # fabricloader itself is a runtime builtin already provided by audit().
    # The declared nested jars participate in normal version selection.
    return [entry for entry in entries if not entry["top_level"]]


def find_loader_jar(directory, loader):
    directory = Path(directory)
    filename = f"fabric-loader-{loader}.jar"
    candidates = [directory / filename,
                  directory.parent / "libraries" / "net" / "fabricmc" / "fabric-loader" / loader / filename,
                  ROOT / "journal-mod" / ".dev" / "tools" / filename]
    return next((path for path in candidates if path.is_file()), None)


def audit(directory, side, manifest=None, minecraft="26.2", loader="0.19.5", java="25", download=False, loader_jar=None):
    directory = Path(directory)
    errors, warnings, mods = [], [], []
    indexed = {}
    if manifest:
        for entry in manifest["files"]:
            relative = safe_relative(entry["path"])
            if relative.startswith("mods/"):
                name = Path(relative).name
                if name in indexed:
                    errors.append(f"Duplicate manifest filename: {name}")
                indexed[name] = entry
        dependencies = manifest.get("dependencies", {})
        minecraft = dependencies.get("minecraft", minecraft)
        loader = dependencies.get("fabric-loader", loader)
    loader_jar = Path(loader_jar) if loader_jar is not None else find_loader_jar(directory, loader)
    if loader_jar is not None:
        try:
            mods.extend(loader_builtins(loader_jar, loader, side))
        except (BuildError, ValueError, OSError, KeyError, zipfile.BadZipFile) as exc:
            errors.append(f"Invalid Fabric Loader builtin metadata: {exc}")
    else:
        warnings.append("Fabric Loader bundled mods not audited; supply --fabric-loader-jar for the complete runtime dependency set")
    for name, entry in indexed.items():
        environment = entry.get("env", {}).get(side, "required")
        if environment not in ("required", "optional", "unsupported"):
            errors.append(f"Invalid manifest {side} environment: {name}")
            continue
        if environment == "unsupported":
            continue
        dest = directory / name
        try:
            if download:
                ensure_file(entry, dest)
            elif dest.is_file():
                verify(dest, entry)
            else:
                errors.append(f"Missing {side} jar: {name} ({environment})")
        except (BuildError, OSError) as exc:
            errors.append(str(exc))
    if directory.is_dir():
        for path in sorted(directory.glob("*.jar")):
            if loader_jar is not None and path.resolve() == loader_jar.resolve():
                continue
            if path.name in indexed and indexed[path.name].get("env", {}).get(side) == "unsupported":
                continue
            try:
                with zipfile.ZipFile(path) as archive:
                    mods.extend(scan(archive, path.name, side))
            except (BuildError, ValueError, OSError, KeyError, zipfile.BadZipFile) as exc:
                errors.append(f"Invalid jar {path.name}: {exc}")
    else:
        errors.append(f"Jar directory not found: {directory}")
    candidates = {}
    for mod in mods:
        candidates.setdefault(mod["id"], []).append(mod)
    selected = []
    for mid, entries in candidates.items():
        roots = [m for m in entries if m["top_level"]]
        if len(roots) > 1:
            errors.append(f"Duplicate top-level mod {mid}: " + ", ".join(m["owner"] for m in roots))
            continue
        if roots:
            chosen = roots[0]
        else:
            versions = {m["version"] for m in entries}
            try:
                chosen = max(entries, key=cmp_to_key(lambda a, b: compare(a["version"], b["version"]))) if len(versions) > 1 else entries[0]
            except PredicateError as exc:
                errors.append(f"Ambiguous nested mod {mid}: {exc}")
                continue
            if len(versions) > 1:
                warnings.append(f"Nested alternatives {mid}: assumed highest {chosen['version']}; Loader must confirm selection")
        selected.append(chosen)
    provided = {"minecraft": (minecraft, "runtime"), "fabricloader": (loader, "runtime"), "java": (java, "runtime")}
    for mod in selected:
        aliases = mod.get("provides", [])
        if not isinstance(aliases, list) or not all(isinstance(alias, str) for alias in aliases):
            errors.append(f"Unsupported provides metadata: {mod['id']}")
            aliases = []
        for mid in [mod["id"], *aliases]:
            if mid in provided and provided[mid][1] != mod["id"]:
                errors.append(f"Duplicate mod/alias provider {mid}: {provided[mid][1]}, {mod['id']}")
            provided[mid] = (mod["version"], mod["id"])
    for mod in selected:
        for kind in ("depends", "breaks", "recommends", "conflicts"):
            entries = mod.get(kind, {})
            if not isinstance(entries, dict):
                errors.append(f"Invalid {kind} metadata: {mod['id']}")
                continue
            for dep, constraint in entries.items():
                try:
                    # Parse even absent constraints to detect unsupported syntax.
                    match = matches(provided[dep][0] if dep in provided else "0", constraint)
                except PredicateError as exc:
                    errors.append(f"UNSUPPORTED {mod['id']} {kind} {dep}: {exc}")
                    continue
                detail = f"{mod['id']} ({mod['owner']}) {kind} {dep} {constraint!r}"
                if kind == "depends" and (dep not in provided or not match):
                    errors.append(f"DEPENDENCY {detail}; have {provided.get(dep, ('missing',))[0]}")
                elif kind == "breaks" and dep in provided and match:
                    errors.append(f"BREAKS {detail}; have {provided[dep][0]}")
                elif kind == "recommends" and (dep not in provided or not match):
                    warnings.append(f"RECOMMENDS {detail}")
                elif kind == "conflicts" and dep in provided and match:
                    warnings.append(f"CONFLICTS {detail}")
    return {"side": side, "entries": len(mods), "selected": len(selected), "errors": errors, "warnings": warnings,
            "loader_jar": str(loader_jar) if loader_jar is not None else None}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory")
    parser.add_argument("--side", choices=("client", "server", "both"), default="both")
    parser.add_argument("--index", "--manifest", dest="manifest", help="mrpack, index.json or lock.json (default tools/lock.json)")
    parser.add_argument("--minecraft", default="26.2")
    parser.add_argument("--loader", default="0.19.5")
    parser.add_argument("--java", default="25", help="Java major to check, not the Python host runtime")
    parser.add_argument("--fabric-loader-jar", "--loader-jar", dest="loader_jar", help="actual runtime Fabric Loader jar; audits its declared bundled mods offline")
    parser.add_argument("--download", action="store_true", help="explicitly download missing indexed jars")
    args = parser.parse_args(argv)
    try:
        manifest_path = Path(args.manifest) if args.manifest else ROOT / "tools" / "lock.json"
        manifest = read_manifest(manifest_path) if manifest_path.is_file() else None
        if args.manifest and manifest is None:
            raise BuildError(f"Manifest not found: {args.manifest}")
        total = 0
        for side in (("client", "server") if args.side == "both" else (args.side,)):
            result = audit(args.directory, side, manifest, args.minecraft, args.loader, args.java, args.download, args.loader_jar)
            if result["loader_jar"]:
                print(f"[{side}] Runtime bundled mods read from {result['loader_jar']}")
            for message in result["errors"]:
                print(f"[{side}] ERROR {message}")
            for message in result["warnings"]:
                print(f"[{side}] WARN {message}")
            print(f"[{side}] {result['entries']} mod entries, {result['selected']} selected: {len(result['errors'])} error(s), {len(result['warnings'])} warning(s)")
            total += len(result["errors"])
        print("Static preflight only. A clean Fabric Loader startup is still required.")
        return 1 if total else 0
    except (BuildError, ValueError, OSError, KeyError, zipfile.BadZipFile) as exc:
        parser.exit(1, f"Audit failed: {exc}\n")


if __name__ == "__main__":
    sys.exit(main())
