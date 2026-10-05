"""Resolves the Fancy Vanilla 2.0 file list (Fabric 26.2) against Modrinth and writes lock.json.

Base = Streamline Master 1.5.1 (the author's optimisation core), then vanilla-friendly visuals / QoL,
resource packs and shaders. Pinned by default: entries already in lock.json keep their exact file.
Use --update to re-pick the newest 26.2 build of everything."""
import json, os, sys, time, urllib.error, urllib.parse, urllib.request, zipfile

UA = {"User-Agent": "FancyVanilla-Dev/2.0 (github.com/wtfangler/fancy-vanilla)"}
ROOT = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(ROOT, ".."))  # project root (ROOT here is tools/)
GV = sys.argv[sys.argv.index("--mc") + 1] if "--mc" in sys.argv else "26.2"

# ---------------------------------------------------------------- what goes in (slug -> (client, server) override)
MODS = {
    # animations / models / entity visuals
    "entity-model-features": None, "entitytexturefeatures": None, "not-enough-animations": None,
    "3dskinlayers": None, "optigui": None,
    # atmosphere, particles, sound
    "better-clouds": None, "ambient-environment": None, "fallingleaves": None, "wakes": None, "visuality": None,
    "subtle-effects": None, "explosive-enhancement": None, "particle-rain": None, "particular-reforged": None,
    "particle-effects": None, "lambdynamiclights": None, "make_bubbles_pop": None, "glowing-torchflower": None,
    "bettergrassify": None, "ambientsounds": None, "sound-physics-remastered": None, "sound": None,
    # HUD / information (vanilla look, more info)
    "jade": None, "appleskin": None, "betterf3": None, "better-stats": None, "bookshelf-inspector": None,
    "detail-armor-bar-reconstructed": None, "durability-tooltip": None, "status-effect-bars": None,
    "better-mount-hud": None, "dynamiccrosshair": None, "shoulder-surfing-reloaded": None,
    # comfort
    "mouse-tweaks": None, "inventory-sorting": None, "searchables": None, "morechathistory": None, "chat-heads": None,
    "now-playing": None, "controlify": None, "controlling": None,
    "cherished-worlds": None, "capes": None, "no-chat-reports": None, "xaeros-minimap": None, "xaeros-world-map": None,
    "animaticarefabricated": None, "puzzle": None,
    # server-friendly, gameplay-neutral
    "clumps": None, "chunky": None, "spark": None, "fastback": ("required", "required"),
}
# resource packs and shaders (verified to carry a 26.2 tag); order = load order in options.txt (later wins)
PACKS = [
    "fast-better-grass", "os-colorful-grasses", "simple-grass-flowers", "bushier-bushes", "better-leaves",
    "fresh-flower-pots", "fancy-crops", "rays-3d-ladders", "rays-3d-rails", "better-lanterns", "better-flame-particles",
    "low-on-fire", "eggs-n-eyes", "blocky-armor-stands", "visual-armor-trims", "even-better-enchants",
    "enchanted-books-re-covered", "theones-eating-animation-pack", "clearer-slot-highlight",
    "fresh-animations", "als-creepers-revamped", "als-enderman-revamped-x-fresh-animations",
    "als-scorpions-crabs-x-fresh-animations", "als-skeletons-revamped-x-fresh-animations",
]
SHADERS = ["complementary-reimagined", "miniature-shader"]
UPGRADE = ["fabric-api", "fabric-language-kotlin"]  # Streamline files that must be newer for the added mods


def api(path, data=None, **p):
    u = "https://api.modrinth.com/v2" + path + ("?" + urllib.parse.urlencode(p) if p else "")
    body = json.dumps(data).encode() if data is not None else None
    h = dict(UA)
    if body:
        h["Content-Type"] = "application/json"
    for attempt in range(8):
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request(u, data=body, headers=h)))
        except urllib.error.HTTPError as e:
            if e.code != 429 or attempt == 7:
                raise
            time.sleep(5 * (attempt + 1))





# mods dropped on purpose: Controlify prevents "Remove Reloading Screen" from working in every client log
DROP_SLUGS = {"rrls"}
PINNED = {}


def pick(pid, loader=True):
    old = PINNED.get(pid)
    if old:
        # A transient API failure must not silently upgrade a pinned dependency.
        return api(f"/version_file/{old['hashes']['sha1']}", algorithm="sha1")
    kw = {"game_versions": json.dumps([GV])}
    if loader:
        kw["loaders"] = json.dumps(["fabric"])
    vs = api(f"/project/{pid}/version", **kw)
    for t in ("release", "beta", "alpha"):
        c = [v for v in vs if v["version_type"] == t]
        if c:
            return sorted(c, key=lambda v: v["date_published"])[-1]


def pick_fallback(pid):
    vs = api(f"/project/{pid}/version", game_versions=json.dumps(["26.2"]))
    for t in ("release", "beta", "alpha"):
        c = [v for v in vs if v["version_type"] == t]
        if c:
            return sorted(c, key=lambda v: v["date_published"])[-1]


def entry(proj, v, folder, env, dep):
    f = next((x for x in v["files"] if x["primary"]), v["files"][0])
    result = {"path": f"{folder}/{f['filename']}", "slug": proj["slug"], "title": proj["title"], "version": v["version_number"],
            "channel": v["version_type"], "hashes": {"sha1": f["hashes"]["sha1"], "sha512": f["hashes"]["sha512"]},
            "downloads": [f["url"]], "fileSize": f["size"], "env": {"client": env[0], "server": env[1]}, "dep": dep}
    old = PINNED.get(proj["id"])
    if old and old["hashes"] == result["hashes"] and "resourcePackFormat" in old:
        result["resourcePackFormat"] = old["resourcePackFormat"]
    return result


def main():
    global PINNED
    lock_file = os.path.join(ROOT, "lock.json" if GV == "26.2" else f"lock-{GV}.json")
    if "--update" not in sys.argv and os.path.exists(lock_file):
        PINNED = {a["slug"]: a for a in json.load(open(lock_file, encoding="utf8"))["added"]}
    base = json.loads(zipfile.ZipFile(os.path.join(ROOT_DIR, "inputs", "Streamline Master 1.5.1.mrpack")).read("modrinth.index.json"))
    byhash = api("/version_files", {"hashes": [f["hashes"]["sha1"] for f in base["files"]], "algorithm": "sha1"})
    have, base_files, base_items = {}, [f for f in base["files"] if "rrls-" not in f["path"].lower()], []
    for f in base["files"]:
        v = byhash.get(f["hashes"]["sha1"])
        if v:
            have[v["project_id"]] = f["path"]
            base_items.append((v["project_id"], f))
    for slug in UPGRADE:
        pid = api(f"/project/{slug}")["id"]
        old = have.pop(pid, None)
        base_files = [f for f in base_files if f["path"] != old]
        MODS[slug] = ("required", "required")
    if GV != "26.2":
        # Streamline's files are 26.2 builds: re-resolve every one of them for this Minecraft version
        base_files, have = [], {}
    added, log, done = [], [], set(have)
    dropped, fallback = [], []
    pins = {}

    all_pins = {a["slug"]: a for a in (json.load(open(lock_file, encoding="utf8"))["added"] if "--update" not in sys.argv and os.path.exists(lock_file) else [])}

    def run(slug, env, folder, loader, dep=False):
        proj = api(f"/project/{slug}")
        if proj["id"] in done:
            return
        pins.clear()
        if proj["slug"] in all_pins:
            pins[proj["id"]] = all_pins[proj["slug"]]
        PINNED.clear(); PINNED.update(pins)
        v = pick(proj["id"], loader)
        if not v and GV != "26.2" and folder != "mods":
            # resource packs/shaders rarely break: fall back to the newest build tagged for 26.2
            v = pick_fallback(proj["id"])
            if v:
                fallback.append(proj["slug"])
        if not v:
            (dropped if GV != "26.2" else log).append(f"NO {GV} build: {proj['slug']}")
            return
        e = env
        if e is None:
            e = (proj["client_side"], proj["server_side"]) if folder == "mods" else ("required", "unsupported")
        if folder == "shaderpacks":
            e = ("optional", "unsupported")
        elif e[0] == "optional" or (dep and e[0] == "unsupported"):
            e = ("required", e[1])  # never leave the client side to a launcher prompt
        added.append(entry(proj, v, folder, e, dep))
        done.add(proj["id"])
        for d in v["dependencies"]:
            if d["dependency_type"] == "required" and d.get("project_id") and d["project_id"] not in done:
                run(d["project_id"], None, "mods", True, True)

    for slug in UPGRADE:  # first, so they are not first reached as optional dependencies
        run(slug, MODS[slug], "mods", True)
    if GV != "26.2":
        base_packs = []
        for pid, f in base_items:
            slug = api(f"/project/{pid}")["slug"]
            if slug in DROP_SLUGS:
                continue
            if f["path"].startswith("mods/"):
                run(slug, (f["env"]["client"], f["env"]["server"]), "mods", True)
            elif f["path"].startswith("resourcepacks/"):
                base_packs.append(slug)
                run(slug, (f["env"]["client"], f["env"]["server"]), "resourcepacks", False)
    for slug, env in MODS.items():
        if slug in DROP_SLUGS:
            continue
        run(slug, env, "mods", True)
    for slug in PACKS:
        run(slug, None, "resourcepacks", False)
    for slug in SHADERS:
        run(slug, None, "shaderpacks", False)
    out = {"mc": GV, "base": base_files, "added": added, "log": log, "packs": PACKS, "dropped": dropped, "fallback": fallback}
    if GV != "26.2":
        out["packs"] = base_packs + PACKS
    json.dump(out, open(lock_file, "w", encoding="utf8"), indent=1, ensure_ascii=False)
    for a in added:
        print(f'{"dep " if a["dep"] else "    "}{a["slug"]:44}{a["version"][:30]:31}{a["channel"]:8} {a["env"]["client"]:11} {a["env"]["server"]}')
    print("\n".join(log) or "no unresolved entries")


if __name__ == "__main__":
    if GV not in ("26.2", "26.3"):
        raise ValueError(f"Unsupported Minecraft version: {GV}")
    main()
