"""Regression checks for Fabric version predicates and actual Loader builtins."""
import io
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools import check_deps as deps


def jar(metadata, nested=None):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("fabric.mod.json", json.dumps(dict(schemaVersion=1, **metadata)))
        for name, content in (nested or {}).items():
            archive.writestr(name, content)
    return buffer.getvalue()


class FabricVersionTests(unittest.TestCase):
    def test_real_fzzy_build_suffix_is_ignored_for_ordering(self):
        version = "0.7.7+fix3+26.3"
        self.assertEqual(deps.semantic(version), ((0, 7, 7), None))
        self.assertTrue(deps.matches(version, ">=0.7.6 <0.8"))
        self.assertEqual(deps.compare(version, "0.7.7+different metadata+*"), 0)
        self.assertFalse(deps.matches(version, ">=0.7.8"))

    def test_build_metadata_never_becomes_wildcard(self):
        self.assertFalse(deps.matches("1.3.0", "1.2.3+build.x"))
        self.assertTrue(deps.matches("1.2.3+other", "1.2.3+build.x"))
        self.assertTrue(deps.matches("1.2.3", "1.2.3+build,arbitrary|+text"))
        with self.assertRaises(deps.PredicateError):
            deps.matches("1.2.3", ">=1.2.x")

    def test_semver_prerelease_order_and_padding(self):
        ordered = ["1.0.0-", "1.0.0-alpha", "1.0.0-alpha.1", "1.0.0-alpha.beta",
                   "1.0.0-beta", "1.0.0-beta.2", "1.0.0-beta.11", "1.0.0-rc.1", "1.0.0"]
        for a, b in zip(ordered, ordered[1:]):
            with self.subTest(a=a, b=b):
                self.assertLess(deps.compare(a, b), 0)
        self.assertEqual(deps.compare("1.2", "1.2.0.0"), 0)
        self.assertLess(deps.compare("1.0-", "1.0-0"), 0)
        self.assertEqual(deps.compare("01.002", "1.2"), 0)  # Fabric superset.

    def test_long_prerelease_numbers_do_not_overflow(self):
        self.assertLess(deps.compare("1.0-" + "9" * 5000, "1.0-1" + "0" * 5000), 0)
        self.assertIsNone(deps.semantic("2147483648.0"))  # Java int core limit.
        self.assertIsNone(deps.semantic("1.0-alpha..1"))

    def test_ranges_and_invalid_metadata_keep_failure_checks(self):
        self.assertTrue(deps.matches("0.9", "^0.2"))  # Fabric has no special major-zero rule.
        self.assertFalse(deps.matches("1.0", "^0.2"))
        self.assertTrue(deps.matches("1.2.99", "~1.2.0"))
        self.assertFalse(deps.matches("1.3", "~1.2.0"))
        self.assertTrue(deps.matches("1.2-alpha", "1.2.x"))
        self.assertFalse(deps.matches("1.3", "1.2.x"))
        self.assertTrue(deps.matches("2.1", ["<1", ">=2 <3"]))
        with self.assertRaises(deps.PredicateError):
            deps.matches("release", ">release")
        with self.assertRaises(deps.PredicateError):
            deps.matches("1.2", ["*", "1.2 || 2.0"])
        with self.assertRaises(deps.PredicateError):
            deps.matches("1.2", [])


class LoaderBuiltinTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.mods = self.root / "mods"
        self.mods.mkdir()
        nested = jar({"id": "mixinextras", "version": "0.5.5", "provides": ["com_github_llamalad7_mixinextras"],
                      "depends": {"fabricloader": ">=0.14.25"}})
        self.loader = self.root / "fabric-loader-0.19.5.jar"
        self.loader.write_bytes(jar({"id": "fabricloader", "version": "0.19.5", "jars": [{"file": "META-INF/jars/mixinextras-fabric-0.5.5.jar"}]},
                                   {"META-INF/jars/mixinextras-fabric-0.5.5.jar": nested}))
        older = jar({"id": "mixinextras", "version": "0.5.4"})
        self.consumer = self.mods / "consumer.jar"
        self.consumer.write_bytes(jar({"id": "consumer", "version": "1.0", "jars": [{"file": "older.jar"}],
                                       "depends": {"mixinextras": ">=0.5.5", "com_github_llamalad7_mixinextras": ">=0.5.5", "java": ">=25"}},
                                      {"older.jar": older}))

    def tearDown(self):
        self.temporary.cleanup()

    def test_actual_nested_builtin_and_alias_resolve_both_sides(self):
        for side in ("client", "server"):
            with self.subTest(side=side):
                result = deps.audit(self.mods, side, loader_jar=self.loader)
                self.assertEqual(result["errors"], [])
                self.assertIn("highest 0.5.5", " ".join(result["warnings"]))
        with patch.object(deps, "find_loader_jar", return_value=None):
            without_loader = deps.audit(self.mods, "client")
        self.assertTrue(any("DEPENDENCY" in e for e in without_loader["errors"]))

    def test_wrong_loader_and_missing_declared_library_fail(self):
        wrong_version = deps.audit(self.mods, "client", loader="0.19.4", loader_jar=self.loader)
        self.assertTrue(any("does not match" in e for e in wrong_version["errors"]))
        self.loader.write_bytes(jar({"id": "fabricloader", "version": "0.19.5", "jars": [{"file": "missing.jar"}]}))
        result = deps.audit(self.mods, "server", loader_jar=self.loader)
        self.assertTrue(any("Declared nested jar missing" in e for e in result["errors"]))

    def test_real_version_java_and_breaks_errors_still_fail(self):
        self.consumer.write_bytes(jar({"id": "consumer", "version": "1", "depends": {"mixinextras": ">=0.6", "java": ">=26"},
                                       "breaks": {"mixinextras": ">=0.5.5"}}))
        result = deps.audit(self.mods, "client", loader_jar=self.loader)
        self.assertEqual(sum("DEPENDENCY" in e for e in result["errors"]), 2)
        self.assertEqual(sum("BREAKS" in e for e in result["errors"]), 1)

    def test_client_only_mod_does_not_supply_server_dependency(self):
        self.consumer.write_bytes(jar({"id": "consumer", "version": "1", "depends": {"clientlib": "*"}}))
        (self.mods / "clientlib.jar").write_bytes(jar({"id": "clientlib", "version": "1", "environment": "client"}))
        self.assertEqual(deps.audit(self.mods, "client", loader_jar=self.loader)["errors"], [])
        result = deps.audit(self.mods, "server", loader_jar=self.loader)
        self.assertTrue(any("clientlib" in e for e in result["errors"]))

    def test_manifest_selects_minecraft_version_and_hashes_are_checked(self):
        self.consumer.write_bytes(jar({"id": "consumer", "version": "1", "depends": {"minecraft": "26.3", "fabricloader": "0.19.5"}}))
        content = self.consumer.read_bytes()
        manifest = {"dependencies": {"minecraft": "26.3", "fabric-loader": "0.19.5"},
                    "files": [{"path": "mods/consumer.jar", "fileSize": len(content),
                               "hashes": {"sha512": hashlib.sha512(content).hexdigest()},
                               "env": {"client": "required", "server": "required"}}]}
        result = deps.audit(self.mods, "client", manifest, minecraft="26.2", loader="0.19.4", loader_jar=self.loader)
        self.assertEqual(result["errors"], [])
        manifest["files"][0]["hashes"]["sha512"] = "0" * 128
        result = deps.audit(self.mods, "client", manifest, loader_jar=self.loader)
        self.assertTrue(any("hash" in error.lower() for error in result["errors"]))

    def test_side_environment_does_not_require_or_scan_unsupported_jar(self):
        self.consumer.write_bytes(jar({"id": "consumer", "version": "1"}))
        (self.mods / "clientlib.jar").write_bytes(b"intentionally not a valid jar")
        manifest = {"files": [{"path": "mods/clientlib.jar", "fileSize": 1,
                               "hashes": {"sha512": "0" * 128},
                               "env": {"client": "required", "server": "unsupported"}}]}
        self.assertEqual(deps.audit(self.mods, "server", manifest, loader_jar=self.loader)["errors"], [])
        self.assertTrue(deps.audit(self.mods, "client", manifest, loader_jar=self.loader)["errors"])


if __name__ == "__main__":
    unittest.main()
