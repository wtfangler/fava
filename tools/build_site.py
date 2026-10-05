"""Builds the Fancy Vanilla website from its source (site/) plus real project data.

  python tools/build_site.py            -> build/site/ (folder) and build/fancy-vanilla-site.zip (for deployment)

Everything that can go stale is computed here, not typed into the HTML:
  * the version table, sizes, hashes and download links come from releases/ (+ dates/channels in site/versions-meta.json),
  * counts (mods, packs, shaders, quests) come from the newest packs and their bundled TEMPERED jar,
  * age names come from TEMPERED's language files, the mod lists from tools/lock.json,
  * images are derived from brand/ (the author's artwork) and gallery/ (real in-game screenshots).
"""
import hashlib
import urllib.parse
import html
import importlib.util
import io
import json
import re
import shutil
import sys
import zipfile
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
OUT = ROOT / "build" / "site"
MODRINTH = "https://modrinth.com/modpack/fava"
CURRENT = ("26.2", "26.3")
# Fixed by the TEMPERED mod: quests needed to advance / quests in the age (see docs/modrinth_description.md)
THRESHOLDS = [(6, 9), (9, 15), (8, 13), (8, 13), (9, 14), (8, 13), (8, 12)]

CORE = ("Sodium, Iris, Lithium, C2ME, VMP, FerriteCore, ModernFix, ScalableLux, Krypton, ImmediatelyFast, Entity Culling, "
        "More Culling, BadOptimizations, Dynamic FPS, Continuity, Zoomify, Smooth Scroll, FastQuit i inne")
CORE_EN = CORE.replace(" i inne", " and more")


def esc(text):
    return html.escape(str(text), quote=True)


def bi(pl, en):
    return f'<span lang="pl">{pl}</span><span lang="en">{en}</span>'


def human_size(n):
    return f"{n / 1024:.0f} KB" if n < 1024 * 1024 else f"{n / 1024 / 1024:.1f} MB"


# ------------------------------------------------------------------ releases
def read_release(path, meta):
    with zipfile.ZipFile(path) as z:
        index = json.loads(z.read("modrinth.index.json"))
        names = z.namelist()
        jar_name = next((n for n in names if n.startswith("overrides/mods/TEMPERED")), None)
        jar = z.read(jar_name) if jar_name else None
    data = path.read_bytes()
    digest = hashlib.sha512(data).hexdigest()
    sidecar = Path(str(path) + ".sha512")
    if sidecar.exists() and sidecar.read_text(encoding="ascii").split()[0] != digest:
        raise SystemExit(f"Checksum file does not match {path.name}")
    info = meta.get(path.name, {})
    return {
        "file": path.name, "path": path, "mc": index["dependencies"]["minecraft"],
        "loader": index["dependencies"].get("fabric-loader", ""), "version": info.get("version") or path.name.split(" for ")[0].replace("Fancy Vanilla ", ""),
        "date": info.get("date", ""), "channel": info.get("channel", "alpha"), "legacy": bool(info.get("legacy")),
        "modrinth": info.get("modrinth", MODRINTH), "size": len(data), "sha512": digest, "index": index, "jar": jar,
    }


def load_releases():
    meta = json.loads((SITE / "versions-meta.json").read_text(encoding="utf8"))
    releases = [read_release(p, meta) for p in sorted((ROOT / "releases").glob("*/*.mrpack"))]
    releases.sort(key=lambda r: (r["date"], r["version"]), reverse=True)
    return releases


def current_by_mc(releases):
    found = {}
    for r in releases:
        if r["mc"] in CURRENT and not r["legacy"] and r["mc"] not in found:
            found[r["mc"]] = r
    if set(found) != set(CURRENT):
        raise SystemExit(f"No current release for: {sorted(set(CURRENT) - set(found))}")
    return found


GITHUB = "https://github.com/wtfangler/fancy-vanilla"


def journal_jars(cur):
    """Fancy Journal (which contains the loader) as bundled in each pack, for a standalone download."""
    found = {}
    for mc, r in cur.items():
        with zipfile.ZipFile(r["path"]) as z:
            for name in z.namelist():
                if name.startswith("overrides/mods/fancy_journal-") and name.endswith(".jar"):
                    found[mc] = (name.rsplit("/", 1)[-1], z.read(name))
    return found


# ------------------------------------------------------------------ rendering
def render_downloads(cur):
    tabs, panels = [], []
    for i, mc in enumerate(CURRENT):
        r = cur[mc]
        sel = "true" if i == 0 else "false"
        tabs.append(f'<button type="button" role="tab" id="tab-{mc}" aria-controls="panel-{mc}" aria-selected="{sel}" tabindex="{0 if i == 0 else -1}">Minecraft {mc}</button>')
        link = f"downloads/{mc}/{esc(r['file'])}"
        panels.append(f'''<div class="panel" role="tabpanel" id="panel-{mc}" aria-labelledby="tab-{mc}"{'' if i == 0 else ' hidden'}>
            <div class="ver">{esc(r['version'])}<small>{esc(r['channel'])}</small></div>
            <p class="meta">{bi('Minecraft ' + mc + ', Fabric ' + esc(r['loader']) + ', ' + human_size(r['size']), 'Minecraft ' + mc + ', Fabric ' + esc(r['loader']) + ', ' + human_size(r['size']))}</p>
            <div class="row">
              <a class="btn primary" href="{link}" download>{bi('Pobierz .mrpack', 'Download .mrpack')}</a>
              <a class="btn ghost" href="{esc(MODRINTH)}" rel="noopener">Modrinth</a>
            </div>
            <div class="hash"><span>SHA-512</span><code title="{r['sha512']}">{r['sha512'][:16]}…</code><button type="button" data-copy="{r['sha512']}">{bi('Kopiuj', 'Copy')}</button></div>
          </div>''')
    return "\n            ".join(tabs), "\n          ".join(panels)


def quest_stats(jar_bytes):
    with zipfile.ZipFile(io.BytesIO(jar_bytes)) as jar:
        names = jar.namelist()
        base = sum(1 for n in names if n.startswith("data/tempered/advancement/quest/") and n.endswith(".json"))
        epilog = sum(1 for n in names if n.startswith("data/tempered/advancement/bonus/epilog/") and n.endswith(".json") and not n.endswith("root.json"))
        era_opt = {}
        for n in names:
            m = re.match(r"data/tempered/advancement/bonus/(\d)/.+\.json$", n)
            if m:
                era_opt[int(m.group(1))] = era_opt.get(int(m.group(1)), 0) + 1
        pl = json.loads(jar.read("assets/tempered/lang/pl_pl.json"))
        en = json.loads(jar.read("assets/tempered/lang/en_us.json"))
    return base, epilog, era_opt, pl, en


def render_stats(cur, base, epilog, era_opt):
    idx = cur["26.2"]["index"]
    count = lambda kind: sum(1 for f in idx["files"] if f["path"].startswith(kind + "/"))
    mods, packs, shaders = count("mods") + 2, count("resourcepacks") + 1, count("shaderpacks")
    idx3 = cur["26.3"]["index"]
    mods3 = sum(1 for f in idx3["files"] if f["path"].startswith("mods/")) + 2
    optional_total = sum(era_opt.values())
    rows = [
        (bi("Dodane bloki, moby, biomy", "Added blocks, mobs, biomes"), "0"),
        (bi("Pliki modów (26.2 / 26.3)", "Mod files (26.2 / 26.3)"), f"{mods} / {mods3}"),
        (bi("Paczki zasobów", "Resource packs"), str(packs)),
        (bi("Shadery (domyślnie wyłączone)", "Shader packs (off by default)"), str(shaders)),
        (bi("Ery progresji", "Progression ages"), "7"),
        (bi("Zadania oryginalne", "Original quests"), str(base)),
        (bi("Zadania opcjonalne w erach", "Optional quests in ages"), str(optional_total)),
        (bi("Epilog po zabiciu smoka", "Epilogue after the dragon"), str(epilog)),
    ]
    return "\n          ".join(f"<div><dt>{k}</dt><dd>{v}</dd></div>" for k, v in rows)


def render_ages(era_opt, pl, en):
    rows = []
    for n, (need, total) in enumerate(THRESHOLDS, 1):
        name_pl, name_en = pl.get(f"tempered.era.{n}", f"ERA {n}"), en.get(f"tempered.era.{n}", f"AGE {n}")
        rows.append(f'<tr><td class="num">{n}</td><td>{bi(esc(name_pl.title()), esc(name_en.title()))}</td><td class="num">{need} / {total}</td><td class="num">{era_opt.get(n, 0)}</td></tr>')
    return "\n                ".join(rows)


def render_groups():
    spec = importlib.util.spec_from_file_location("gen_docs", ROOT / "tools" / "gen_docs.py")
    gd = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gd)
    lock = json.loads((ROOT / "tools" / "lock.json").read_text(encoding="utf8"))
    added = {a["slug"]: a for a in lock["added"]}
    blocks = [(bi("Optymalizacja", "Performance"), bi(esc(CORE), esc(CORE_EN)))]
    for pl_name, en_name, slugs in gd.GROUPS:
        names = ", ".join(gd.clean(added[s]["title"]) for s in slugs if s in added)
        blocks.append((bi(esc(pl_name), esc(en_name)), esc(names)))
    packs = [a for a in lock["added"] if a["path"].startswith("resourcepacks/")]
    pack_names = ", ".join(gd.clean(added[s]["title"]) for s in lock.get("packs", []) if s in added)
    blocks.append((bi("Paczki tekstur", "Resource packs"), esc(pack_names + f" ({len(packs) + 1})")))
    shaders = ", ".join(gd.clean(a["title"]) for a in lock["added"] if a["path"].startswith("shaderpacks/"))
    blocks.append((bi("Shadery", "Shaders"), esc(shaders)))
    return "\n        ".join(f"<div><h3>{title}</h3><p>{body}</p></div>" for title, body in blocks)


def render_versions(releases):
    rows = []
    newest = {}
    for r in releases:
        newest.setdefault(r["mc"], r["file"])
    for r in releases:
        classes = "legacy" if r["legacy"] else ("latest" if r["mc"] in CURRENT else "")
        link = f"downloads/{r['mc']}/{esc(r['file'])}"
        channel = f'<span class="tag {esc(r["channel"])}">{esc(r["channel"])}</span>'
        rows.append(f'<tr class="{classes}"><td>{esc(r["version"])}</td><td class="num">{esc(r["mc"])}</td><td>{channel}</td>'
                    f'<td class="num">{esc(r["date"])}</td><td class="num">{human_size(r["size"])}</td>'
                    f'<td class="hashcell"><code title="{r["sha512"]}">{r["sha512"][:12]}…</code><button type="button" data-copy="{r["sha512"]}">{bi("kopiuj", "copy")}</button></td>'
                    f'<td><a href="{link}" download>{bi("Pobierz", "Download")}</a></td></tr>')
    return "\n              ".join(rows)


def render_server(cur):
    pack = cur["26.2"]["file"]
    plain = (f'python build_server.py "{pack}" moj_serwer --ram 6G' + chr(10) +
             "# 1) zaakceptuj EULA w moj_serwer/eula.txt  2) start.bat (Windows) lub start.sh")
    code = (f'python build_server.py "{esc(pack)}" moj_serwer --ram 6G' + chr(10) +
            '<span class="c"># 1) zaakceptuj EULA w moj_serwer/eula.txt  2) start.bat (Windows) lub start.sh</span>')
    return esc(plain).replace(chr(10), "&#10;"), code


# ------------------------------------------------------------------ images
def make_images(out_img):
    out_img.mkdir(parents=True, exist_ok=True)
    brand = ROOT / "brand"
    shutil.copy2(brand / "logo" / "wordmark-white.png", out_img / "wordmark.png")
    live = Image.open(brand / "icons" / "favicon-live-64.png").convert("RGBA")
    live.save(out_img / "favicon.png")
    touch = Image.new("RGBA", (180, 180), (14, 16, 19, 255))
    touch.alpha_composite(live.resize((140, 140), Image.LANCZOS), (20, 20))
    touch.convert("RGB").save(out_img / "apple-touch-icon.png")
    hero = Image.open(brand / "backgrounds" / "mountains-7680x4320.jpg").convert("RGB")
    hero.thumbnail((2400, 1350), Image.LANCZOS)
    hero.save(out_img / "hero.jpg", quality=80, optimize=True, progressive=True)
    og = Image.open(brand / "banners" / "banner-1920x1080.jpg").convert("RGB").resize((1200, 675), Image.LANCZOS)
    og.crop((0, 22, 1200, 652)).save(out_img / "og.jpg", quality=86, optimize=True)
    shot = brand / "gallery" / "journal-epilog.png"
    if not shot.exists():
        raise SystemExit(f"Missing gallery screenshot: {shot}")
    img = Image.open(shot).convert("RGB")
    img.thumbnail((1600, 900), Image.LANCZOS)
    img.save(out_img / "journal-epilog.webp", quality=88, method=6)
    for name in ("loader-start", "loader-saving"):
        Image.open(brand / "gallery" / f"{name}.png").convert("RGB").save(out_img / f"{name}.webp", quality=90, method=6)


# ------------------------------------------------------------------ build
def main():
    releases = load_releases()
    cur = current_by_mc(releases)
    base, epilog, era_opt, pl, en = quest_stats(cur["26.2"]["jar"])
    tabs, panels = render_downloads(cur)
    cmd_plain, cmd_html = render_server(cur)
    latest = cur["26.2"]
    values = {
        "mc_range": " / ".join(CURRENT), "latest_version": esc(latest["version"]), "loader": esc(latest["loader"]),
        "latest_channel_pl": esc(latest["channel"]), "latest_channel_en": esc(latest["channel"]),
        "dl_tabs": tabs, "dl_panels": panels, "stats_rows": render_stats(cur, base, epilog, era_opt),
        "groups": render_groups(), "era_rows": render_ages(era_opt, pl, en), "version_rows": render_versions(releases),
        "epilog_count": str(epilog), "github": GITHUB,
        "journal_downloads": "".join(
            f'<a class="btn ghost" href="downloads/mods/{urllib.parse.quote(name)}" download>Fancy Journal {esc(name.split("-")[1].split("+")[0])} · Minecraft {mc}</a>'
            for mc, (name, _) in journal_jars(cur).items()), "server_cmd_plain": cmd_plain, "server_cmd_html": cmd_html, "modrinth": esc(MODRINTH),
    }
    page = (SITE / "index.template.html").read_text(encoding="utf8")
    for key, value in values.items():
        page = page.replace("{{" + key + "}}", value)
    left = sorted(set(re.findall(r"\{\{(\w+)\}\}", page)))
    if left:
        raise SystemExit(f"Unfilled placeholders: {left}")

    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "assets").mkdir(parents=True)
    shutil.copy2(SITE / "assets" / "site.css", OUT / "assets" / "site.css")
    shutil.copy2(SITE / "assets" / "site.js", OUT / "assets" / "site.js")
    make_images(OUT / "assets" / "img")
    jars = journal_jars(cur)
    (OUT / "index.html").write_text(page, encoding="utf8", newline="\n")
    for r in releases:
        target = OUT / "downloads" / r["mc"]
        target.mkdir(parents=True, exist_ok=True)
        shutil.copy2(r["path"], target / r["file"])
    mods_dir = OUT / "downloads" / "mods"
    mods_dir.mkdir(parents=True, exist_ok=True)
    for name, data in jars.values():
        (mods_dir / name).write_bytes(data)
    server = OUT / "downloads" / "server"
    server.mkdir(parents=True)
    with zipfile.ZipFile(server / "fancy-vanilla-server-builder.zip", "w", zipfile.ZIP_DEFLATED) as z:
        z.write(ROOT / "server" / "build_server.py", "build_server.py")
        for f in sorted((ROOT / "server" / "template").iterdir()):
            if f.is_file():
                z.write(f, "template/" + f.name)
        z.writestr("README.txt", "Extract all files, including template/.\nPython builds the server; Java 25 runs it.\n"
                   "python build_server.py \"Fancy Vanilla <version> for 26.2.mrpack\" my_server --ram 4G\n"
                   "Use a new output directory. Review and accept the Minecraft EULA yourself.\n"
                   "--no-download writes configs only and is not a complete server.\n")
    archive = ROOT / "build" / "fancy-vanilla-site.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(OUT.rglob("*")):
            if f.is_file():
                z.write(f, f.relative_to(OUT).as_posix())
    total = sum(f.stat().st_size for f in OUT.rglob("*") if f.is_file())
    print(f"Built {OUT} ({total / 1024 / 1024:.1f} MB, {len(releases)} releases) and {archive.name}")


if __name__ == "__main__":
    sys.exit(main())
