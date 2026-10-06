"""Launch a Fancy Vanilla pack on the real game client (any Fabric Minecraft version), join a world, then stop.

python tools/smoke_client.py 1.21.1 <releases/.../pack.mrpack> <world dir> --game <new dir> --cache <mod cache>

Builds the launch command from Mojang's version JSON and Fabric's profile JSON (hash-verified downloads, cached under
--libs), so it does not need a launcher install. Uses an empty asset index: sounds and non-English language files are
missing, everything else (mods, data packs, resource packs, rendering) is real. Never touches existing profiles/worlds.
"""
import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import time
import urllib.request
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UA = {"User-Agent": "FancyVanilla-Dev/2.0 (github.com/wtfangler/fava)"}
LOADER = "0.19.5"


def fetch(url, target, sha1=None):
    target = Path(target)
    if target.is_file() and (sha1 is None or hashlib.sha1(target.read_bytes()).hexdigest() == sha1):
        return target
    target.parent.mkdir(parents=True, exist_ok=True)
    data = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120).read()
    if sha1 and hashlib.sha1(data).hexdigest() != sha1:
        raise RuntimeError(f"Hash mismatch: {url}")
    target.write_bytes(data)
    return target


def allowed(rules):
    if not rules:
        return True
    ok = False
    for rule in rules:
        if "features" in rule:
            continue
        match = not rule.get("os") or rule["os"].get("name") == "windows"
        if match:
            ok = rule["action"] == "allow"
    return ok


def maven_path(name):
    group, artifact, version, *classifier = name.split(":")
    suffix = f"-{classifier[0]}" if classifier else ""
    return f"{group.replace('.', '/')}/{artifact}/{version}/{artifact}-{version}{suffix}.jar"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mc")
    parser.add_argument("pack", type=Path)
    parser.add_argument("world", type=Path)
    parser.add_argument("--game", type=Path, required=True)
    parser.add_argument("--cache", action="append", default=[])
    parser.add_argument("--libs", type=Path, required=True, help="download cache for game libraries")
    parser.add_argument("--java", type=Path, required=True)
    parser.add_argument("--seconds", type=int, default=150, help="run time after the process starts")
    args = parser.parse_args()
    game, libs = args.game.resolve(), args.libs.resolve()

    spec = importlib.util.spec_from_file_location("materialize", ROOT / "tools" / "materialize.py")
    materialize = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(materialize)
    index = materialize.materialize(args.pack, game, args.cache)
    if index["dependencies"]["minecraft"] != args.mc:
        raise SystemExit("Pack Minecraft version differs from target")

    manifest = json.load(urllib.request.urlopen(urllib.request.Request("https://piston-meta.mojang.com/mc/game/version_manifest_v2.json", headers=UA)))
    entry = next(v for v in manifest["versions"] if v["id"] == args.mc)
    vanilla = json.load(urllib.request.urlopen(urllib.request.Request(entry["url"], headers=UA)))
    fabric = json.load(urllib.request.urlopen(urllib.request.Request(
        f"https://meta.fabricmc.net/v2/versions/loader/{args.mc}/{LOADER}/profile/json", headers=UA)))

    classpath = []
    for lib in vanilla["libraries"]:
        if not allowed(lib.get("rules")):
            continue
        art = lib["downloads"]["artifact"]
        classpath.append(fetch(art["url"], libs / "lib" / art["path"], art["sha1"]))
    def ident(name):
        group, artifact, _version, *classifier = name.split(":")
        return (group, artifact, tuple(classifier))

    mojang_names = {ident(lib["name"]): i for i, lib in enumerate(vanilla["libraries"]) if allowed(lib.get("rules"))}
    for lib in fabric["libraries"]:
        rel = maven_path(lib["name"])
        path = fetch(lib["url"].rstrip("/") + "/" + rel, libs / "lib" / rel, lib.get("sha1"))
        if ident(lib["name"]) in mojang_names:  # Fabric's newer build replaces Mojang's (e.g. ASM): never both
            classpath = [c for c in classpath if Path(c) != Path(libs / "lib" / maven_path(vanilla["libraries"][mojang_names[ident(lib["name"])]]["name"]))]
        classpath.append(path)
    client = fetch(vanilla["downloads"]["client"]["url"], libs / "client" / f"{args.mc}.jar", vanilla["downloads"]["client"]["sha1"])
    classpath.append(client)

    assets = libs / "assets"
    (assets / "indexes").mkdir(parents=True, exist_ok=True)
    (assets / "indexes" / f"{vanilla['assetIndex']['id']}.json").write_text('{"objects":{}}', encoding="utf8")

    shutil.copytree(args.world, game / "saves" / "Test", ignore=shutil.ignore_patterns("session.lock"))
    options = game / "options.txt"
    values = dict(line.split(":", 1) for line in options.read_text(encoding="utf8").splitlines() if ":" in line)
    values.update(onboardAccessibility="false", tutorialStep="none", guiScale="2", fullscreen="false", pauseOnLostFocus="false")
    options.write_text("".join(f"{k}:{v}\n" for k, v in values.items()), encoding="utf8")

    repl = {"natives_directory": str(libs / "natives"), "launcher_name": "fv-smoke", "launcher_version": "1",
            "classpath": os.pathsep.join(map(str, classpath)), "auth_player_name": "Dev", "version_name": args.mc,
            "game_directory": str(game), "assets_root": str(assets), "assets_index_name": vanilla["assetIndex"]["id"],
            "auth_uuid": str(uuid.uuid4()), "auth_access_token": "0", "clientid": "0", "auth_xuid": "0", "version_type": "release",
            "user_type": "legacy", "user_properties": "{}"}

    def fill(text):
        for k, v in repl.items():
            text = text.replace("${" + k + "}", v)
        return text

    jvm, game_args = [], []
    for profile in (vanilla, fabric):
        for item in profile.get("arguments", {}).get("jvm", []):
            if isinstance(item, str):
                jvm.append(fill(item))
            elif allowed(item.get("rules")):
                jvm.extend(map(fill, [item["value"]] if isinstance(item["value"], str) else item["value"]))
    for profile in (vanilla, fabric):
        game_args += [fill(a) for a in profile.get("arguments", {}).get("game", []) if isinstance(a, str)]
    cmd = [str(args.java), "-Xmx3G", *jvm, fabric["mainClass"], *game_args, "--width", "1280", "--height", "720", "--quickPlaySingleplayer", "Test"]
    log = game / "client.out"
    with log.open("w", encoding="utf8") as out:
        process = subprocess.Popen(cmd, cwd=game, stdout=out, stderr=subprocess.STDOUT)
        start = time.time()
        joined = None
        while time.time() - start < args.seconds and process.poll() is None:
            time.sleep(3)
            text = log.read_text(encoding="utf8", errors="replace") if log.exists() else ""
            if joined is None and "Dev joined the game" in text:
                joined = time.time() - start
                time.sleep(25)  # let the world tick: data packs, mods and resource packs do their work
                break
        crashed = process.poll() is not None
        if not crashed:
            process.terminate()
            try:
                process.wait(timeout=30)
            except subprocess.TimeoutExpired:
                process.kill()
    reports = sorted((game / "crash-reports").glob("*.txt")) if (game / "crash-reports").exists() else []
    print(json.dumps({"mc": args.mc, "joined_after_s": joined, "exited_early": crashed, "crash_reports": [r.name for r in reports], "log": str(log)}))


if __name__ == "__main__":
    main()
