from contextlib import redirect_stdout
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("ecc_plugin_install", ROOT / "scripts/plugin_install.py")
plugins = importlib.util.module_from_spec(spec)
spec.loader.exec_module(plugins)


class NativeCodex:
    def __init__(self, installed=None, marketplaces=None, fail=None):
        self.installed = installed or []
        self.marketplaces = marketplaces or []
        self.calls = []
        self.fail = fail

    def __call__(self, args, **kwargs):
        self.calls.append(args)
        command = args[1:]
        data = ""
        if command == ["plugin", "list", "--json"]:
            data = json.dumps({"installed": self.installed, "available": []})
        elif command == ["plugin", "marketplace", "list", "--json"]:
            data = json.dumps({"marketplaces": self.marketplaces})
        elif command[:3] == ["plugin", "marketplace", "add"]:
            self.marketplaces.append({"name": "ecc-plugins", "root": command[3]})
        elif command[:2] == ["plugin", "add"]:
            if command[2] == self.fail:
                return subprocess.CompletedProcess(args, 7)
            self.installed.append({"pluginId": command[2], "installed": True, "enabled": True})
        else:
            raise AssertionError(args)
        return subprocess.CompletedProcess(args, 0, stdout=data, stderr="")

    @property
    def writes(self):
        return [c for c in self.calls if c[1:3] == ["plugin", "add"] or c[1:4] == ["plugin", "marketplace", "add"]]


class PluginTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="ecc plugins ")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name).resolve() / "источник с пробелами"
        bundle = self.root / "plugins/cc-skills"
        (bundle / ".codex-plugin").mkdir(parents=True)
        (bundle / "skills/example").mkdir(parents=True)
        (bundle / "skills/example/SKILL.md").write_text("---\nname: example\ndescription: Example skill\n---\n")
        (bundle / "LICENSE").write_text("MIT fixture")
        (bundle / ".codex-plugin/plugin.json").write_text(json.dumps({"name": "cc-skills", "skills": "./skills/"}))
        self.data = {"schema_version": 1, "plugins": [
            {"name": "cc-skills", "display_name": "CC Skills", "kind": "bundled", "observed": "installed-global-skills", "marketplace": "ecc-plugins", "path": "plugins/cc-skills"},
            {"name": "github", "display_name": "GitHub", "kind": "marketplace", "observed": "installed-connector", "marketplace": "openai-curated"},
            {"name": "documents", "display_name": "Documents", "kind": "host", "observed": "installed-cli"},
            {"name": "google-contacts", "display_name": "Google Contacts", "kind": "directory", "observed": "installed-connector", "url": "https://chatgpt.com/plugins"},
        ]}
        self.write_catalog()
        self.market = {"name": "ecc-plugins", "plugins": [{
            "name": "cc-skills", "source": {"source": "local", "path": "./plugins/cc-skills"},
            "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"}, "category": "Productivity",
        }]}
        (self.root / ".agents/plugins").mkdir(parents=True)
        self.write_market()

    def write_catalog(self):
        (self.root / "plugins/catalog.json").write_text(json.dumps(self.data))

    def write_market(self):
        (self.root / ".agents/plugins/marketplace.json").write_text(json.dumps(self.market))

    def run_plugins(self, names, runner=None, **kwargs):
        out = io.StringIO()
        with redirect_stdout(out):
            plugins.run_plugins(names, root=self.root, executable="codex-fixture", runner=runner, **kwargs)
        return out.getvalue()

    def test_listing_and_dry_run_work_without_cli_or_side_effects(self):
        native = NativeCodex()
        with redirect_stdout(io.StringIO()):
            plugins.show_catalog(self.root)
        before = sorted(str(p.relative_to(self.root)) for p in self.root.rglob("*"))
        self.run_plugins(["all"], runner=native, dry_run=True)
        self.assertEqual(native.calls, [])
        self.assertEqual(before, sorted(str(p.relative_to(self.root)) for p in self.root.rglob("*")))

    def test_install_uses_native_marketplace_and_argument_arrays(self):
        native = NativeCodex()
        self.run_plugins(["cc-skills", "github", "cc-skills"], native)
        self.assertEqual(native.writes, [
            ["codex-fixture", "plugin", "marketplace", "add", str(self.root)],
            ["codex-fixture", "plugin", "add", "cc-skills@ecc-plugins"],
            ["codex-fixture", "plugin", "add", "github@openai-curated"],
        ])

    def test_second_install_is_idempotent(self):
        native = NativeCodex()
        self.run_plugins(["all"], native)
        writes = list(native.writes)
        self.run_plugins(["all"], native)
        self.assertEqual(native.writes, writes)

    def test_existing_disabled_plugin_is_not_reenabled(self):
        native = NativeCodex(installed=[{"pluginId": "github@openai-curated", "installed": True, "enabled": False}])
        self.run_plugins(["github"], native)
        self.assertEqual(native.writes, [])
        self.assertFalse(native.installed[0]["enabled"])

    def test_existing_marketplace_is_reused(self):
        native = NativeCodex(marketplaces=[{"name": "ecc-plugins", "root": str(self.root)}])
        self.run_plugins(["cc-skills"], native)
        self.assertEqual(native.writes, [["codex-fixture", "plugin", "add", "cc-skills@ecc-plugins"]])

    def test_foreign_marketplace_is_rejected_before_any_install(self):
        native = NativeCodex(marketplaces=[{"name": "ecc-plugins", "root": str(self.root.parent / "foreign")}])
        with self.assertRaisesRegex(ValueError, "another checkout"):
            self.run_plugins(["github", "cc-skills"], native)
        self.assertEqual(native.writes, [])

    def test_unknown_plugin_rejected_before_subprocesses(self):
        native = NativeCodex()
        with self.assertRaisesRegex(ValueError, "Unknown plugins"):
            self.run_plugins(["cc-skills", "--malicious"], native)
        self.assertEqual(native.calls, [])

    def test_host_and_directory_plugins_do_not_run_native_commands(self):
        native = NativeCodex()
        self.run_plugins(["documents", "google-contacts"], native)
        self.assertEqual(native.calls, [])

    def test_bad_cli_json_cannot_trigger_install(self):
        calls = []
        def invalid(args, **kwargs):
            calls.append(args)
            return subprocess.CompletedProcess(args, 0, stdout="not json", stderr="")
        with self.assertRaisesRegex(ValueError, "invalid JSON"):
            self.run_plugins(["github"], invalid)
        self.assertEqual(len(calls), 1)

    def test_unknown_cli_record_shape_cannot_trigger_install(self):
        calls = []
        def outdated(args, **kwargs):
            calls.append(args)
            return subprocess.CompletedProcess(args, 0, stdout=json.dumps({"installed": [{"name": "github"}]}), stderr="")
        with self.assertRaisesRegex(ValueError, "Unsupported Codex plugin list format"):
            self.run_plugins(["github"], outdated)
        self.assertEqual(len(calls), 1)

    def test_partial_native_failure_stops_without_rollback(self):
        native = NativeCodex(fail="github@openai-curated")
        with self.assertRaisesRegex(ValueError, "Earlier successful native operations remain"):
            self.run_plugins(["cc-skills", "github"], native)
        self.assertEqual([p["pluginId"] for p in native.installed], ["cc-skills@ecc-plugins"])
        self.assertFalse(any("remove" in c for c in native.calls))

    def test_symlinked_or_unlicensed_bundle_is_rejected(self):
        license_path = self.root / "plugins/cc-skills/LICENSE"
        license_path.unlink()
        with self.assertRaisesRegex(ValueError, "license missing"):
            plugins.load_catalog(self.root)
        license_path.write_text("MIT fixture")
        (self.root / "plugins/cc-skills/secret").symlink_to(self.root.parent / "outside")
        with self.assertRaisesRegex(ValueError, "real files"):
            plugins.load_catalog(self.root)

    def test_catalog_cannot_escape_checkout(self):
        self.data["plugins"][0]["path"] = "../outside"
        self.write_catalog()
        with self.assertRaisesRegex(ValueError, "inside the checkout"):
            plugins.load_catalog(self.root)

    def test_marketplace_mismatch_and_duplicates_are_rejected(self):
        self.market["plugins"].append(dict(self.market["plugins"][0]))
        self.write_market()
        with self.assertRaisesRegex(ValueError, "Duplicate entries"):
            plugins.load_catalog(self.root)
        self.market["plugins"].pop()
        self.market["plugins"][0]["source"]["path"] = "./plugins/wrong"
        self.write_market()
        with self.assertRaisesRegex(ValueError, "disagrees"):
            plugins.load_catalog(self.root)

    def test_skill_and_plugin_scopes_cannot_be_mixed(self):
        for arguments in [["--profile", "core"], ["--project", str(self.root)], ["--dest", str(self.root)], ["--uninstall"], ["--list"]]:
            result = subprocess.run([sys.executable, str(ROOT / "scripts/install.py"), "--plugins", "cc-skills", *arguments], capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
            self.assertIn("Plugin mode cannot be combined", result.stderr)


if __name__ == "__main__":
    unittest.main()
