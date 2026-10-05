"""Build reproducible TEMPERED jars from editable src/tempered.

python tools/build_tempered.py --mc 26.2
python tools/build_tempered.py --mc 26.3 --vanilla-jar <official server jar>

The optional official jar check verifies every gated recipe and its advancement
guard against that Minecraft version. No downloads or Java compilation needed.
"""
import argparse
import hashlib
import io
import json
import re
import sys
import zipfile
from pathlib import Path, PurePosixPath

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tempered_legacy  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "tempered"
VERSION="2.19.0"
ERA_BONUSES = 9  # 3 by Codex + 6 more per era (tools/gen_more_quests.py)
EPILOG_ROOT = "tempered:bonus/epilog/root"
DATE = (2026, 1, 1, 0, 0, 0)
FORMATS = {"26.2": [107, 1], "26.3": [121, 0], "1.21.1": [48, 0], "1.21.4": [61, 0]}
LEGACY_MC = ("1.21.1", "1.21.4")
RESOURCE_FORMAT = {"1.21.1": 34, "1.21.4": 46}  # TEMPERED is both a data pack (FORMATS) and a resource pack (lang files)


def encode(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf8")


def source_entries():
    entries = {}
    for path in sorted(SOURCE.rglob("*")):
        if not path.is_file():
            continue
        name = path.relative_to(SOURCE).as_posix()
        rel = PurePosixPath(name)
        if rel.is_absolute() or ".." in rel.parts or "\\" in name or ":" in name:
            raise ValueError(f"Unsafe source path: {name}")
        entries[name] = path.read_bytes()
    if not entries:
        raise ValueError(f"No TEMPERED source files in {SOURCE}")
    return entries


def gated_recipes(entries):
    gated = {}
    for tier in range(2, 8):
        lock = entries[f"data/tempered/function/recipe/lock_{tier}.mcfunction"].decode("utf8")
        unlock = entries[f"data/tempered/function/recipe/unlock_{tier}.mcfunction"].decode("utf8")
        recipes = re.findall(r"^recipe take @s (minecraft:\S+)$", lock, re.M)
        unlocked = re.findall(r"^recipe give @a (minecraft:\S+)$", unlock, re.M)
        if set(recipes) != set(unlocked):
            raise ValueError(f"Era {tier} has different locked and unlocked recipes")
        for recipe in recipes:
            if recipe in gated:
                raise ValueError(f"Recipe appears in multiple eras: {recipe}")
            gated[recipe] = tier
    return gated


def bonus_for_mc(data, mc):
    """26.3 replaces context-predicate lists and recipe/potion trigger fields.

    Source keeps the verified 26.2 schema. Conversion applies to our 21 bonuses
    only; existing impossible advancements and hidden recipe guards are shared.
    """
    if mc == "26.2":
        return data
    data = json.loads(json.dumps(data))

    def predicate(value):
        if isinstance(value, list):
            terms = [predicate(term) for term in value]
            return terms[0] if len(terms) == 1 else {"type": "minecraft:all_of", "terms": terms}
        if isinstance(value, dict):
            converted = {}
            for key, member in value.items():
                if key == "condition":
                    converted["type"] = member
                elif key in ("term", "terms"):
                    converted[key] = ([predicate(term) for term in member]
                                      if isinstance(member, list) else predicate(member))
                else:
                    converted[key] = member
            return converted
        return value

    for criterion in data["criteria"].values():
        conditions = criterion.get("conditions", {})
        for field in ("player", "entity", "child", "parent", "partner", "location"):
            if field in conditions:
                conditions[field] = predicate(conditions[field])
        if criterion["trigger"] == "minecraft:recipe_crafted" and "recipe_id" in conditions:
            conditions["recipes"] = conditions.pop("recipe_id")
        if criterion["trigger"] == "minecraft:player_generates_container_loot" and "loot_table" in conditions:
            conditions["loot_tables"] = conditions.pop("loot_table")
        if criterion["trigger"] == "minecraft:brewed_potion" and isinstance(conditions.get("potion"), str):
            conditions["potion"] = {"potions": conditions["potion"]}
    return data


def validate_epilog(epilog):
    """The Epilog is a hidden optional branch: root unlocked by the Ender Dragon, quests gated by that root."""
    root = epilog.get("data/tempered/advancement/bonus/epilog/root.json")
    if not root or "parent" in root or not root["display"].get("hidden"):
        raise ValueError("Epilog root must exist, have no parent and stay hidden until unlocked")
    if set(root["criteria"]) != {"killed_dragon", "already_defeated"}:
        raise ValueError("Epilog root must unlock only through the Ender Dragon")
    quests = {n: d for n, d in epilog.items() if not n.endswith("/root.json")}
    if len(quests) < 30:
        raise ValueError(f"Expected at least 30 epilog quests, got {len(quests)}")
    expected_gate = [{"condition": "minecraft:entity_properties", "entity": "this",
                      "predicate": {"minecraft:type_specific/player": {"advancements": {EPILOG_ROOT: True}}}}]
    for name, data in quests.items():
        if data["parent"] != EPILOG_ROOT:
            raise ValueError(f"Epilog quest has the wrong parent: {name}")
        rewards = data.get("rewards", {})
        if set(rewards) != {"experience"} or not 25 <= rewards["experience"] <= 200:
            raise ValueError(f"Epilog reward must be personal XP between 25 and 200: {name}")
        for criterion in data["criteria"].values():
            gate = criterion.get("conditions", {}).get("player")
            if gate != expected_gate and not (isinstance(gate, list) and gate[-1:] == expected_gate):
                raise ValueError(f"Epilog criterion can count before the dragon is defeated: {name}")


def validate(entries, vanilla_jar=None):
    parsed = {name: json.loads(data) for name, data in entries.items()
              if name.endswith((".json", ".mcmeta"))}
    for name, content in entries.items():
        if not name.endswith(".mcfunction"):
            continue
        for function in re.findall(r"\bfunction tempered:([\w/]+)", content.decode("utf8")):
            target = f"data/tempered/function/{function}.mcfunction"
            if target not in entries:
                raise ValueError(f"Missing function {target} referenced by {name}")

    bonuses = {name: data for name, data in parsed.items()
               if name.startswith("data/tempered/advancement/bonus/")}
    epilog = {name: data for name, data in bonuses.items() if name.startswith("data/tempered/advancement/bonus/epilog/")}
    era_bonuses = {name: data for name, data in bonuses.items() if name not in epilog}
    if len(era_bonuses) != ERA_BONUSES * 7:
        raise ValueError(f"Expected {ERA_BONUSES * 7} personal optional era quests, got {len(era_bonuses)}")
    validate_epilog(epilog)
    for era in range(1, 8):
        prefix = f"data/tempered/advancement/bonus/{era}/"
        selected = {name: data for name, data in era_bonuses.items() if name.startswith(prefix)}
        if len(selected) != ERA_BONUSES:
            raise ValueError(f"Expected {ERA_BONUSES} optional quests in era {era}")
        for name, data in selected.items():
            if data["parent"] != f"tempered:age/{era}":
                raise ValueError(f"Bonus has the wrong era parent: {name}")
            rewards = data.get("rewards", {})
            if set(rewards) != {"experience"} or not 10 <= rewards["experience"] <= 30:
                raise ValueError(f"Bonus reward must be small personal XP: {name}")
            for criterion in data["criteria"].values():
                gate = criterion.get("conditions", {}).get("player")
                expected = [{"condition": "minecraft:entity_properties", "entity": "this",
                             "predicate": {"minecraft:type_specific/player": {
                                 "advancements": {f"tempered:age/{era}": True}}}}]
                if gate != expected:
                    raise ValueError(f"Bonus criterion can count before its era unlock: {name}")

    gated = gated_recipes(entries)
    guarded = set()
    guards = {}
    for name, advancement in parsed.items():
        if not name.startswith("data/minecraft/advancement/recipes/"):
            continue
        criteria = advancement["criteria"]
        if criteria != {"tempered_manual_unlock": {"trigger": "minecraft:impossible"}}:
            raise ValueError(f"Recipe guard can award automatically: {name}")
        recipes = advancement.get("rewards", {}).get("recipes", [])
        if not set(recipes).issubset(gated):
            raise ValueError(f"Guard modifies an ungated recipe: {name}")
        guarded.update(recipes)
        guards[name] = recipes
    if guarded != set(gated):
        raise ValueError(f"Missing vanilla unlock guards: {sorted(set(gated) - guarded)}")

    if vanilla_jar:
        with zipfile.ZipFile(vanilla_jar) as outer:
            nested = [name for name in outer.namelist()
                      if name.startswith("META-INF/versions/") and name.endswith(".jar")]
            if len(nested) != 1:
                raise ValueError("Expected one official nested Minecraft server jar")
            vanilla_bytes = outer.read(nested[0])
        with zipfile.ZipFile(io.BytesIO(vanilla_bytes)) as vanilla:
            for recipe in gated:
                recipe_path = f"data/minecraft/recipe/{recipe.split(':', 1)[1]}.json"
                if recipe_path not in vanilla.namelist():
                    raise ValueError(f"Unknown vanilla recipe: {recipe}")
            for name, rewards in guards.items():
                original = json.loads(vanilla.read(name))
                if original.get("rewards", {}).get("recipes", []) != rewards:
                    raise ValueError(f"Vanilla recipe advancement moved or changed: {name}")
            version = json.loads(vanilla.read("version.json"))["id"]
        print(f"Validated {len(gated)} recipe guards against official Minecraft {version}")
    return len(gated)


def build(mc, vanilla_jar=None):
    entries = source_entries()
    legacy = mc in LEGACY_MC
    if legacy:
        entries = tempered_legacy.prune(entries, mc)
    count = validate(entries, vanilla_jar)
    metadata = json.loads(entries["fabric.mod.json"])
    metadata["version"] = VERSION
    metadata["depends"]["minecraft"] = {"26.2": ">=26.2 <26.3", "26.3": ">=26.3 <26.4"}.get(mc, mc)
    if legacy:
        metadata["depends"]["fabricloader"] = ">=0.15.0"
    entries["fabric.mod.json"] = encode(metadata)
    pack = json.loads(entries["pack.mcmeta"])
    major, minor = FORMATS[mc]
    if legacy:
        # one pack.mcmeta serves both roles, and the two format numbers differ: accept the whole range between them
        low = RESOURCE_FORMAT[mc]
        pack["pack"] = {"description": pack["pack"]["description"], "pack_format": low,
                        "supported_formats": {"min_inclusive": low, "max_inclusive": major}}
    else:
        pack["pack"].update(pack_format=major, min_format=[major, minor], max_format=[major, minor])
    entries["pack.mcmeta"] = encode(pack)
    for name, content in list(entries.items()):
        if name.startswith("data/tempered/advancement/bonus/") and name.endswith(".json") and not legacy:
            entries[name] = encode(bonus_for_mc(json.loads(content), mc))
    if legacy:
        entries = tempered_legacy.convert(entries, mc)

    output = ROOT / "build" / "mods" / f"TEMPERED{VERSION}mc{mc}.jar"
    output.parent.mkdir(parents=True, exist_ok=True)
    memory = io.BytesIO()
    with zipfile.ZipFile(memory, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as jar:
        for name, content in sorted(entries.items()):
            info = zipfile.ZipInfo(name, DATE)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            jar.writestr(info, content)
    temporary = output.with_suffix(".jar.tmp")
    temporary.write_bytes(memory.getvalue())
    temporary.replace(output)
    digest = hashlib.sha256(memory.getvalue()).hexdigest()
    print(f"Built {output.name}: {len(entries)} entries, {count} guarded recipes, SHA256 {digest}")
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mc", choices=FORMATS, default="26.2")
    parser.add_argument("--vanilla-jar", type=Path)
    arguments = parser.parse_args()
    build(arguments.mc, arguments.vanilla_jar)
