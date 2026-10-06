"""Builds releases/<mc>/Fancy Vanilla <version> for <mc>.mrpack (reproducible archive) from lock.json, inputs/ and src/."""
import hashlib
import io
import json
import re
import sys
import argparse
from pathlib import Path, PurePosixPath
import zipfile

ROOT = Path(__file__).resolve().parents[1]
STREAMLINE = {"26.2": ROOT / "inputs" / "Streamline Master 1.5.1.mrpack",
              "26.3": ROOT / "inputs" / "Streamline Master 1.6.2-beta-mc26.3.mrpack"}
MC_VERSIONS = ("26.2", "26.3")
# Fancy Vanilla release number, the same for every game version; the Modrinth version number is "<VERSION>+<game version>"
# and the channel (alpha/beta/release) tells how stable it is (docs/VERSIONING.md).
VERSION = "0.1.0"


def version_id(mc):
    return f"{VERSION}+{mc}"
NAME = "Fancy Vanilla"
PACK = "FancyVanilla.zip"
TEMPERED_JAR = "TEMPERED2.20.0mc26.2.jar"
JOURNAL_VERSION = "1.2.0"
DATE = (2026, 1, 1, 0, 0, 0)


def safe_path(name):
    path = PurePosixPath(name)
    if path.is_absolute() or ".." in path.parts or "\\" in name or ":" in name:
        raise ValueError(f"Unsafe archive path: {name}")
    return path


def archive(entries):
    data = io.BytesIO()
    with zipfile.ZipFile(data, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as output:
        for name, content in sorted(entries.items()):
            safe_path(name)
            info = zipfile.ZipInfo(name, DATE)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            output.writestr(info, content)
    return data.getvalue()


def tree(path):
    return {f.relative_to(path).as_posix(): f.read_bytes() for f in sorted(path.rglob("*")) if f.is_file()}


def encode(value):
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf8")


def options_for_new_mc(raw, ordered_packs, incompatible=()):
    """26.3: Streamline's pack file names are stale, so rebuild the list. Packs built for older pack formats
    must be listed in incompatibleResourcePacks or the game silently drops them from the selection."""
    entries = {}
    for line in raw.decode("utf8").splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            entries[key] = value
    old = json.loads(entries["resourcePacks"])
    builtins = [p for p in old if not p.startswith("file/") and p != "vanilla"]
    files = list(dict.fromkeys(["file/" + n for n in ordered_packs] + ["file/" + PACK]))
    entries["resourcePacks"] = json.dumps(["vanilla"] + builtins + files, ensure_ascii=False, separators=(",", ":"))
    entries["incompatibleResourcePacks"] = json.dumps([p for p in files if p in incompatible], ensure_ascii=False, separators=(",", ":"))
    entries["renderDistance"] = "12"
    entries["simulationDistance"] = "8"
    entries["key_chloride.zoom"] = "key.keyboard.unknown"
    entries.pop("lastServer", None)
    nl = chr(10)
    return (nl.join(k + ":" + v for k, v in entries.items()) + nl).encode("utf8")


def options(raw, new_packs):
    """Streamline's options.txt + our packs: new ones after the grass pack, Fancy Vanilla last (highest priority)."""
    entries = {}
    for line in raw.decode("utf8").splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            entries[key] = value
    packs = json.loads(entries["resourcePacks"])
    anchor = packs.index("file/Fast Better Grass.zip") + 1 if "file/Fast Better Grass.zip" in packs else 1
    for name in new_packs:
        if name not in packs:
            packs.insert(anchor, name)
            anchor += 1
    # DARK changes inventory sprites; the specific slot highlight must win.
    clearer = next((p for p in packs if "clearer" in p.lower() and "highlight" in p.lower()), None)
    if clearer:
        packs.remove(clearer)
        packs.append(clearer)
    packs.append("file/" + PACK)
    packs = list(dict.fromkeys(packs))
    entries["resourcePacks"] = json.dumps(packs, ensure_ascii=False, separators=(",", ":"))
    entries["renderDistance"] = "12"       # Streamline ships 8; Fancy Vanilla is about the view
    entries["simulationDistance"] = "8"
    entries["key_chloride.zoom"] = "key.keyboard.unknown"
    entries.pop("lastServer", None)
    return ("\n".join(k + ":" + v for k, v in entries.items()) + "\n").encode("utf8")


def build(MC="26.2"):
    if MC not in MC_VERSIONS:
        raise ValueError(f"Unsupported Minecraft version: {MC}")
    lock = json.loads((ROOT / "tools" / ("lock.json" if MC == "26.2" else f"lock-{MC}.json")).read_text(encoding="utf8"))
    if lock.get("log"):
        raise ValueError(f"Unresolved lock: {lock['log']}")
    files, seen = [], set()
    for item in lock["base"] + lock["added"]:
        if item["path"].startswith("resourcepacks/") and "resourcePackFormat" not in item:
            raise ValueError(f"Annotate pinned resource metadata first: python tools/annotate_resources.py --mc {MC} --download")
        entry = {k: item[k] for k in ("path", "hashes", "env", "downloads", "fileSize")}
        safe_path(entry["path"])
        if entry["path"].casefold() in seen:
            raise ValueError(f"Duplicate file: {entry['path']}")
        seen.add(entry["path"].casefold())
        files.append(entry)
    files.sort(key=lambda f: f["path"].lower())

    payload = {}
    with zipfile.ZipFile(STREAMLINE[MC]) as src:
        for name in src.namelist():
            if name.endswith("/") or not name.startswith("overrides/"):
                continue
            rel = name[len("overrides/"):]
            safe_path(rel)
            if rel == "options.txt" or (rel.startswith("config/") and not any(w in rel.lower() for w in ("backup", ".bak"))):
                payload[name] = src.read(name)
    # Version-specific overlays come after shared defaults.
    for folder in ("config", f"config-{MC}"):
        for name, data in tree(ROOT / "src" / folder).items():
            safe_path(name)
            if folder == "config" and MC != "26.2" and "overrides/config/" + name in payload:
                continue  # the base's own tuned config wins over our shared overlay
            payload["overrides/config/" + name] = data
    tempered_name = TEMPERED_JAR.replace("mc26.2", f"mc{MC}")
    payload["overrides/mods/" + tempered_name] = (ROOT / "build" / "mods" / tempered_name).read_bytes()
    journal = ROOT / "journal-mod" / "dist" / f"fancy_journal-{JOURNAL_VERSION}+mc{MC}.jar"
    if not journal.exists():
        raise ValueError(f"Build the journal mod first: python journal-mod/build.py {MC}")
    payload["overrides/mods/" + journal.name] = journal.read_bytes()
    payload["overrides/resourcepacks/" + PACK] = archive(tree(ROOT / "src" / "resourcepack"))

    credits = "overrides/config/isxander-main-menu-credits.json"
    if credits in payload:
        cfg = json.loads(payload[credits])
        for menu in ("main_menu", "pause_menu"):
            for entry in cfg.get(menu, {}).get("bottom_right", [])[:1]:
                entry["text"] = f"{NAME} {VERSION}"
                entry.pop("click_event", None)
                entry.pop("hover_event", None)
        payload[credits] = encode(cfg)

    new_packs = [("file/" + Path(f["path"]).name) for slug in lock["packs"] for f in lock["added"]
                 if f["slug"] == slug and f["path"].startswith("resourcepacks/")]
    if MC == "26.2":
        payload["overrides/options.txt"] = options(payload["overrides/options.txt"], new_packs)
    else:
        by_slug = {f["slug"]: Path(f["path"]).name for f in lock["added"] if f["path"].startswith("resourcepacks/")}
        incompatible = {"file/" + by_slug[x] for x in lock.get("fallback", []) if x in by_slug}
        payload["overrides/options.txt"] = options_for_new_mc(payload["overrides/options.txt"], [by_slug[x] for x in lock["packs"] if x in by_slug], incompatible)
        # These client mods have no 26.3 build. Do not ship their stale defaults.
        for name in ("chloride-client.toml", "particle_core_config.toml", "particle-rain.json", "particle-rain.json5", "wakes.json"):
            payload.pop("overrides/config/" + name, None)
    # Compatibility is determined from the downloaded pack's metadata, not
    # from which Minecraft versions its Modrinth page happens to list.
    expected_format = (88, 0) if MC == "26.2" else (97, 1)
    incompatible = []
    for item in lock["base"] + lock["added"]:
        formats = item.get("resourcePackFormat")
        if formats and not tuple(formats["min"]) <= expected_format <= tuple(formats["max"]):
            incompatible.append("file/" + Path(item["path"]).name)
    values = dict(line.split(":", 1) for line in payload["overrides/options.txt"].decode("utf8").splitlines() if ":" in line)
    selected = json.loads(values["resourcePacks"])
    values["incompatibleResourcePacks"] = json.dumps([name for name in incompatible if name in selected], ensure_ascii=False, separators=(",", ":"))
    payload["overrides/options.txt"] = ("".join(f"{k}:{v}\n" for k, v in values.items())).encode("utf8")
    payload["modrinth.index.json"] = encode({
        "formatVersion": 1, "game": "minecraft", "versionId": version_id(MC), "name": NAME,
        "summary": "Vanilla z oprawą: szybka, piękna, z progresją Tempered. Nic nowego w świecie, tylko lepiej.",
        "files": files, "dependencies": {"minecraft": MC, "fabric-loader": "0.19.5"}})
    out = ROOT / "releases" / MC / f"{NAME} {VERSION} for {MC}.mrpack"
    out.parent.mkdir(exist_ok=True)
    tmp = out.with_suffix(".mrpack.tmp")
    tmp.write_bytes(archive(payload))
    tmp.replace(out)
    out.with_suffix(".mrpack.sha512").write_text(hashlib.sha512(out.read_bytes()).hexdigest() + "  " + out.name + "\n", encoding="ascii")
    print(f"Built {out.name}: {len(files)} downloaded files + 3 bundled (TEMPERED, Fancy Journal, resource pack); {out.stat().st_size} bytes")
    return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mc", choices=MC_VERSIONS, default="26.2")
    build(parser.parse_args().mc)
