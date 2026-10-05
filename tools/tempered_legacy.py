"""Downgrades the TEMPERED source (written for Minecraft 26.2) to the data pack schema of Minecraft 1.21.x.

What differs for 1.21.1 / 1.21.4 (verified against the official server jars, see build_tempered.py --vanilla-jar):
- Copper tools/armour and all spears do not exist yet (added in 1.21.9 / 1.21.11): their recipes, recipe guards and
  tier-tag entries are removed. 1.21.1 also lacks the Creaking (one Epilogue quest is removed).
- Entity predicates were flattened in later versions: `minecraft:entity_type`, `minecraft:flags`, `minecraft:location`
  and `minecraft:type_specific/player` become `type`, `flags`, `location` and `type_specific: {type: player, ...}`;
  the location predicate field `structures` is still called `structure`.
- Advancement backgrounds are texture paths (`minecraft:textures/gui/advancements/backgrounds/<name>.png`).
- The gamerule is called `doLimitedCrafting`; chat click events use `clickEvent` with `value`.
"""
import json
import re

LEGACY = {
    # mc: (data pack format, extra removed ids)
    "1.21.1": (48, {"creaking", "creaking_heart"}),
    "1.21.4": (61, set()),
}

COPPER = ("axe", "boots", "chestplate", "helmet", "hoe", "leggings", "pickaxe", "shovel", "sword")
SPEARS = ("stone", "copper", "iron", "golden", "diamond", "netherite")


def removed_items(mc):
    items = {f"copper_{part}" for part in COPPER}
    items |= {f"{material}_spear" for material in SPEARS}
    items |= set(LEGACY[mc][1])
    return items


def _recipe_ids(items):
    """Recipe ids that belong to removed items: crafting recipes and the netherite smithing recipe of a spear."""
    ids = set(items)
    ids.add("netherite_spear_smithing")
    return ids


def prune(entries, mc):
    """Remove everything that refers to content missing in `mc`. Returns a new dict."""
    items = removed_items(mc)
    recipes = _recipe_ids(items)
    out = {}
    for name, data in entries.items():
        text = data.decode("utf8") if name.endswith((".json", ".mcfunction", ".mcmeta")) else None
        if name.startswith("data/minecraft/advancement/recipes/"):
            advancement = json.loads(text)
            if set(r.split(":", 1)[1] for r in advancement.get("rewards", {}).get("recipes", [])) & recipes:
                continue
        if name == "data/tempered/advancement/bonus/epilog/creaking_down.json" and "creaking" in items:
            continue
        if name.endswith(".mcfunction") and ("/recipe/lock_" in name or "/recipe/unlock_" in name):
            lines = [l for l in text.splitlines()
                     if not any(re.search(rf"minecraft:{re.escape(r)}\s*$", l) for r in recipes)]
            text = "\n".join(lines) + "\n"
        if name == "data/tempered/function/core/reset_bonus.mcfunction" and "creaking" in items:
            text = "\n".join(l for l in text.splitlines() if "creaking_down" not in l) + "\n"
        if name.startswith("data/tempered/tags/item/tier/") and name.endswith(".json"):
            tag = json.loads(text)
            tag["values"] = [v for v in tag["values"]
                             if (v["id"] if isinstance(v, dict) else v).split(":", 1)[1] not in items]
            text = json.dumps(tag, indent=2) + "\n"
        out[name] = text.encode("utf8") if text is not None else data
    return out


def _predicate(value):
    """Rewrite one entity predicate dictionary."""
    if not isinstance(value, dict):
        return value
    out = {}
    for key, member in value.items():
        if key == "minecraft:entity_type":
            out["type"] = member
        elif key == "minecraft:flags":
            out["flags"] = member
        elif key == "minecraft:location":
            location = dict(member)
            if "structures" in location:
                location["structure"] = location.pop("structures")
            out["location"] = location
        elif key.startswith("minecraft:type_specific/"):
            out["type_specific"] = {"type": "minecraft:" + key.split("/", 1)[1], **member}
        else:
            out[key] = member
    return out


def _walk(node):
    if isinstance(node, dict):
        if node.get("condition") == "minecraft:entity_properties" and isinstance(node.get("predicate"), dict):
            node["predicate"] = _predicate(node["predicate"])
        for key in list(node):
            if key == "background" and isinstance(node[key], str):
                name = node[key].split("backgrounds/", 1)[1]
                node[key] = f"minecraft:textures/gui/advancements/backgrounds/{name}.png"
            else:
                _walk(node[key])
    elif isinstance(node, list):
        for item in node:
            _walk(item)


CLICK = re.compile(r'"click_event"\s*:\s*\{\s*"action"\s*:\s*"(\w+)"\s*,\s*"command"\s*:\s*"((?:[^"\\]|\\.)*)"\s*\}')


def convert(entries, mc):
    """Schema conversion; run after validation (which expects the 26.2 schema)."""
    out = {}
    for name, data in entries.items():
        if name.endswith(".json") and name.startswith("data/") and "/tags/" not in name:
            node = json.loads(data)
            _walk(node)
            data = (json.dumps(node, ensure_ascii=False, indent=2) + "\n").encode("utf8")
        elif name.endswith(".mcfunction"):
            text = data.decode("utf8")
            text = text.replace("gamerule minecraft:limited_crafting", "gamerule doLimitedCrafting")
            text = CLICK.sub(lambda m: f'"clickEvent":{{"action":"{m.group(1)}","value":"{m.group(2)}"}}', text)
            data = text.encode("utf8")
        out[name] = data
    return out
