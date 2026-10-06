"""Maps every file of the old Fancy Vanilla packs (+ Tempered 26.2) to Modrinth projects and checks 26.2 availability."""
import json, os, urllib.request, urllib.parse, zipfile
UA = {"User-Agent": "FancyVanilla-Dev/2.0 (github.com/wtfangler/fava)"}
HERE = os.path.dirname(os.path.abspath(__file__)); PROJECT = os.path.abspath(os.path.join(HERE, ".."))
PACKS = {"fv1204": os.path.join(PROJECT, "releases", "1.20.4", "Fancy Vanilla 1.0.1.Es for 1.20.4.mrpack"),
         "fv1218": os.path.join(PROJECT, "releases", "1.21.8", "Fancy Vanilla 1.0.2 for 1.21.8.mrpack"),
         "tempered": os.path.join(PROJECT, "inputs", "Tempered 1.0.0.mrpack"),
         "streamline": os.path.join(PROJECT, "inputs", "Streamline Master 1.5.2.mrpack")}

def api(path, data=None, **p):
    u = "https://api.modrinth.com/v2" + path + ("?" + urllib.parse.urlencode(p) if p else "")
    body = json.dumps(data).encode() if data is not None else None
    h = dict(UA); h.update({"Content-Type": "application/json"} if body else {})
    return json.load(urllib.request.urlopen(urllib.request.Request(u, data=body, headers=h)))

projects = {}; membership = {}
for name, path in PACKS.items():
    idx = json.loads(zipfile.ZipFile(path).read("modrinth.index.json"))
    hashes = [f["hashes"]["sha1"] for f in idx["files"]]
    found = api("/version_files", {"hashes": hashes, "algorithm": "sha1"})
    for f in idx["files"]:
        v = found.get(f["hashes"]["sha1"])
        key = v["project_id"] if v else "unknown:" + f["path"]
        membership.setdefault(key, {})[name] = f["path"]
        projects.setdefault(key, {"path": f["path"]})
ids = [k for k in projects if not k.startswith("unknown:")]
for i in range(0, len(ids), 80):
    for p in api("/projects", ids=json.dumps(ids[i:i + 80])):
        projects[p["id"]].update(slug=p["slug"], title=p["title"], type=p["project_type"], client=p["client_side"], server=p["server_side"])
out = []
for k, info in projects.items():
    m = membership[k]
    row = {"id": k, "in": sorted(m), **{x: info.get(x) for x in ("slug", "title", "type", "client", "server", "path")}}
    if not k.startswith("unknown:"):
        t = info["type"]
        kw = dict(game_versions=json.dumps(["26.2"]))
        if t == "mod": kw["loaders"] = json.dumps(["fabric"])
        try:
            vs = api(f"/project/{k}/version", **kw)
        except Exception as e:
            vs = []
        row["v262"] = vs[0]["version_number"] if vs else None
        row["channel"] = vs[0]["version_type"] if vs else None
    out.append(row)
os.makedirs(os.path.join(HERE, "data"), exist_ok=True)
json.dump(out, open(os.path.join(HERE, "data", "inventory.json"), "w", encoding="utf8"), indent=1, ensure_ascii=False)
print(len(out), "projects")
