#!/usr/bin/env python3
"""Generate honest release docs (README, Modrinth description, changelog, quest list).

Run after building both mrpacks (the website is built separately by tools/build_site.py). No upload happens. Runtime checks
remain pending unless the caller explicitly names completed --runtime-check.
"""
import argparse
import hashlib
import html
import io
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PROJECT = "https://modrinth.com/modpack/fava"
DATE = "05.10.2026"
COMMANDS = {
    "Wyłącz blokadę przepisów i osłabienia sprzętu (ustawienie przetrwa restart)": "/function tempered:admin/gate_off",
    "Ponownie włącz ograniczenia progresji": "/function tempered:admin/gate_on",
    "Ustaw wspólną erę, przykład ery 3 (dozwolone 1–7)": "/function tempered:admin/set_age {n:3}",
    "Wyzeruj postęp wszystkich graczy, także nieobecnych; używaj świadomie": "/function tempered:admin/reset",
}

GROUPS = [
    ("Wygląd i animacje", "Look and animations", ["entity-model-features", "entitytexturefeatures", "not-enough-animations", "3dskinlayers", "optigui", "animaticarefabricated", "bettergrassify", "better-clouds", "puzzle"]),
    ("Atmosfera i dźwięk", "Atmosphere and sound", ["ambient-environment", "fallingleaves", "wakes", "visuality", "subtle-effects", "explosive-enhancement", "particle-rain", "particular-reforged", "particle-effects", "lambdynamiclights", "make_bubbles_pop", "glowing-torchflower", "ambientsounds", "sound-physics-remastered", "sound"]),
    ("Informacje i wygoda", "Information and comfort", ["jade", "appleskin", "betterf3", "better-stats", "bookshelf-inspector", "durability-tooltip", "status-effect-bars", "inventory-sorting", "searchables", "morechathistory", "chat-heads", "controlify", "controlling", "xaeros-minimap", "xaeros-world-map"]),
    ("Narzędzia serwera", "Server tools", ["clumps", "chunky", "spark", "fastback"]),
]


def encode(value):
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf8")


def atomic_write(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix="." + path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as target:
            target.write(data if isinstance(data, bytes) else data.encode("utf8"))
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def safe_name(name):
    path = PurePosixPath(name)
    if not name or path.is_absolute() or ".." in path.parts or "\\" in name or ":" in name or "\0" in name:
        raise ValueError(f"Unsafe website archive path: {name!r}")
    return name


def zip_bytes(entries):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, content in sorted(entries.items()):
            safe_name(name)
            info = zipfile.ZipInfo(name, (2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, content)
    return buffer.getvalue()


def build_constants():
    spec = importlib.util.spec_from_file_location("fv_build", ROOT / "tools" / "build.py")
    build = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(build)
    return {"VERSION": build.VERSION, "TEMPERED_JAR": build.TEMPERED_JAR, "JOURNAL_VERSION": build.JOURNAL_VERSION}


def pack_info(mc, version):
    filename = f"Fancy Vanilla {version} for {mc}.mrpack"
    path = ROOT / "releases" / mc / filename
    lock = json.loads((ROOT / "tools" / ("lock.json" if mc == "26.2" else "lock-26.3.json")).read_text(encoding="utf8"))
    if lock.get("log"):
        raise ValueError(f"Unresolved lock for {mc}: {lock['log']}")
    with zipfile.ZipFile(path) as archive:
        index = json.loads(archive.read("modrinth.index.json"))
        if index["dependencies"]["minecraft"] != mc:
            raise ValueError(f"Wrong Minecraft version in {filename}")
        if index["versionId"] != f"{version}+{mc}":
            raise ValueError(f"Stale release file {filename}")
        bundled_mods = [n for n in archive.namelist() if n.startswith("overrides/mods/") and n.endswith(".jar")]
        bundled_packs = [n for n in archive.namelist() if n.startswith("overrides/resourcepacks/") and n.endswith(".zip")]
        if len(bundled_mods) != 2:
            raise ValueError(f"Expected TEMPERED + Fancy Journal in {filename}: {bundled_mods}")
        mod_versions = {}
        for name in bundled_mods:
            with zipfile.ZipFile(io.BytesIO(archive.read(name))) as jar:
                metadata = json.loads(jar.read("fabric.mod.json"))
                mod_versions[metadata["id"].lower()] = metadata["version"]
        counts = {category: sum(f["path"].startswith(category + "/") for f in index["files"])
                  for category in ("mods", "resourcepacks", "shaderpacks")}
        checksum_file = path.with_suffix(".mrpack.sha512")
        if not checksum_file.is_file() or checksum_file.read_text(encoding="ascii").split()[0] != hashlib.sha512(path.read_bytes()).hexdigest():
            raise ValueError(f"Missing or incorrect release checksum: {filename}")
    return {"mc": mc, "filename": filename, "path": path, "lock": lock, "counts": counts,
            "bundled_mods": len(bundled_mods), "bundled_packs": len(bundled_packs), "mod_versions": mod_versions,
            "total_mods": counts["mods"] + len(bundled_mods),
            "total_packs": counts["resourcepacks"] + len(bundled_packs)}


def clean(title):
    title = re.sub(r"[🀀-🿿☀-➿️]", "", title)
    return re.sub(r"\s{2,}", " ", re.sub(r"^\[[^\]]+\]\s*|^\([^)]+\)\s*", "", title)).strip()


def group_text(lock, language=0):
    added = {entry["slug"]: entry for entry in lock["added"]}
    return "\n\n".join("**" + group[language] + ":** " + ", ".join(clean(added[s]["title"]) for s in group[2] if s in added) + "."
                        for group in GROUPS)


def list_differences(lock):
    dropped = ", ".join(value.partition(": ")[2] or value for value in lock.get("dropped", [])) or "brak"
    fallback = ", ".join(lock.get("fallback", [])) or "brak"
    return dropped, fallback


def validation(checks, language=0, version="2.1.0"):
    labels = {"server-26.2": "serwer 26.2", "server-26.3": "serwer 26.3", "client-26.2": "klient 26.2", "client-26.3": "klient 26.3"}
    if not checks:
        return (f"Testy uruchomieniowe wersji {version} są w toku. Logi starszych wydań pokazują wcześniejsze uruchomienia i problemy, które poprawiono; nie potwierdzają wyniku {version}."
                if language == 0 else f"Runtime tests for {version} are pending. Logs of older releases document earlier launches and issues addressed here; they do not verify this release.")
    targets = ", ".join(labels[c] if language == 0 else c.replace("-", " ") for c in sorted(checks))
    return (f"Potwierdzone testy uruchomieniowe {version}: {targets}. Zakres i logi: docs/CLAUDE_REVIEW_2.1.0.md oraz docs/CODEX_REVIEW.md."
            if language == 0 else f"Confirmed {version} runtime checks: {targets}. Scope and logs: docs/CLAUDE_REVIEW_2.1.0.md and docs/CODEX_REVIEW.md.")


def quest_rows(info):
    """(group, title, description, xp) for every optional quest; group is an era number or 'epilog'."""
    def text(value, lang):
        if isinstance(value, str): return value
        if isinstance(value, list): return "".join(text(part, lang) for part in value)
        result = value.get("text", lang.get(value.get("translate"), value.get("translate", "")))
        for part in value.get("with", []): result = result.replace("%s", text(part, lang), 1)
        return result + text(value.get("extra", []), lang)
    tables = {}
    for mc, package in info.items():
        with zipfile.ZipFile(package["path"]) as pack:
            name = next(n for n in pack.namelist() if n.startswith("overrides/mods/TEMPERED"))
            with zipfile.ZipFile(io.BytesIO(pack.read(name))) as jar:
                lang = json.loads(jar.read("assets/tempered/lang/pl_pl.json"))
                rows = []
                for name in sorted(jar.namelist()):
                    if not name.startswith("data/tempered/advancement/bonus/") or not name.endswith(".json"): continue
                    if name.endswith("/epilog/root.json"): continue
                    goal = json.loads(jar.read(name))
                    group = name.split("/")[4]
                    group = "epilog" if group == "epilog" else int(group)
                    clean_text = lambda value: text(value, lang).replace("|", chr(92) + "|").replace(chr(10), " ")
                    rows.append((group, clean_text(goal["display"]["title"]), clean_text(goal["display"]["description"]), goal["rewards"]["experience"]))
        per_era = [sum(row[0] == era for row in rows) for era in range(1, 8)]
        if len(set(per_era)) != 1 or per_era[0] < 3 or sum(row[0] == "epilog" for row in rows) < 30:
            raise ValueError(f"Unexpected optional quest layout in {mc}: {per_era}")
        tables[mc] = rows
    if tables["26.2"] != tables["26.3"]:
        raise ValueError("Optional quest descriptions/rewards differ between versions")
    return tables["26.2"]


def quest_counts(rows):
    n_epilog = sum(row[0] == "epilog" for row in rows)
    return len(rows) - n_epilog, n_epilog, sum(row[3] for row in rows if row[0] == "epilog")


def quest_catalogue(info):
    rows = quest_rows(info)
    n_era, n_epilog, epilog_xp = quest_counts(rows)
    per_era = n_era // 7
    era_rows = "".join(f"| {era} | {title} | {description} | {xp} |" + chr(10) for era, title, description, xp in rows if era != "epilog")
    epilog_rows = "".join(f"| {title} | {description} | {xp} |" + chr(10) for era, title, description, xp in rows if era == "epilog")
    return f"""# Dodatkowe questy Fancy Vanilla

{n_era} zadań opcjonalnych w erach ({per_era} na erę) i {n_epilog} w gałęzi **Epilog**, z osobistym postępem i nagrodami XP.
Zaczynają zaliczać zdarzenia po odblokowaniu swojej ery (Epilog: po pokonaniu Smoka Endu). Nie zwiększają globalnego
licznika przejścia ery; oryginalne 89 zadań i ich progi pozostają bez zmian.
Otwórz Dziennik przez **J**, **L** lub przycisk w menu pauzy.

## Questy er

| Era | Quest | Cel | XP |
|---|---|---|---:|
{era_rows}
## Epilog: po zabiciu smoka

Ukryta zakładka **Epilog** odblokowuje się, gdy pokonasz Smoka Endu (albo masz już osiągnięcie *Koniec?* z vanilli, np. w istniejącym świecie).
{n_epilog} celów na długie wieczory: wyprawy i walka z bossami, hodowla, budowle, mikstury i zaklęcia oraz kolekcje. Razem {epilog_xp} XP na osobę.
Cele zaliczasz po odblokowaniu zakładki; przedmioty zdobyte wcześniej liczą się, gdy tylko je przestawisz lub zdobędziesz kolejny raz.
Reset administratora czyści postęp także w Epilogu.

| Quest | Cel | XP |
|---|---|---:|
{epilog_rows}"""


def pack_notes():
    path = ROOT / "tools" / "data" / "pack_notes.json"
    return json.loads(path.read_text(encoding="utf8")) if path.exists() else {}


def compromises(language=0):
    """Mods built for another game version and alpha/beta mods, from tools/data/pack_notes.json (tools/pack_notes.py)."""
    notes = pack_notes()
    if not notes:
        return ""
    none = "brak" if language == 0 else "none"
    other = "; ".join(f"{mc}: " + (", ".join(f"{e['name']} ({e['built_for']})" for e in n["other_game_version"]) or none) for mc, n in notes.items())
    pre = "; ".join(f"{mc}: " + (", ".join(f"{e['name']} ({e['channel']})" for e in n["prerelease"]) or none) for mc, n in notes.items())
    if language == 0:
        return (f"**Mody zbudowane pod inną wersję gry** (autorzy oznaczają je jako zgodne): {other}.\n\n"
                f"**Mody w wersjach beta i alpha:** {pre}. Przed dłuższą grą na serwerze sprawdź FastBack i odtworzenie świata.")
    return (f"**Mods built for another game version** (their authors tag them as compatible): {other}.\n\n"
            f"**Beta and alpha mods:** {pre}. Before long server sessions, check FastBack and world re-creation.")


def render_docs(constants, info, checks):
    if not COMMANDS:
        raise ValueError("TEMPERED public commands need verification before generating docs")
    journal = constants["JOURNAL_VERSION"]
    version = constants["VERSION"]
    tempered = re.fullmatch(r"TEMPERED(.+)mc26\.2\.jar", constants["TEMPERED_JAR"]).group(1)
    for mc, package in info.items():
        if package["mod_versions"] != {"tempered": tempered, "fancy_journal": f"{journal}+mc{mc}"}:
            raise ValueError(f"Stale bundled mods in {mc}: {package['mod_versions']}")
    a, b = info["26.2"], info["26.3"]
    n_era, n_epilog, _ = quest_counts(quest_rows(info))
    dropped, fallback = list_differences(b["lock"])
    shaders = ", ".join(clean(f["title"]) for f in a["lock"]["added"] if f["path"].startswith("shaderpacks/"))
    counts = "\n".join(f"| {p['mc']} | {p['total_mods']} ({p['counts']['mods']} + 2 własne) | {p['total_packs']} ({p['counts']['resourcepacks']} + 1 własna) | {p['counts']['shaderpacks']} |" for p in (a, b))
    controls = "\n".join(f"- {description}: `{command}`." for description, command in COMMANDS.items())
    pl = f"""# Fancy Vanilla

**Minecraft 26.2 i 26.3 · Fabric · singleplayer i mały serwer ze znajomymi · {version} alpha**

Znany Minecraft z bogatszą oprawą: animacje mobów, roślinność, cząsteczki, dźwięk, tekstury i opcjonalne shadery. Rdzeń **Streamline Master** odpowiada za optymalizację, a autorski **TEMPERED** porządkuje przygodę w 7 er: 89 oryginalnych zadań oraz {n_era} nowych zadań opcjonalnych w erach i gałąź **Epilog** z {n_epilog} celami po zabiciu smoka. Paczka nie dodaje bloków, mobów ani biomów.

### TEMPERED i własna baza

Zadania prowadzą od drewna do wypraw po Endzie, zostawiając miejsce na budowanie i własne cele. Przepisy wyższych er mogą być blokowane do odpowiedniej ery. Zbyt zaawansowany sprzęt jest ograniczany przez efekty i osłabienia; nie oznacza to fizycznego zakazu zakładania pancerza czy używania elytry. Usunięcie pliku TEMPERED usuwa jego funkcje po ponownym wczytaniu świata, ale nie cofa zapisanej reguły ograniczonego craftingu ani stanu odblokowanych przepisów. Najpierw wyłącz ograniczenia komendą opisaną poniżej.

Ery są **wspólne dla świata**: w singleplayer odblokowujesz je sam, a na serwerze postęp graczy przesuwa wspólną erę. Nie trzeba wykonywać wszystkich zadań, aby przejść dalej: progi kolejnych er to **6/9, 9/15, 8/13, 8/13, 9/14, 8/13, 8/12**. Są stałe; paczka nie oferuje przełącznika er indywidualnych ani konfiguracji tych progów. Administrator może wyłączyć ograniczenia przez `/function tempered:admin/gate_off` i włączyć je przez `/function tempered:admin/gate_on`; wybór przetrwa przeładowanie i restart. Stan sprawdzisz przez `/trigger tempered.menu`.

### Oprawa i wygoda

{group_text(a['lock'])}

**Shadery:** {shaders}. Są domyślnie wyłączone. W ustawieniach Sterowania sprawdzisz skróty Iris do wyboru i przełączania shaderów. **Zoomify** obsługuje przybliżenie pod C. Fancy Vanilla zachowuje własne logo, menu oraz paczkę zasobów.

### Fancy Journal {journal}

Naciśnij **J** lub wybierz **Dziennik** w menu pauzy. Własny skrót zmienisz w ustawieniach sterowania. Klawisz osiągnięć **L** również otwiera dziennik z zakładkami, postępem, wyszukiwaniem i filtrami: Wszystkie, Pozostałe, Ukończone. Układ dopasowuje się do rozmiaru okna; listy i zadania można przewijać, a wybór zakładki pozostaje stabilny. Ukryte nieukończone zadania nie są ujawniane. Lista aktualizuje się po zmianach osiągnięć, bez pełnego przebudowywania w każdej klatce. W singleplayer otwarty dziennik zatrzymuje grę jak klasyczny ekran osiągnięć; na serwerze gra trwa dalej. **Shift** przy otwieraniu lub „Klasyczny widok” pozwala wrócić do ekranu vanilli. Zakładki przełączysz także przez **Ctrl+PageUp/PageDown**, a zadania przewiniesz przez **PageUp/PageDown/Home/End**.

Każda era ma {n_era // 7} dodatkowych celów dla własnej bazy i wypraw. Po pokonaniu Smoka Endu odblokowuje się ukryta zakładka **Epilog**: {n_epilog} opcjonalnych celów, które dają co robić po końcu gry. Wszystkie są oznaczone jako **opcjonalne**, mają osobisty postęp i nagrody XP. Nie zwiększają licznika przejścia do kolejnej ery ani nie zmieniają powyższych progów. Lista: [nowe questy](QUESTS.md).

### Instalacja

1. Zaimportuj `.mrpack` do Modrinth App lub Prism Launcher i wybierz wariant zgodny z wersją Minecrafta.
2. Użyj **Java 25**. Zacznij od 6 GB RAM dla klienta (paczka ma ponad 100 modów), dobierając ustawienia do swojego komputera.
3. W nowym świecie progresja zaczyna się od drewna. Przed dodaniem paczki do istniejącego świata zrób kopię; obecny ekwipunek może przekraczać początkową erę.

Paczka nadaje się do singleplayer i małego serwera znajomych. Instrukcja budowy serwera, jego ustawienia startowe oraz funkcje administracyjne są w README. Shadery i wysokość renderowania zwiększają obciążenie; nie podajemy gwarancji FPS ani liczby graczy.

### Warianty

| Minecraft | Pliki modów | Paczki zasobów | Shadery |
|---|---:|---:|---:|
{counts}

Liczby dotyczą plików w paczce. Fabric może raportować więcej modułów, ponieważ biblioteki zawierają zagnieżdżone jary.

**26.3:** wariant nie zawiera: {dropped}. Następujące paczki zasobów korzystają z wydań oznaczonych dla 26.2: {fallback}. Ich zgodność deklarowana przez autorów jest węższa, dlatego wygląd wymaga sprawdzenia w grze.

{compromises(0)}

**Weryfikacja:** {validation(checks, 0, version)} Testy uruchomienia nie zastępują dłuższej gry ze znajomymi ani porównania wydajności. Dobór shaderów i efekty nakładających się tekstur wymagają oceny na docelowym sprzęcie.

[Projekt Fancy Vanilla na Modrinth]({PROJECT}). Pliki i strona WWW powstają lokalnie; samo przygotowanie wydania nie oznacza publikacji.

---

# Fancy Vanilla — English

**Minecraft 26.2 and 26.3 · Fabric · singleplayer and a small server with friends · {version} alpha**

Familiar Minecraft with richer animation, foliage, particles, audio, textures and optional shaders. **Streamline Master** provides the optimisation base. The author's **TEMPERED** progression adds 7 ages, preserving 89 original quests and adding {n_era} optional quests plus an **Epilogue** branch of {n_epilog} goals after the Ender Dragon, without adding blocks, mobs or biomes.

Higher-age recipes can be locked. Higher-age equipment is restricted through effects and penalties; armour and elytra are not physically prevented from being equipped. Removing the TEMPERED jar removes its functions after reloading the world, but saved limited-crafting rules and recipe unlocks remain. Disable the gates before removing it. Ages are shared across the world: play alone in singleplayer or advance a shared age with friends. Fixed quest thresholds are **6/9, 9/15, 8/13, 8/13, 9/14, 8/13, 8/12**. Individual ages and custom thresholds are not provided. Administrators can disable gates through `/function tempered:admin/gate_off` and restore them through `/function tempered:admin/gate_on`; the setting survives reloads and restarts. Players can check status through `/trigger tempered.menu`.

**Fancy Journal {journal}** opens with configurable **J**, the **Journal** button in the pause menu, or **L**, providing a responsive layout, scrolling tabs/tasks, search, filters and progress. Hidden unfinished tasks remain hidden; selected tabs stay stable and the list refreshes when progress changes. It pauses an ordinary singleplayer game like the vanilla advancement screen, while multiplayer keeps running. Hold **Shift** when opening or use *Classic view* for the vanilla screen. **Ctrl+PageUp/PageDown** switches tabs and **PageUp/PageDown/Home/End** scrolls tasks. Each age has {n_era // 7} extra optional goals for exploration and building, and a hidden **Epilogue** tab unlocks after the Ender Dragon with {n_epilog} more; their personal progress and XP rewards do not change the shared age thresholds.

Import the matching `.mrpack` in Modrinth App or Prism Launcher, use **Java 25**, and start with 6 GB client RAM (the pack has over 100 mods). Back up existing worlds before installing: existing equipment may exceed the initial age. Shaders are off by default; rendering settings should be chosen for your hardware.

The 26.2 variant contains **{a['total_mods']} top-level mod files**, **{a['total_packs']} resource packs** and **{a['counts']['shaderpacks']} shader packs**; 26.3 contains **{b['total_mods']}**, **{b['total_packs']}** and **{b['counts']['shaderpacks']}** respectively. Each includes two custom mods, TEMPERED and Fancy Journal. Nested libraries increase the number reported by Fabric.

The 26.3 variant omits: {dropped}. Resource packs using 26.2-labelled releases: {fallback}; inspect their appearance in game.

{compromises(1)}

**Validation:** {validation(checks, 1, version)} Launch checks do not establish a performance benchmark or multiplayer capacity. Visual combinations and shaders need testing on your hardware.

[Fancy Vanilla on Modrinth]({PROJECT}). Preparing local archives does not publish them.
"""
    readme = f"""# Fancy Vanilla {version}

Minecraft 26.2 / 26.3, Fabric, Java 25. Oprawa Fancy Vanilla, optymalizacja Streamline Master i progresja TEMPERED. Docelowo singleplayer i mały serwer ze znajomymi.

| Plik / katalog | Przeznaczenie |
|---|---|
| `releases/26.2/{a['filename']}` | Klient Minecraft 26.2 |
| `releases/26.3/{b['filename']}` | Klient Minecraft 26.3 |
| `docs/modrinth_description.md` | Opis PL/EN |
| `docs/CHANGELOG.md` | Zmiany wydania |
| `docs/CODEX_REVIEW.md` | Zakres weryfikacji i uwagi |
| `server/build_server.py`, `server/template/` | Budowa dedykowanego serwera |
| `site/` (źródło), `build/site/` (wynik) | Strona projektu; `python tools/build_site.py` składa ją i pakuje do ZIP-a do wdrożenia |
| `brand/`, `src/resourcepack/` | Oryginalna identyfikacja wizualna (logo, ikony, banery) |

## Skład

| Minecraft | Pliki modów | Paczki zasobów | Shadery |
|---|---:|---:|---:|
{counts}

Dwa własne mody to TEMPERED {tempered} i Fancy Journal {journal}. Paczka FancyVanilla.zip jest własnym zasobem. Liczymy wszystkie wpisy obu locków oraz te pliki dołączone w overrides; nie tylko nowo dodane dodatki. Zagnieżdżone biblioteki nie są osobnymi plikami w tym zestawieniu.

## Instalacja i progresja

Zaimportuj wariant `.mrpack` zgodny z wersją gry. Klient: Java 25, początkowo 6 GB RAM; shadery są wyłączone. Zrób kopię istniejącego świata przed dodaniem progresji.

TEMPERED ma 7 er, 89 oryginalnych zadań, {n_era} nowych opcjonalnych celów w erach i {n_epilog} w gałęzi Epilog (po zabiciu smoka). Blokadę przepisów oraz osłabienia zbyt zaawansowanego sprzętu można włączyć lub wyłączyć. Pancerz i elytra nie są fizycznie zablokowane przed założeniem. TEMPERED jest datapackiem w formie moda. Usunięcie `{constants['TEMPERED_JAR']}` usuwa funkcje po ponownym wczytaniu świata, ale pozostawia zapisaną regułę ograniczonego craftingu i odblokowane przepisy. **Przed usunięciem wywołaj gate_off.** Jeżeli plik już usunięto, administrator może użyć `/gamerule minecraft:limited_crafting false` oraz `/recipe give @a *` dla obecnych graczy (powtórz odblokowanie po dołączeniu nieobecnych).

Ery są globalne dla świata. Na serwerze osiągnięcia graczy przesuwają wspólną erę; nie ma trybu er indywidualnych. Stałe progi to **6/9, 9/15, 8/13, 8/13, 9/14, 8/13, 8/12**; nie trzeba zaliczyć wszystkich zadań. Paczka nie udostępnia konfiguracji tych progów.

Stan progresji sprawdzisz przez `/trigger tempered.menu` bez OP. Poniższe funkcje administracyjne wymagają uprawnień do komend (OP na serwerze lub komendy w świecie). Zmianę wspólnej ery i reset uzgodnij z pozostałymi graczami.

{controls}

Fancy Journal otwierasz przez **J**, przycisk **Dziennik** w menu pauzy lub **L**. Własny skrót jest konfigurowalny. Dostępne są wyszukiwarka, filtry, przewijanie i klasyczny ekran pod **Shift**. Dziennik zachowuje widoczność ukrytych osiągnięć, stabilny wybór zakładki i aktualizuje listę po zmianach postępu. Zatrzymuje zwykły singleplayer; na serwerze nie zatrzymuje świata.

Dodatkowe questy ({n_era // 7} w każdej erze oraz {n_epilog} w Epilogu po zabiciu smoka) są osobiste, opcjonalne i nagradzane XP. Nie liczą się do progu przejścia wspólnej ery. [Lista nowych zadań](docs/QUESTS.md).

## Serwer

Gracze instalują ten sam wariant paczki. Buduj w **nowym katalogu**; nie nadpisuj istniejącej instalacji z innym zestawem modów.

```powershell
python server/build_server.py "releases/26.2/{a['filename']}" moj_serwer_26_2 --ram 4G
python server/build_server.py "releases/26.3/{b['filename']}" moj_serwer_26_3 --ram 4G
```

W paczce serwerowej pobranej jako osobny ZIP skrypt jest w katalogu głównym: użyj `python build_server.py ...` i zachowaj katalog `template` obok niego. Przeczytaj EULA, zaakceptuj ją samodzielnie w `eula.txt`, a następnie uruchom `start.bat` lub `start.sh` na Java 25. Builder sprawdza hashe modów, wybiera stronę serwerową i zachowuje istniejące ustawienia/start scripts; nie zarządza światem.

Domyślne `view-distance=8`, `simulation-distance=6`, limit 15 graczy i 4 GB maksymalnej pamięci są ustawieniami startowymi, nie potwierdzoną pojemnością serwera. Zacznij od kilku znajomych, potem oceń czasy ticków przez spark. Chunky służy do przygotowania terenu, FastBack do kopii zapasowych. Zweryfikuj konfigurację backupu i możliwość odtworzenia świata przed dłuższą grą.

`--no-download` tworzy konfiguracje/skrypty i dołączone mody. **Nie tworzy kompletnego, gotowego do uruchomienia serwera.** W nowym katalogu nie dostarcza pobieranych modów ani Fabric launchera.

## Budowa ze źródeł

`tools/resolve.py` ustala locki; aktualizacja wymaga świadomego wyboru. Następnie zbuduj TEMPERED i Fancy Journal zgodnie z ich narzędziami, potem paczki:

```powershell
python tools/build.py --mc 26.2
python tools/build.py --mc 26.3
python tools/check_deps.py KATALOG_JAROW_26_2 --side both --index "releases/26.2/{a['filename']}" --fabric-loader-jar FABRIC_LOADER_0_19_5_JAR
python tools/check_deps.py KATALOG_JAROW_26_3 --side both --index "releases/26.3/{b['filename']}" --fabric-loader-jar FABRIC_LOADER_0_19_5_JAR
python tools/gen_docs.py
```

Kontrola zależności jest domyślnie offline; `--download` jawnie pozwala pobrać brakujące pliki. Oba katalogi audytu muszą zawierać także dwa jary z `overrides/mods`. Podaj rzeczywisty JAR Fabric Loader, żeby uwzględnić jego dołączone biblioteki. Po zmianie locka odczytaj metadane zasobów przez `python tools/annotate_resources.py --mc 26.2 --cache KATALOG_RESOURCEPACKS` (analogicznie 26.3; `--download` pobiera brakujące pliki). Budowanie Dziennika wymaga Java 25, zestawu klienta/bibliotek w `--dev-dir` oraz właściwego Fabric API w `--fabric-api`. Generator dokumentacji wymaga gotowych paczek i zgodnych SHA512. Zachowuje istniejącą oprawę strony i generuje ZIP w pamięci, bez rozpakowywania i kasowania katalogów. Nie trzeba ponownie uruchamiać `gen_assets.py` do zwykłej budowy wydania.

## Różnice i status testów

26.3 nie zawiera: {dropped}. Wydania zasobów użyte jako fallback z 26.2: {fallback}.

{compromises(0)}

{validation(checks, 0, version)} Nie podajemy wyniku FPS z pięciu próbek jako benchmarku. Do dalszych testów należą dłuższa gra, istniejący świat, shader i obciążenie małego serwera. [Projekt Modrinth]({PROJECT}).
"""
    changelog = f"""# Changelog

## {version} alpha — Minecraft 26.2 / 26.3 — 06.10.2026

- **26.2** stoi teraz na nowej bazie **Streamline Master 1.5.2** (dużo lepsza wydajność): baza nie ma już trio wątkowego C2ME, VMP i ScalableLux, a ma własne, dopracowane konfiguracje (Dynamic FPS, Entity Culling, More Culling, Lithium, ModernFix, ImmediatelyFast i inne). Te ustawienia mają pierwszeństwo, tak samo jak na 26.3. Zostają tylko dwie poprawki Fancy Vanilla: wyłączony zoom Chloride (zoom robi Zoomify) i ustawienia cząsteczek.
- **26.3** bez zmian w zawartości (nadal Streamline Master 1.6.2-beta). Zmienia się tylko numer wydania.

## 0.1.0 alpha — Minecraft 26.2 / 26.3 — 06.10.2026

- Pierwsze wydanie w numeracji `MAJOR.MINOR.PATCH+wersja gry` (zasady w `docs/VERSIONING.md`); dotychczasowe numery robocze 2.x nie były publikowane.
- **26.3** stoi na nowej bazie optymalizacyjnej **Streamline Master 1.6.2-beta** (własna wersja autora dla 26.3): mody bazy są w dokładnie tych wersjach, które wskazuje jej paczka, razem z jej ustawieniami i konfiguracjami. Dodatki Fancy Vanilla (oprawa, TEMPERED, Fancy Journal, loader) zostają. **26.2** stała jeszcze na Streamline Master 1.5.1.
- Śledzenie zadań (Fancy Journal 1.2.0): pinezka przy każdym zadaniu w dzienniku. Panel w prawym dolnym rogu ekranu pokazuje nazwę zadania, opis, listę wymagań z haczykami i liczniki (np. „Zdobądź: Dowolne deski 20/32”): przedmioty liczone są z ekwipunku, reszta ze statystyk gracza, a przy zadaniach wieloetapowych każdy krok ma osobny haczyk. Po ukończeniu panel znika sam. Wybór i róg panelu (`corner`) zapisują się w `config/fancy_journal.json`. Tylko 26.2 i 26.3. Uwaga: liczniki ze statystyk to statystyki całego życia gracza w świecie, więc w świecie założonym przed TEMPERED mogą wyprzedzać wewnętrzny licznik zadania; panel nie pokaże wtedy ukończenia przed serwerem.
- Nowa ikona moda TEMPERED (TEMPERED 2.20.0).
- Usunięto mod Remove Reloading Screen (RRLS): Controlify blokuje go przy każdym uruchomieniu, a własny loader rysuje się niezależnie od niego. Zalecana pamięć klienta to teraz 6 GB (paczka ma ponad 100 modów).
- Opisy modów w Mod Menu zależą od języka gry (po angielsku i po polsku), tak jak zadania, komendy i dziennik. Język wybiera się w grze: Opcje > Język; moda nie mają osobnego przełącznika.

## Robocze 2.3.0 (poprzednia numeracja, nieopublikowane)

- Własny loader Fancy Vanilla (Fancy Journal 1.1.0): ciemny ekran z logo i paskiem postępu zamiast logo Mojang przy starcie gry i przeładowaniu zasobów oraz przy komunikatach typu „Zapisywanie świata”. Vanilla nadal steruje ładowaniem i wygaszaniem; nakładka tylko rysuje na wierzchu.
- Dwa języki (PL/EN): komunikaty komend administracyjnych (`help`, `diag`, `gate_on/off`, `set_age`, `reset`, status) korzystają teraz z kluczy tłumaczeń (TEMPERED 2.19.0), tak jak zadania i osiągnięcia. Wersja angielska działa po przełączeniu języka gry.
- Zadania opcjonalne: 63 w erach (po 9) i 55 w Epilogu (po zabiciu smoka); progi przejścia er bez zmian. Wbudowany przycisk „Postępy” w menu pauzy zastąpiono jednym dziennikiem pod klawiszem J.

## Robocze 2.0–2.2 (nieopublikowane)

- Poprawiono zamykanie klienta z aktywnymi animowanymi teksturami: Fancy Journal kończy pulę roboczą Animatica przy wyjściu z gry.
- Kolejność paczek zasobów zachowuje Clearer Slot Highlight nad DARK, a lista wyjątków zgodności wynika z rzeczywistych metadanych pobranych ZIP-ów. Wariant 26.3 korzysta z przypiętej, zweryfikowanej czcionki 4.0.

- Fancy Journal {journal}: dopasowanie do okna, przewijanie zakładek/zadań, poprawna widoczność ukrytych osiągnięć, stabilny wybór zakładki i odświeżanie po zmianach postępu. Zwykły singleplayer zatrzymuje się jak przy ekranie vanilli.
- TEMPERED {tempered}: wyłączenie ograniczeń przez gate_off przetrwa restart; gate_on ponownie je włącza. Reset obejmuje też nieobecnych graczy, set_age sprawdza zakres 1–7, a natywny sprzęt miedziany i włócznie mają przypisane poziomy. Ery pozostają globalne, z zachowanymi 89 zadaniami i stałymi progami. Dodano po trzy osobiste questy opcjonalne do każdej ery, z niewielkimi nagrodami XP; nie zwiększają wymaganego postępu ery.
- Dziennik otrzymał konfigurowalny skrót J oraz przycisk w menu pauzy. Zadania opcjonalne są oddzielone od licznika zadań potrzebnych do przejścia ery.
- ModernFix: przywrócono wyłączone czyszczenie ClassInfo i leniwe tworzenie rendererów. Poprzednie logi zawierały wyjątek klientowej klasy na serwerze oraz tworzenie renderera na CullThread klienta.
- 26.2: Particle Core korzysta z BOUNDING_BOX; jego optymalizacje i efekty wizualne zostają. Zoomify jest wybranym zoomem, ustawienie Chloride wyłączone i jego klawisz zwolniony.
- Paczki zasobów: poprawiona kolejność i usunięte powtórzenia. Clearer Slot Highlight znajduje się powyżej DARK; konfiguracje uwzględniają rzeczywisty zestaw modów danego wariantu.
- Zachowano identyfikację Fancy Vanilla: własne grafiki, menu, roślinność, animacje, efekty, dźwięk i opcjonalne shadery.
- Liczby składu obejmują całe locki i dwa dołączone mody: 26.2 — {a['total_mods']} pliki modów, {a['total_packs']} paczek zasobów, {a['counts']['shaderpacks']} shadery; 26.3 — {b['total_mods']}, {b['total_packs']}, {b['counts']['shaderpacks']}.
- Instrukcje serwera opisują nowy katalog oraz ograniczony zakres `--no-download`. Lokalna strona odsyła do projektu Modrinth; nie zakłada istnienia opublikowanego adresu `/version/{version}`.

**Weryfikacja:** {validation(checks, 0, version)} Test uruchomienia nie stanowi benchmarku FPS ani testu pojemności serwera. Wyniki z pięciu próbek wcześniejszej wersji usunięto z deklaracji wydajności.

### Różnice wariantu 26.3

Brak w tym locku: {dropped}. Paczki zasobów wykorzystujące wydania 26.2: {fallback}. Zgodność wyglądu wymaga sprawdzenia w grze.

{compromises(0)}

## Robocze 2.0.3 (nieopublikowane)

Dodano pierwszą wersję Fancy Journal do paczek 26.2 i 26.3. Dostępne stare logi potwierdzają uruchomienia w kontrolowanych światach, ale zawierają też błędy konfiguracji oraz brak pobieranych paczek zasobów w tamtym teście. Nie należy traktować ich jako potwierdzenia bieżącego wydania ani jego wydajności.
"""
    return {"README.md": readme, "docs/modrinth_description.md": pl, "docs/CHANGELOG.md": changelog, "docs/QUESTS.md": quest_catalogue(info)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime-check", action="append", choices=("server-26.2", "server-26.3", "client-26.2", "client-26.3"), default=[], help="name a check only after its successful completion; scope stays in CODEX_REVIEW.md")
    args = parser.parse_args(argv)
    constants = build_constants()
    info = {mc: pack_info(mc, constants["VERSION"]) for mc in ("26.2", "26.3")}
    documents = render_docs(constants, info, set(args.runtime_check))
    for filename, content in documents.items():
        atomic_write(ROOT / filename, content)
    print(f"Generated docs for {constants['VERSION']}; no publication performed.")


if __name__ == "__main__":
    main()
