"""Compiles Fancy Journal against a Minecraft client jar and packs dist/fancy_journal-<ver>+mc<mc>.jar.

Usage: python build.py <mc> [--dev-dir <dir with <mc>/client.jar, <mc>/libs, tools/>]
                          [--fabric-api <Fabric API jar matching that Minecraft version>]
No Gradle/Loom: Minecraft 26.x is unobfuscated, so plain javac + Mixin annotations are enough
(mixins are applied by Fabric Loader at runtime; there is no refmap because names are not remapped)."""
import glob
import io
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile

ROOT = os.path.dirname(os.path.abspath(__file__))
VERSION = "1.2.0"
mc = sys.argv[1]
if mc not in {"26.2", "26.3"}:
    sys.exit("Supported Minecraft versions: 26.2, 26.3")
DEV = sys.argv[sys.argv.index("--dev-dir") + 1] if "--dev-dir" in sys.argv else os.path.join(ROOT, ".dev")
JAVAC = os.environ.get("JAVAC", "javac")
out = os.path.join(ROOT, "build", mc)
if os.path.commonpath([os.path.realpath(out), os.path.realpath(ROOT)]) != os.path.realpath(ROOT):
    sys.exit("Build output must stay inside journal-mod")
shutil.rmtree(out, ignore_errors=True)
os.makedirs(os.path.join(out, "classes"))

cp = [os.path.join(DEV, mc, "client.jar")] + sorted(glob.glob(os.path.join(DEV, mc, "libs", "*.jar"))) + sorted(glob.glob(os.path.join(DEV, "tools", "*.jar")))
fabric_api = sys.argv[sys.argv.index("--fabric-api") + 1] if "--fabric-api" in sys.argv else os.environ.get("JOURNAL_FABRIC_API")
if fabric_api:
    # Fabric API bundles its components as nested jars, which javac cannot read as a classpath by itself.
    api_dir = os.path.join(out, "api")
    os.makedirs(api_dir)
    with zipfile.ZipFile(fabric_api) as api:
        for name in sorted(api.namelist()):
            basename = name.rsplit("/", 1)[-1]
            if name.startswith("META-INF/jars/") and basename.startswith(("fabric-api-base-", "fabric-lifecycle-events-v1-", "fabric-key-mapping-api-v1-", "fabric-screen-api-v1-", "fabric-rendering-v1-")) and basename.endswith(".jar"):
                target = os.path.join(api_dir, basename)
                with open(target, "wb") as dependency:
                    dependency.write(api.read(name))
                cp.append(target)
sources = sorted(glob.glob(os.path.join(ROOT, "src", "**", "*.java"), recursive=True) + glob.glob(os.path.join(ROOT, f"src-{mc}", "**", "*.java"), recursive=True))
cmd = [JAVAC, "--release", "25", "-encoding", "UTF-8", "-Xlint:-options", "-proc:none", "-d", os.path.join(out, "classes"),
       "-cp", os.pathsep.join(cp)] + sources
print("javac", len(sources), "files for", mc)
res = subprocess.run(cmd, capture_output=True, text=True)
if res.returncode:
    errors = [l for l in res.stderr.splitlines() if "error:" in l]
    print(chr(10).join(errors[:15]) or res.stderr[:1500])
    sys.exit(f"{len(errors)} compile error(s) for {mc}")

jar = os.path.join(ROOT, "dist", f"fancy_journal-{VERSION}+mc{mc}.jar")
os.makedirs(os.path.dirname(jar), exist_ok=True)
# Each jar is compiled against one API (DisplayInfo differs between these versions).
minecraft_range = mc
buffer = io.BytesIO()


def write_entry(archive, name, data):
    info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.create_system = 3
    info.external_attr = 0o100644 << 16
    archive.writestr(info, data)


with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as z:
    for r, directories, fs in os.walk(os.path.join(out, "classes")):
        directories.sort()
        for f in sorted(fs):
            full = os.path.join(r, f)
            with open(full, "rb") as source:
                write_entry(z, os.path.relpath(full, os.path.join(out, "classes")).replace(os.sep, "/"), source.read())
    for r, directories, fs in os.walk(os.path.join(ROOT, "resources")):
        directories.sort()
        for f in sorted(fs):
            full = os.path.join(r, f)
            rel = os.path.relpath(full, os.path.join(ROOT, "resources")).replace(os.sep, "/")
            data = open(full, "rb").read()
            if rel == "fabric.mod.json":
                data = data.decode("utf8").replace("${version}", f"{VERSION}+mc{mc}").replace("${minecraft}", minecraft_range).encode("utf8")
            write_entry(z, rel, data)
fd, temporary = tempfile.mkstemp(prefix="." + os.path.basename(jar) + ".", suffix=".tmp", dir=os.path.dirname(jar))
try:
    with os.fdopen(fd, "wb") as target:
        target.write(buffer.getvalue())
        target.flush()
        os.fsync(target.fileno())
    os.replace(temporary, jar)
finally:
    if os.path.exists(temporary):
        os.unlink(temporary)
print("built", jar, os.path.getsize(jar), "bytes")
