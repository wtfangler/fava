"""Read resource-pack format bounds from hash-verified pinned ZIPs into a lock.

python tools/annotate_resources.py --mc 26.3 --cache <game/resourcepacks>
Use --download to fetch missing pinned files. Does not change versions/hashes.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("server_builder", ROOT / "server" / "build_server.py")
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


def bound(value, upper=False):
    default_minor = 2147483647 if upper else 0
    if isinstance(value, int):
        return [value, default_minor]
    if isinstance(value, list) and 1 <= len(value) <= 2 and all(type(x) is int for x in value):
        return [value[0], value[1] if len(value) == 2 else default_minor]
    raise ValueError(f"Ambiguous resource pack format: {value!r}")


def formats(metadata):
    if "min_format" in metadata:
        return {"min": bound(metadata["min_format"]), "max": bound(metadata["max_format"], True)}
    supported = metadata.get("supported_formats", metadata["pack_format"])
    if isinstance(supported, list):
        low, high = supported
    elif isinstance(supported, dict):
        low, high = supported["min_inclusive"], supported["max_inclusive"]
    else:
        low = high = supported
    return {"min": bound(low), "max": bound(high, True)}


def annotate(mc, caches, download=False):
    path = ROOT / "tools" / ("lock.json" if mc == "26.2" else "lock-26.3.json")
    lock = json.loads(path.read_text(encoding="utf8"))
    count = 0
    with tempfile.TemporaryDirectory(prefix="fv-resource-metadata-") as temporary:
        for item in lock["base"] + lock["added"]:
            if not item["path"].startswith("resourcepacks/"):
                continue
            source = None
            for cache in caches:
                candidate = Path(cache) / Path(item["path"]).name
                if candidate.is_file():
                    try:
                        builder.verify(candidate, item)
                    except builder.BuildError:
                        continue
                    source = candidate
                    break
            if source is None:
                source = Path(temporary) / Path(item["path"]).name
                builder.ensure_file(item, source, download=download)
            with zipfile.ZipFile(source) as pack:
                item["resourcePackFormat"] = formats(json.loads(pack.read("pack.mcmeta"))["pack"])
            count += 1
    builder.atomic_bytes(path, (json.dumps(lock, ensure_ascii=False, indent=1) + "\n").encode("utf8"))
    print(f"Annotated {count} pinned resource packs for {mc}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mc", choices=("26.2", "26.3"), default="26.2")
    parser.add_argument("--cache", action="append", default=[])
    parser.add_argument("--download", action="store_true")
    args = parser.parse_args()
    annotate(args.mc, args.cache, args.download)
