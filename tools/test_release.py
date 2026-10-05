"""Regression checks against BOTH finished mrpack artifacts (no network)."""
import hashlib
import io
import json
from pathlib import Path
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
import re
_BUILD = (ROOT / "tools" / "build.py").read_text(encoding="utf8")
PACK_VERSION = re.search(r'^VERSION = "([^"]+)"', _BUILD, re.M).group(1)
JOURNAL_VERSION = re.search(r'^JOURNAL_VERSION = "([^"]+)"', _BUILD, re.M).group(1)
TEMPERED_VERSION = re.search(r'^TEMPERED_JAR = "TEMPERED([^"]+)mc26\.2\.jar"', _BUILD, re.M).group(1)


class ReleaseChecks(unittest.TestCase):
    def test_format_minor_semantics(self):
        if __package__:
            from .annotate_resources import bound
        else:
            from annotate_resources import bound
        self.assertEqual(bound(97), [97, 0])
        self.assertEqual(bound(97, True), [97, 2147483647])
        self.assertEqual(bound([97, 0], True), [97, 0])
        with self.assertRaises(ValueError):
            bound([97.1, 3], True)

    def test_finished_artifacts(self):
        for mc in ("26.2", "26.3"):
            with self.subTest(mc=mc):
                name = f"Fancy Vanilla {PACK_VERSION} for {mc}.mrpack"
                path = ROOT / "releases" / mc / name
                self.assertEqual(hashlib.sha512(path.read_bytes()).hexdigest(), path.with_suffix(".mrpack.sha512").read_text().split()[0])
                with zipfile.ZipFile(path) as pack:
                    self.assertIsNone(pack.testzip())
                    names = pack.namelist()
                    self.assertEqual(len(names), len(set(n.casefold() for n in names)))
                    index = json.loads(pack.read("modrinth.index.json"))
                    self.assertEqual(index["dependencies"]["minecraft"], mc)
                    files = index["files"]
                    self.assertEqual(len(files), len(set(f["path"].casefold() for f in files)))
                    bundled = [n for n in names if n.startswith("overrides/mods/")]
                    self.assertEqual(len(bundled), 2)
                    for jar_name in bundled:
                        jar_bytes = pack.read(jar_name)
                        with zipfile.ZipFile(io.BytesIO(jar_bytes)) as jar:
                            self.assertIsNone(jar.testzip())
                            metadata = json.loads(jar.read("fabric.mod.json"))
                            if metadata["id"] == "fancy_journal":
                                self.assertEqual(metadata["version"], f"{JOURNAL_VERSION}+mc{mc}")
                                self.assertEqual(metadata["depends"]["minecraft"], mc)
                                self.assertEqual(metadata["environment"], "client")
                            else:
                                self.assertEqual(metadata["id"].lower(), "tempered")
                                self.assertEqual(metadata["version"], TEMPERED_VERSION)
                                self.assertEqual(json.loads(jar.read("pack.mcmeta"))["pack"]["min_format"], [107, 1] if mc == "26.2" else [121, 0])
                                dimensions = [jar.read(f"data/tempered/function/check/{age}.mcfunction").decode() for age in (5, 6)]
                                self.assertTrue(all("as @a at @s if dimension" in f for f in dimensions))
                                locks = jar.read("data/tempered/function/core/locks.mcfunction").decode()
                                self.assertIn("execute as @a run scoreboard players operation @s tempered.lock = @s tempered.lockn", locks)
                                guards = [n for n in jar.namelist() if n.startswith("data/minecraft/advancement/recipes/")]
                                self.assertEqual(len(guards), 83)
                                optional = [n for n in jar.namelist() if n.startswith("data/tempered/advancement/bonus/") and n.endswith(".json")]
                                epilog = [n for n in optional if "/bonus/epilog/" in n]
                                era_quests = [n for n in optional if n not in epilog]
                                self.assertEqual(len(era_quests), 63)
                                for age in range(1, 8):
                                    self.assertEqual(sum(n.startswith(f"data/tempered/advancement/bonus/{age}/") for n in era_quests), 9)
                                for name in era_quests:
                                    goal = json.loads(jar.read(name))
                                    self.assertEqual(goal["parent"], f"tempered:age/{name.split('/')[4]}")
                                    self.assertLessEqual(goal["rewards"]["experience"], 30)
                                # Epilog: hidden root unlocked only by the Ender Dragon, quests gated by that root
                                root = json.loads(jar.read("data/tempered/advancement/bonus/epilog/root.json"))
                                self.assertTrue(root["display"]["hidden"])
                                self.assertNotIn("parent", root)
                                self.assertEqual(set(root["criteria"]), {"killed_dragon", "already_defeated"})
                                self.assertGreaterEqual(len(epilog) - 1, 30)
                                for name in epilog:
                                    if name.endswith("/root.json"):
                                        continue
                                    goal = json.loads(jar.read(name))
                                    self.assertEqual(goal["parent"], "tempered:bonus/epilog/root")
                                    self.assertTrue(25 <= goal["rewards"]["experience"] <= 200, name)
                                reset = jar.read("data/tempered/function/core/reset_bonus.mcfunction").decode()
                                for name in optional:
                                    if not name.endswith("/root.json"):
                                        quest_id = name[len("data/tempered/advancement/"):-len(".json")]
                                        self.assertIn(f"advancement revoke @s only tempered:{quest_id}", reset, name)
                                original = ROOT / "inputs" / "TEMPERED-2.16.0-baseline.jar"
                                with zipfile.ZipFile(original) as baseline:
                                    quests = [n for n in baseline.namelist() if n.startswith("data/tempered/advancement/quest/") and n.endswith(".json")]
                                    self.assertEqual(len(quests), 89)
                                    for name in quests:
                                        self.assertEqual(jar.read(name), baseline.read(name), name)
                                    rewards = [n for n in baseline.namelist() if n.startswith("data/tempered/function/quest/") and n.endswith(".mcfunction")]
                                    for name in rewards:
                                        self.assertEqual(jar.read(name), baseline.read(name), name)
                    options = dict(line.split(":", 1) for line in pack.read("overrides/options.txt").decode().splitlines() if ":" in line)
                    selected = json.loads(options["resourcePacks"])
                    self.assertEqual(len(selected), len(set(selected)))
                    available = {"file/" + Path(f["path"]).name for f in files if f["path"].startswith("resourcepacks/")}
                    available.add("file/FancyVanilla.zip")
                    self.assertEqual({p for p in selected if p.startswith("file/")}, available)
                    self.assertEqual(selected[-1], "file/FancyVanilla.zip")
                    self.assertEqual(json.loads(options["incompatibleResourcePacks"]), ["file/Clearer Slot Highlight.zip"])
                    clearer = selected.index("file/Clearer Slot Highlight.zip")
                    self.assertLess(next(i for i, p in enumerate(selected) if "Recolourful" in p), clearer)
                    self.assertEqual(options["key_chloride.zoom"], "key.keyboard.unknown")
                    self.assertEqual(options["key_zoomify.key.zoom"], "key.keyboard.c")
                    modern = pack.read("overrides/config/modernfix-mixins.properties").decode()
                    self.assertIn("mixin.perf.clear_mixin_classinfo=false", modern)
                    self.assertIn("mixin.perf.dynamic_entity_renderers=false", modern)
                    if mc == "26.2":
                        self.assertIn('cullingBehavior = "BOUNDING_BOX"', pack.read("overrides/config/particle_core_config.toml").decode())
                    else:
                        self.assertNotIn("overrides/config/chloride-client.toml", names)
                        font = next(f for f in files if "qrafty" in f["path"])
                        self.assertIn("-4.0.zip", font["path"])


if __name__ == "__main__":
    unittest.main()
