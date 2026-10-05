"""Reads how TEMPERED's original quests are checked (data/tempered/function/check/*.mcfunction + the scoreboard
objectives in core/init.mcfunction) and turns it into data a client can show: what to get or do, and how much.

The original quests are `minecraft:impossible` advancements granted by functions, so the advancement JSON itself says
nothing about their goals. The result goes into the mod as assets/tempered/quest_specs.json:

  {"tempered:quest/2l": {"reqs": [{"kind": "have", "ids": ["minecraft:copper_ingot"], "need": 8}]},
   "tempered:quest/2f": {"reqs": [{"kind": "stat", "stats": ["minecraft.mined:minecraft.stone"], "need": 64}]},
   "tempered:quest/5b": {"reqs": [{"kind": "dimension", "id": "minecraft:the_nether", "need": 1}]}}

Quests whose check is anything else are left out (the client then shows only their description).
"""
import json
import re

OBJECTIVE = re.compile(r"^scoreboard objectives add tempered\.(\w+) (minecraft\.\S+)\s*$", re.M)
QUEST = re.compile(r"#q\.(\w+) tempered\.data matches 1")


def objectives(init_text):
    return {name: criterion for name, criterion in OBJECTIVE.findall(init_text)}


def build_specs(entries):
    """entries: {path inside the mod: bytes}. Returns the spec dictionary."""
    stats = objectives(entries["data/tempered/function/core/init.mcfunction"].decode("utf8"))
    specs = {}
    for name, content in sorted(entries.items()):
        if not (name.startswith("data/tempered/function/check/") and name.endswith(".mcfunction")):
            continue
        pending_have = {}   # quest -> item/tag cleared-for-count
        pending_sum = {}    # quest -> objectives added up in tempered.n
        for line in content.decode("utf8").splitlines():
            m = QUEST.search(line)
            if not m or "unless score" not in line:
                continue
            quest = m.group(1)
            have = re.search(r"store result score @s tempered\.n run clear @s (\S+) 0$", line)
            if have:
                pending_have[quest] = have.group(1)
                continue
            for source in re.findall(r"operation @s tempered\.n \+= @s tempered\.(\w+)$", line):
                pending_sum.setdefault(quest, []).append(source)
            dim = re.search(r"if dimension (\S+) run function tempered:quest/(\w+)$", line)
            if dim:
                specs[f"tempered:quest/{dim.group(2)[0]}/{dim.group(2)}"] = {"reqs": [{"kind": "dimension", "id": dim.group(1), "need": 1}]}
                continue
            goal = re.search(r"scores=\{tempered\.(\w+)=(\d+)\.\.\}\] run function tempered:quest/(\w+)$", line)
            if not goal:
                continue
            objective, need, target = goal.group(1), int(goal.group(2)), goal.group(3)
            key = f"tempered:quest/{target[0]}/{target}"
            if objective == "n" and target in pending_have:
                item = pending_have[target]
                specs[key] = {"reqs": [{"kind": "have", "ids": [item.replace("#", "#", 1)], "need": need}]}
            elif objective == "n" and target in pending_sum and all(s in stats for s in pending_sum[target]):
                specs[key] = {"reqs": [{"kind": "stat", "stats": [stats[s] for s in pending_sum[target]], "need": need}]}
            elif objective in stats:
                specs[key] = {"reqs": [{"kind": "stat", "stats": [stats[objective]], "need": need}]}
    return specs


def encode(specs):
    return (json.dumps(specs, ensure_ascii=False, indent=1, sort_keys=True) + "\n").encode("utf8")
