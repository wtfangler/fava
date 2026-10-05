"""Writes docs/modrinth_listing.md: everything to paste into the Modrinth project settings (summary, description with
credits for every included project, licence/links/disclosure advice, gallery order). Nothing is sent anywhere.

python tools/gen_listing.py
Run tools/pack_notes.py first when the mod lists changed.
"""
import json
import re
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MC = ("26.2", "26.3")
SUMMARY = ("Vanilla Minecraft, polished: full visual and sound overhaul, a performance core, a 7-age progression with 200+ quests (TEMPERED), "
           "a modern journal on J and its own loader. No new blocks or mobs. Fabric, Minecraft 26.2 and 26.3.")
assert len(SUMMARY) <= 256, len(SUMMARY)


def credits(mc):
    """Every file the pack downloads, with a link to its Modrinth project, read from the newest release."""
    pack = sorted((ROOT / "releases" / mc).glob("*.mrpack"))[-1]
    index = json.loads(zipfile.ZipFile(pack).read("modrinth.index.json"))
    groups = {"mods": [], "resourcepacks": [], "shaderpacks": []}
    for f in index["files"]:
        m = re.search(r"/data/([A-Za-z0-9]{8})/", f["downloads"][0])
        groups.setdefault(f["path"].split("/")[0], []).append((Path(f["path"]).stem, m.group(1) if m else None))
    out = []
    for kind, title in (("mods", "Mods"), ("resourcepacks", "Resource packs"), ("shaderpacks", "Shader packs")):
        items = sorted(groups.get(kind, []))
        if items:
            out.append(f"**{title} ({len(items)})**\n")
            out += [f"- [{n}](https://modrinth.com/project/{pid})" if pid else f"- {n}" for n, pid in items]
            out.append("")
    return "\n".join(out)


def compromises():
    notes_file = ROOT / "tools" / "data" / "pack_notes.json"
    if not notes_file.exists():
        return ""
    notes = json.loads(notes_file.read_text(encoding="utf8"))
    other = "; ".join(f"{mc}: " + (", ".join(f"{e['name']} ({e['built_for']})" for e in n["other_game_version"]) or "none") for mc, n in notes.items())
    pre = "; ".join(f"{mc}: " + (", ".join(f"{e['name']} ({e['channel']})" for e in n["prerelease"]) or "none") for mc, n in notes.items())
    return (f"- **Mods built for another game version** (their authors tag them as compatible): {other}.\n"
            f"- **Beta and alpha mods:** {pre}. Before long server sessions, check FastBack and world re-creation.\n")


DESC = f"""![Fancy Vanilla Banner](https://cdn.modrinth.com/data/cached_images/50ed80c237c4a70634c52b59643f9cb7e70da268.jpeg)

**Fancy Vanilla** keeps Minecraft vanilla and makes it look, sound and run better. There are no new blocks, mobs or biomes: you get the game you know, carefully polished, plus a progression system and a reason to keep playing after the Ender Dragon.

Available for **Minecraft 26.2** and **26.3** on **Fabric**. Built for singleplayer first, with a server-compatible setup for small groups of friends.

## What is inside

### Visual and sound polish
- Curated resource packs for foliage, leaves, crops, animations, mob models, fonts, GUI and sound, ordered so they do not fight each other.
- Particle, water and weather effects (a few of them are available on 26.2 only), a tidied interface and a Fancy Vanilla title screen.
- Two optional shader packs (via Iris). The pack is tuned to look good without them.

### Performance core
- The optimisation set from **Streamline Master**: rendering, chunk loading and generation, memory use, networking and fast game exit.
- Client-only mods are marked as client-only, so a server built from this pack does not load them.
- Note: I have not published FPS benchmarks. Results depend on your hardware, render distance and shader choice.

### TEMPERED, the seven-age progression
TEMPERED is my own mod. The world moves through seven ages, and each one unlocks recipes and gear:

| Age | Name | Quests needed to advance |
|-----|------|--------------------------|
| 1 | Wood | 6 of 9 |
| 2 | Stone | 9 of 15 |
| 3 | Iron | 8 of 13 |
| 4 | Diamond | 8 of 13 |
| 5 | Nether | 9 of 14 |
| 6 | End | 8 of 13 |
| 7 | Post-End | 8 of 12 |

- **89 original quests** make up the ages. You do not have to finish everything: only the number in the table is needed to advance.
- **63 optional personal quests** (9 per age) with small XP rewards. They never change how many quests an age needs.
- **55 Epilogue quests** that appear after you defeat the Ender Dragon, for the long game: elytra, dragon egg, navigation, rockets and more.
- Progress is shared by the world, so it also works on a server.

#### What the locks do
- Crafting of recipes from a higher age is blocked until that age is reached.
- *Holding or wearing* gear from a higher age gives **Mining Fatigue and Weakness** while it is held or worn. Take it off or put it away and the effect is cleared right away.
- **Items are never taken from you.** Anything you find in chests, loot, trades or drops stays in your inventory; it is only the use that is limited.
- Creative and spectator mode are not affected.

#### Commands
- `/trigger tempered.menu` opens the in-game menu with your status.
- Admins (`/function tempered:admin/...`): `help`, `diag`, `skip` (next age), `set_age {{n:3}}`, `reset`, `gate_off` and `gate_on` to disable or enable all locks and debuffs.
- Commands and messages are translated into English and Polish.

### Fancy Journal
One modern progress screen on **J** (rebindable) that replaces the two vanilla ones.
- Tabs per age with progress bars, search, and filters: all, remaining, completed.
- Optional quests are kept apart from the required count, and the Epilogue tab unlocks after the dragon.
- **Quest tracking:** a pin on every quest tracks it. A small panel in the bottom-right corner of the screen (movable in `config/fancy_journal.json`) shows the quest name, what to do, a checklist of the requirements with counters such as *Get: Any planks 20/32* (items are counted from your inventory, the rest from your statistics) and a progress bar, even with the journal closed. It disappears a few seconds after you finish the quest.
- Hold Shift while opening it for the classic vanilla view. If the journal ever fails, the game falls back to the classic screen on its own.

### Own loading screen
A dark screen with the Fancy Vanilla wordmark and a thin progress line replaces the Mojang logo at game start and resource reload, and is also shown while the world is saving on exit. The game still runs and fades loading as usual; the overlay only draws on top, and if it cannot load you simply get the vanilla screen.

### Languages
Quests, achievements, the journal, admin commands and the mod descriptions in Mod Menu come in **English** and **Polish**. There is no separate switch: they follow the game language (Options > Language).

## Installation
1. Install **Modrinth App** (or Prism Launcher) and use **Java 25** (the launcher can download it).
2. Search for Fancy Vanilla and install the version that matches your Minecraft version, or import the `.mrpack` file.
3. Give the client **6 GB of RAM** (the pack has over 100 mods) and launch the profile. Fabric, all mods and all settings are applied automatically.

## Servers
The pack is server-compatible. Startup, `/reload` and restart were tested on dedicated servers for 26.2 and 26.3 with no data-pack errors; I have not load-tested it with many players. Players need the pack installed on the client so that quests, the journal and the translations show up correctly.

## Good to know
- Only three files are bundled in the pack and they are all my own: TEMPERED, Fancy Journal and the Fancy Vanilla resource pack. Everything else is downloaded from Modrinth when you install.
- This is an **alpha** release. Quests were validated against the game registries and only a handful were completed in-game so far; long play sessions are still to be tested. Please report problems.
{compromises()}
## Perfect for
- Players who want vanilla survival with better visuals, sound and performance
- Small groups who want a shared progression without learning a new game
- Players who finished the game and want goals for the long run

## Changelog highlights (2.4.0)
- Quest tracking with a pin and a small HUD panel that shows what to do and how far you are.
- New TEMPERED icon; mod descriptions in Mod Menu follow the game language.
- Own loading screen (start, reload, saving).
- Commands and messages available in English and Polish.
- More optional quests, including 55 in the Epilogue.
- One journal on J instead of two progress screens.

<details>
<summary>Included content and credits (Minecraft 26.2)</summary>

All of this is downloaded from Modrinth when you install the pack. Thank you to every author.

{credits("26.2")}
</details>

<details>
<summary>Included content and credits (Minecraft 26.3)</summary>

{credits("26.3")}
</details>
"""

GALLERY = [
    ("brand/banners/banner-1920x1080.jpg", "Fancy Vanilla", "Main banner (set as featured)"),
    ("brand/gallery/loader-start.png", "Own loading screen", "Fancy Vanilla loader at game start"),
    ("brand/gallery/loader-saving.png", "Saving the world", "The same loader while saving on exit"),
    ("brand/gallery/journal-epilog.png", "Fancy Journal: Epilogue", "Journal on the J key with the post-dragon Epilogue tab"),
    ("test-logs/2.3.0-claude/shot-26.2-journal-fj_1_wide.png", "Fancy Journal: ages", "Tabs per age with progress bars"),
    ("test-logs/2.3.0-claude/shot-26.2-journal-fj_5_pause_menu.png", "One progress screen", "Pause menu with the single journal entry"),
    ("test-logs/2.4.0-claude/shot-26.2-track-fj_t1_pin.png", "Quest tracking", "A pin on every quest; the tracked one gets a frame"),
    ("test-logs/2.4.0-claude/shot-26.2-track-fj_t5_hud_multi.png", "Tracker panel", "What to do and how far you are: checklist with counters"),
]
gallery = ROOT / "brand" / "modrinth-gallery"
gallery.mkdir(exist_ok=True)
rows = []
for number, (src, title, desc) in enumerate(GALLERY, 1):
    name = f"{number:02d}-{Path(src).stem.replace('shot-26.2-', '')}{Path(src).suffix}"
    if (ROOT / src).exists():  # test screenshots are not in the repository: keep the copy that is
        shutil.copy2(ROOT / src, gallery / name)
    rows.append(f"| {number} | `brand/modrinth-gallery/{name}` | {title} | {desc} |")

text = f"""# Modrinth listing: fava

Everything to paste into the project settings. Nothing here has been sent anywhere.

## Summary (General → Summary, {len(SUMMARY)}/256)

```
{SUMMARY}
```

## Environment (when uploading a version)

**Client and server → Required on both.** Players need the pack on the client (journal, loader, translations) and the server needs TEMPERED (ages, recipes, locks).

## License (License)

- Select **All Rights Reserved/No License** and **leave the License URL empty**. A link to Wikipedia is what Modrinth flags: the URL must point at the licence text itself, and "All rights reserved" has no text to link to.
- The licence covers your own content in the pack (Fancy Vanilla resource pack, artwork, configuration). TEMPERED stays MIT in its own repo/jar; the downloaded mods keep their authors' licences.
- If you make the GitHub repo public with code under MIT, you may instead pick **MIT** for the pack and put the link to the repo's `LICENSE` file as URL. Artwork can stay all-rights-reserved in `brand/`.

## Links (Links)

- **Source code:** https://github.com/wtfangler/fancy-vanilla once the repository is public (it is private now); until then clear the field. Your website is not source code.
- **Wiki page:** your website (https://fava.netlify.app/).
- Issue tracker: https://github.com/wtfangler/fancy-vanilla/issues once the repository is public.

## Disclosures (Disclosures)

- **Contains AI-generated content:** enable it and tick **Code** and **Text**. The mod code (TEMPERED, Fancy Journal, loader), quest texts and tooling were written with Claude Code, and Modrinth requires this to be declared when AI wrote a substantial part of the code. Artwork is yours (leave Assets unticked).
- Generative AI functionality, advertisements, paid features, telemetry: leave off (none of them applies).

## Gallery (Gallery)

Upload in this order, set number 1 as featured. Files are in `brand/modrinth-gallery/`.

| # | File | Title | Description |
|---|------|-------|-------------|
{chr(10).join(rows)}

Shots 2 to 8 come from the automated test on the real game, not staged screenshots. Add a few of your own from normal play (menu, a build with shaders) when you have them; they sell the pack better than test shots.

## Description (Description)

Paste everything between the lines. The banner at the top is your existing image on cdn.modrinth.com.

---
{DESC}
---

## Before you click "Resubmit"

1. Versions: upload `releases/26.2/Fancy Vanilla 2.4.0 for 26.2.mrpack` and `releases/26.3/Fancy Vanilla 2.4.0 for 26.3.mrpack`, loader Fabric, channel alpha.
2. In the moderation thread write that the pack has no third-party files in overrides, that every other file comes from cdn.modrinth.com, and that the description lists every included project with a link.
3. Use the first section of `docs/CHANGELOG.md` as the version changelog.
"""
(ROOT / "docs" / "modrinth_listing.md").write_text(text, encoding="utf8")
print(len(text), "bytes; summary", len(SUMMARY), "chars")
