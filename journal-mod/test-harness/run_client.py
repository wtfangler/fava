"""Run a complete pack in a NEW game directory; hash-verify all files.
Requires FJ_SCRATCH(dev jars) and JAVAC. Never deletes profiles/worlds or kills other Java processes.
"""
import argparse, importlib.util, json, os, shutil, subprocess, tempfile, uuid, zipfile
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mc", choices=("26.2","26.3"))
    parser.add_argument("world", type=Path)
    parser.add_argument("--full", type=Path, required=True)
    parser.add_argument("--game", type=Path, required=True)
    parser.add_argument("--cache", action="append", default=[])
    parser.add_argument("--timeout", type=int, default=420)
    parser.add_argument("--rd", type=int)
    args = parser.parse_args()
    scratch = Path(os.environ["FJ_SCRATCH"])
    dev, game = scratch/"dev", args.game.resolve()
    spec = importlib.util.spec_from_file_location("materialize", ROOT/"tools"/"materialize.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    index = module.materialize(args.full, game, args.cache)
    if index["dependencies"]["minecraft"] != args.mc:
        raise ValueError("Pack Minecraft version differs from target")
    with tempfile.TemporaryDirectory(prefix="fj-harness-build-") as tmp:
        classes = Path(tmp)/"classes"
        classes.mkdir()
        cp = [dev/args.mc/"client.jar", *sorted((dev/args.mc/"libs").glob("*.jar")), *sorted((dev/"tools").glob("*.jar"))]
        src = sorted((HERE/"src").rglob("*.java"))
        subprocess.run([os.environ["JAVAC"],"--release","25","-proc:none","-d",str(classes),"-cp",os.pathsep.join(map(str,cp)),*map(str,src)],check=True)
        with zipfile.ZipFile(game/"mods"/"fj_harness.jar","w",zipfile.ZIP_DEFLATED) as output:
            for folder in (classes,HERE/"resources"):
                for file in sorted(folder.rglob("*")):
                    if file.is_file():
                        output.write(file,file.relative_to(folder).as_posix())
    shutil.copytree(args.world,game/"saves"/"Test",ignore=shutil.ignore_patterns("session.lock"))
    fixture=game/"saves"/"Test"/"datapacks"/"fv_harness"
    advancements=fixture/"data"/"fvtest"/"advancement"
    advancements.mkdir(parents=True)
    data_format=[107,1] if args.mc=="26.2" else [121,0]
    (fixture/"pack.mcmeta").write_text(json.dumps({"pack":{"description":"Test-only hidden advancement fixture","min_format":data_format,"max_format":data_format}}),encoding="utf8")
    for name,parent,hidden in (("root",None,False),("hidden","fvtest:root",True),("visible_child","fvtest:hidden",False)):
        value={"criteria":{"manual":{"trigger":"minecraft:impossible"}},"display":{"icon":{"id":"minecraft:book"},"title":"Test "+name,"description":"Hidden semantics regression","hidden":hidden,"show_toast":False,"announce_to_chat":False}}
        if parent:value["parent"]=parent
        else:value["display"]["background"]="minecraft:gui/advancements/backgrounds/stone"
        (advancements/(name+".json")).write_text(json.dumps(value),encoding="utf8")
    options=game/"options.txt"
    values=dict(line.split(":",1) for line in options.read_text(encoding="utf8").splitlines() if ":" in line)
    values.update(onboardAccessibility="false",tutorialStep="none",guiScale="2",fullscreen="false",pauseOnLostFocus="false",lang="pl_pl")
    if args.rd: values["renderDistance"]=str(args.rd)
    options.write_text("".join(f"{k}:{v}\n" for k,v in values.items()),encoding="utf8")
    meta=Path.home()/"AppData"/"Roaming"/"ModrinthApp"/"meta"
    version=f"{args.mc}-0.19.5"
    vj=json.loads((meta/"versions"/version/f"{version}.json").read_text(encoding="utf8"))
    def allowed(rules):
        if not rules: return True
        ok=False
        for rule in rules:
            match=not rule.get("os") or rule["os"].get("name")=="windows"
            if "features" in rule: match=False
            if match: ok=rule["action"]=="allow"
        return ok
    libraries=[]
    for lib in vj["libraries"]:
        if not allowed(lib.get("rules")): continue
        group,artifact,number,*classifier=lib["name"].split(":")
        filename=f"{artifact}-{number}"+(f"-{classifier[0]}" if classifier else "")+".jar"
        file=meta/"libraries"/Path(*group.split("."))/artifact/number/filename
        if not file.is_file(): raise FileNotFoundError(file)
        libraries.append(file)
    libraries.append(meta/"versions"/version/f"{version}.jar")
    replacements={"natives_directory":str(meta/"natives"/version),"launcher_name":"fj-test","launcher_version":"2",
                  "classpath":os.pathsep.join(map(str,libraries)),"auth_player_name":"Dev","version_name":version,
                  "game_directory":str(game),"assets_root":str(meta/"assets"),"assets_index_name":vj["assetIndex"]["id"],
                  "auth_uuid":str(uuid.uuid4()),"auth_access_token":"0","clientid":"0","auth_xuid":"0","version_type":"release"}
    def fill(text):
        for k,v in replacements.items(): text=text.replace("${"+k+"}",v)
        return text
    jvm=[]
    for arg in vj["arguments"]["jvm"]:
        if isinstance(arg,str): jvm.append(fill(arg))
        elif allowed(arg.get("rules")):
            values=[arg["value"]] if isinstance(arg["value"],str) else arg["value"]
            jvm.extend(map(fill,values))
    game_args=[fill(a) for a in vj["arguments"]["game"] if isinstance(a,str)]
    java=next((meta/"java_versions").glob("zulu25*/bin/java.exe"))
    cmd=[str(java),"-Xmx4G",*([f"-Dfj.scenario={os.environ['FJ_SCENARIO']}"] if os.environ.get("FJ_SCENARIO") else []),*jvm,vj["mainClass"],*game_args,"--width","1280","--height","720","--quickPlaySingleplayer","Test"]
    print(f"Launching full {args.mc} in {game}",flush=True)
    log_path=game/"client.out"
    with log_path.open("w",encoding="utf8") as log:
        process=subprocess.Popen(cmd,cwd=game,stdout=log,stderr=subprocess.STDOUT)
        try: result=process.wait(timeout=args.timeout)
        except subprocess.TimeoutExpired:
            process.terminate()
            try: process.wait(timeout=15)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
            raise RuntimeError(f"Client timeout; terminated only PID {process.pid}")
    output=log_path.read_text(encoding="utf8",errors="replace")
    if result or "[FJ-HARNESS] finished" not in output or "[FJ-HARNESS] ERROR" in output:
        raise RuntimeError(f"Client verification failed (exit {result}); see {log_path}")
    print("PASS: "+str(log_path),flush=True)

if __name__=="__main__": main()
