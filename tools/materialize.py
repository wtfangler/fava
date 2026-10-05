"""Materialize every client file from an mrpack into a NEW, isolated directory.

Downloads and cached files are checked against both recorded hashes and size.
Used by the integration harness; never installs into an existing game profile.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import importlib.util
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("server_builder", ROOT / "server" / "build_server.py")
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


def materialize(pack, out, caches=(), download=True):
    out = Path(out).resolve()
    if out.exists() and any(out.iterdir()):
        raise ValueError(f"Use a new empty client directory: {out}")
    with zipfile.ZipFile(pack) as archive:
        index = json.loads(archive.read("modrinth.index.json"))
        selected = []
        seen = set()
        for item in index["files"]:
            name = builder.safe_relative(item["path"])
            if name.casefold() in seen:
                raise ValueError(f"Duplicate client path: {name}")
            seen.add(name.casefold())
            if item.get("env", {}).get("client") != "unsupported":
                selected.append(item)
        overrides = {}
        for layer in ("overrides", "client-overrides"):
            for info in archive.infolist():
                if info.is_dir() or not info.filename.startswith(layer + "/"):
                    continue
                name = builder.safe_relative(info.filename[len(layer) + 1:])
                if name.startswith(("saves/", "screenshots/", "logs/")):
                    raise ValueError(f"World/runtime file refused: {name}")
                overrides[name] = archive.read(info)
        for name in [*(f["path"] for f in selected), *overrides]:
            builder.safe_path(out, name)
        out.mkdir(parents=True, exist_ok=True)
        destinations = {f["path"]: builder.safe_path(out, f["path"]) for f in selected}

        def install(item):
            dest = destinations[item["path"]]
            for cache in caches:
                source = Path(cache) / Path(item["path"]).name
                if source.is_file():
                    try:
                        builder.verify(source, item)
                    except builder.BuildError:
                        # The same filename may be a different Minecraft build.
                        # Never install it; try another cache or the pinned URL.
                        continue
                    builder.atomic_bytes(dest, source.read_bytes())
                    return
            builder.ensure_file(item, dest, download=download)

        with ThreadPoolExecutor(max_workers=6) as pool:
            list(pool.map(install, selected))
        for name, data in overrides.items():
            builder.atomic_bytes(builder.safe_path(out, name), data)
    counts = {kind: sum(f["path"].startswith(kind + "/") for f in selected) for kind in ("mods", "resourcepacks", "shaderpacks")}
    print(json.dumps({"mc": index["dependencies"]["minecraft"], "verified_downloads": counts,
                      "overrides": len(overrides), "output": str(out)}, ensure_ascii=False))
    return index


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pack", type=Path)
    parser.add_argument("out", type=Path)
    parser.add_argument("--cache", action="append", default=[])
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args()
    materialize(args.pack, args.out, args.cache, not args.offline)
