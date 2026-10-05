#!/usr/bin/env python3
"""Build a Fabric server. Existing configs/scripts/settings are preserved.

Use a NEW output directory when changing mods or Minecraft/Fabric versions.
--no-download prepares configs and embedded mods; it is not a runnable server.
Worlds are never changed by this tool. Java 25+ is required to run the server.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import tempfile
import urllib.request
import zipfile

HERE = Path(__file__).resolve().parent
UA = {"User-Agent": "Fancy-Vanilla/2.0.4 (server builder)"}
CLIENT_DIRS = ("resourcepacks", "shaderpacks", "screenshots", "config/jei")
CLIENT_FILES = {"options.txt", "servers.dat", "servers.dat_old"}
STATE_FILE = ".expedition-server-build.json"


class BuildError(ValueError):
    pass


def safe_relative(name):
    """Portable archive paths; reject traversal AND Windows path aliases."""
    if not isinstance(name, str) or not name or "\\" in name or "\0" in name:
        raise BuildError(f"Unsafe archive path: {name!r}")
    if any(p in ("", ".", "..") or re.search(r'[:<>"|?*\x00-\x1f]', p)
           or p[-1:] in (".", " ")
           or re.fullmatch(r"(?i)(con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\..*)?", p)
           for p in name.split("/")):
        raise BuildError(f"Unsafe archive path: {name!r}")
    return name


def safe_path(root, relative):
    root = Path(root).absolute()
    result = root.joinpath(*safe_relative(relative).split("/"))
    for parent in (result, *result.parents):
        if parent.is_symlink() or (hasattr(os.path, "isjunction") and os.path.isjunction(parent)):
            raise BuildError(f"Symlink/junction in output path: {relative}")
        if parent == root:
            break
    if os.path.commonpath((root.resolve(), result.resolve())) != str(root.resolve()):
        raise BuildError(f"Output path escapes server directory: {relative}")
    return result


def digest(path, algorithm="sha512"):
    h = hashlib.new(algorithm)
    with Path(path).open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def verify(path, entry):
    hashes = entry.get("hashes", {})
    if not re.fullmatch(r"[0-9a-fA-F]{128}", str(hashes.get("sha512", ""))):
        raise BuildError(f"Missing/invalid sha512: {entry.get('path', path)}")
    for algorithm in ("sha512", "sha1"):
        if algorithm in hashes and digest(path, algorithm) != hashes[algorithm].lower():
            raise BuildError(f"Hash mismatch ({algorithm}): {entry.get('path', path)}")
    if "fileSize" in entry and Path(path).stat().st_size != entry["fileSize"]:
        raise BuildError(f"Size mismatch: {entry.get('path', path)}")


def atomic_bytes(dest, content):
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{dest.name}.", suffix=".tmp", dir=dest.parent)
    try:
        with os.fdopen(fd, "wb") as target:
            target.write(content)
        os.replace(temporary, dest)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def ensure_file(entry, dest, cache_dir=None, download=True):
    """Verify existing and cached files; publish downloads only after hashing."""
    dest = Path(dest)
    if dest.exists():
        verify(dest, entry)
        return
    if cache_dir:
        cached = Path(cache_dir) / Path(entry["path"]).name
        if cached.is_file():
            verify(cached, entry)
            atomic_bytes(dest, cached.read_bytes())
            return
    if not download:
        raise BuildError(f"Missing offline jar: {entry['path']}")
    urls = entry.get("downloads", [])
    if not urls:
        raise BuildError(f"No download URL: {entry['path']}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    failures = []
    for url in urls:
        if not isinstance(url, str) or not url.startswith("https://"):
            raise BuildError(f"Download must use HTTPS: {entry['path']}")
        fd, temporary = tempfile.mkstemp(prefix=f".{dest.name}.", suffix=".tmp", dir=dest.parent)
        try:
            with os.fdopen(fd, "wb") as target:
                with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as source:
                    shutil.copyfileobj(source, target)
            verify(temporary, entry)
            os.replace(temporary, dest)
            return
        except Exception as exc:
            failures.append(str(exc))
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
    raise BuildError(f"Download failed for {entry['path']}: {'; '.join(failures)}")


def is_client_file(relative):
    return relative in CLIENT_FILES or any(relative == p or relative.startswith(p + "/") for p in CLIENT_DIRS)


def archive_overrides(archive):
    layers = {"overrides": {}, "server-overrides": {}}
    seen = set()
    for info in archive.infolist():
        name = safe_relative(info.filename.rstrip("/") if info.is_dir() else info.filename)
        if name.casefold() in seen:
            raise BuildError(f"Duplicate archive entry: {name}")
        seen.add(name.casefold())
        if stat.S_ISLNK(info.external_attr >> 16):
            raise BuildError(f"Archive symlink rejected: {name}")
        if info.is_dir() or "/" not in name:
            continue
        layer, relative = name.split("/", 1)
        if layer not in layers or is_client_file(relative):
            continue
        if relative == STATE_FILE or relative.startswith(".expedition-"):
            raise BuildError(f"Reserved builder path: {relative}")
        layers[layer][relative] = info
    result = layers["overrides"]
    result.update(layers["server-overrides"])
    if len(result) != len({name.casefold() for name in result}):
        raise BuildError("Override paths differ only by letter case")
    return result


def embedded_is_server(data, name):
    import io
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as jar:
            metadata = json.loads(jar.read("fabric.mod.json"))
    except (zipfile.BadZipFile, KeyError, ValueError) as exc:
        raise BuildError(f"Invalid embedded Fabric mod {name}: {exc}") from exc
    return metadata.get("environment", "*") != "client"


def world_roots(out):
    names = {"world", "world_nether", "world_the_end"}
    properties = out / "server.properties"
    if properties.is_file():
        for line in properties.read_text(encoding="utf8", errors="replace").splitlines():
            if line.startswith("level-name="):
                name = safe_relative(line.partition("=")[2].strip())
                names.add(name.split("/")[0])
    if out.is_dir():
        names.update(p.name for p in out.iterdir() if p.is_dir()
                     and ((p / "level.dat").exists() or (p / "session.lock").exists()))
    return names


def install_launcher(out, deps, installer, previous, offline):
    dest = safe_path(out, "fabric-server-launch.jar")
    if dest.exists():
        expected = previous.get("launcher_sha512")
        if previous.get("dependencies") != deps or not expected or digest(dest) != expected:
            raise BuildError("Existing Fabric launcher version/checksum is unknown or different; use a new output directory")
        return expected
    if offline:
        raise BuildError("Offline build needs an existing verified Fabric launcher; use --no-download for configs only")
    url = f"https://meta.fabricmc.net/v2/versions/loader/{deps['minecraft']}/{deps['fabric-loader']}/{installer}/server/jar"
    fd, temporary = tempfile.mkstemp(prefix=".fabric-launcher.", suffix=".tmp", dir=out)
    try:
        with os.fdopen(fd, "wb") as target:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as source:
                shutil.copyfileobj(source, target)
        with zipfile.ZipFile(temporary) as jar:
            if jar.testzip() or "META-INF/MANIFEST.MF" not in jar.namelist():
                raise BuildError("Invalid Fabric server launcher")
        checksum = digest(temporary)
        os.replace(temporary, dest)
        return checksum
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def build(mrpack, out, ram="4G", no_download=False, cache_dir=None, offline=False, installer="1.1.2"):
    if not re.fullmatch(r"[1-9][0-9]*[MG]", ram.upper()):
        raise BuildError("--ram must be a positive whole number plus M or G, e.g. 4G")
    out = Path(out).absolute()
    state_path = safe_path(out, STATE_FILE)
    previous = json.loads(state_path.read_text(encoding="utf8")) if state_path.is_file() else {}
    with zipfile.ZipFile(mrpack) as archive:
        overrides = archive_overrides(archive)  # Validate before touching output.
        index = json.loads(archive.read("modrinth.index.json"))
        if index.get("formatVersion") != 1 or index.get("game") != "minecraft":
            raise BuildError("Only Minecraft mrpack formatVersion 1 is supported")
        deps = {k: index["dependencies"][k] for k in ("minecraft", "fabric-loader")}
        if not all(re.fullmatch(r"[A-Za-z0-9.+_-]+", v) for v in (*deps.values(), installer)):
            raise BuildError("Invalid Minecraft/Fabric version")
        expected, selected, names = {}, [], set()
        for entry in index["files"]:
            relative = safe_relative(entry["path"])
            if relative.casefold() in names:
                raise BuildError(f"Duplicate index path: {relative}")
            names.add(relative.casefold())
            environment = entry.get("env", {}).get("server", "required")
            if environment not in ("required", "optional", "unsupported"):
                raise BuildError(f"Invalid server environment: {relative}")
            if environment == "unsupported" or is_client_file(relative) or relative in overrides:
                continue
            selected.append(entry)
            if relative.startswith("mods/"):
                if not relative.endswith(".jar") or relative.count("/") != 1:
                    raise BuildError(f"Unsupported server mod path: {relative}")
                expected[relative.casefold()] = (relative, entry, None)
        for relative, info in list(overrides.items()):
            if relative.startswith("mods/"):
                if not relative.endswith(".jar") or relative.count("/") != 1:
                    raise BuildError(f"Unsupported embedded mod path: {relative}")
                data = archive.read(info)
                if not embedded_is_server(data, relative):
                    del overrides[relative]
                    continue
                entry = {"path": relative, "hashes": {"sha512": hashlib.sha512(data).hexdigest()}}
                expected[relative.casefold()] = (relative, entry, data)
        protected = {n.casefold() for n in world_roots(out)}
        for relative in [*overrides, *(e["path"] for e in selected)]:
            if relative.split("/")[0].casefold() in protected:
                raise BuildError(f"World file refused: {relative}; manage worlds separately")
            safe_path(out, relative)
        mods_dir = safe_path(out, "mods")
        if mods_dir.is_dir():
            for mod in mods_dir.iterdir():
                if mod.is_dir():
                    raise BuildError(f"Unexpected mods subdirectory: {mod.name}; use a clean output directory")
                if mod.suffix.lower() == ".jar":
                    key = ("mods/" + mod.name).casefold()
                    if key not in expected:
                        raise BuildError(f"Unexpected/stale mod: {mod.name}; use a new output directory")
                    verify(mod, expected[key][1])
        if previous and previous.get("dependencies") != deps:
            raise BuildError("Existing server Minecraft/Fabric versions differ; use a new output directory")
        out.mkdir(parents=True, exist_ok=True)
        mods_dir.mkdir(exist_ok=True)
        if not no_download:
            for entry in selected:
                dest = safe_path(out, entry["path"])
                if not entry["path"].startswith("mods/") and dest.exists():
                    print(f"Preserved existing {entry['path']}")
                    continue
                ensure_file(entry, dest, cache_dir, not offline)
        preserved = []
        for relative, info in overrides.items():
            dest = safe_path(out, relative)
            if relative.startswith("mods/"):
                if not dest.exists():
                    atomic_bytes(dest, expected[relative.casefold()][2])
            elif dest.exists():
                preserved.append(relative)
            else:
                atomic_bytes(dest, archive.read(info))
        for template in sorted((HERE / "template").iterdir()):
            dest = safe_path(out, template.name)
            if dest.exists():
                preserved.append(template.name)
                continue
            content = template.read_text(encoding="utf8").replace("@RAM@", ram.upper())
            if template.suffix == ".bat":
                content = content.replace("\n", "\r\n")
            atomic_bytes(dest, content.encode("utf8"))
            if template.suffix == ".sh":
                dest.chmod(dest.stat().st_mode | 0o111)
        launcher_hash = previous.get("launcher_sha512")
        if not no_download:
            launcher_hash = install_launcher(out, deps, installer, previous, offline)
        state = {"dependencies": deps, "launcher_sha512": launcher_hash, "configs_only": no_download,
                 "pack_name": index.get("name"), "pack_version": index.get("versionId"),
                 "mods": {relative: entry["hashes"]["sha512"] for relative, entry, _ in expected.values()}}
        atomic_bytes(state_path, (json.dumps(state, indent=2) + "\n").encode("utf8"))
        print(f"Prepared {len(expected)} server mod files in {out}")
        if preserved:
            print(f"Preserved {len(preserved)} existing configs/settings/start scripts.")
        print("CONFIGS ONLY: downloaded mods/launcher skipped; this server is not yet runnable." if no_download
              else "Build complete. Review eula.txt, then run start.bat or start.sh. Java 25+ required.")
        return state


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mrpack")
    parser.add_argument("out")
    parser.add_argument("--ram", default="4G")
    parser.add_argument("--no-download", action="store_true", help="configs/scripts + embedded mods only; NOT runnable")
    parser.add_argument("--offline", action="store_true", help="no network; requires cached mods and a verified launcher")
    parser.add_argument("--cache-dir", help="directory of cached mod jars; hashes checked before copying")
    parser.add_argument("--installer", default="1.1.2")
    args = parser.parse_args(argv)
    try:
        build(args.mrpack, args.out, args.ram, args.no_download, args.cache_dir, args.offline, args.installer)
    except (BuildError, OSError, ValueError, KeyError, zipfile.BadZipFile) as exc:
        parser.exit(1, f"Build refused: {exc}\n")


if __name__ == "__main__":
    main()
