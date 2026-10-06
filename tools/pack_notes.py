"""Which mods in a pack are built for another game version, or are alpha/beta builds. Asks Modrinth (needs network)
and writes tools/data/pack_notes.json, which gen_docs.py turns into the "known compromises" section of the docs.

python tools/pack_notes.py
"""
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UA = {"User-Agent": "FancyVanilla-Dev/2.0 (github.com/wtfangler/fava)"}
LOCKS = {"26.2": "lock.json", "26.3": "lock-26.3.json"}


def api(path, payload=None):
    request = urllib.request.Request("https://api.modrinth.com/v2" + path, headers=UA | ({"Content-Type": "application/json"} if payload else {}),
                                     data=json.dumps(payload).encode() if payload else None)
    return json.load(urllib.request.urlopen(request, timeout=120))


def notes(mc, lock_name):
    lock = json.loads((ROOT / "tools" / lock_name).read_text(encoding="utf8"))
    files = [f for f in lock["base"] + lock["added"] if f["path"].startswith("mods/")]
    versions = api("/version_files", {"hashes": [f["hashes"]["sha1"] for f in files], "algorithm": "sha1"})
    titles = {p["id"]: p["title"] for p in api("/projects?ids=" + urllib.parse.quote(json.dumps(sorted({v["project_id"] for v in versions.values()}))))}
    other, pre = [], []
    for f in files:
        v = versions.get(f["hashes"]["sha1"])
        if not v:
            continue
        title = titles.get(v["project_id"], f["path"])
        # Authors often tag a build for several game versions; the file name tells what it was actually built for
        tokens = set(re.findall(r"(?<![\d.])26\.\d+(?:\.\d+)?(?![\d])", f["path"].rsplit("/", 1)[-1] + " " + v["version_number"]))
        tokens = {t for t in tokens if t.count(".") >= 1}
        if tokens and mc not in tokens and not any(t.startswith(mc + ".") for t in tokens):
            other.append({"name": title, "built_for": sorted(tokens)[-1]})
        if v["version_type"] != "release":
            pre.append({"name": title, "channel": v["version_type"], "version": v["version_number"]})
    key = lambda e: e["name"].lower()
    return {"other_game_version": sorted(other, key=key), "prerelease": sorted(pre, key=key), "mod_files": len(files)}


if __name__ == "__main__":
    result = {mc: notes(mc, name) for mc, name in LOCKS.items()}
    out = ROOT / "tools" / "data" / "pack_notes.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=1) + "\n", encoding="utf8")
    for mc, n in result.items():
        print(mc, n["mod_files"], "mods |", len(n["other_game_version"]), "built for another game version |", len(n["prerelease"]), "alpha/beta")
