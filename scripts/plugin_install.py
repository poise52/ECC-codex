#!/usr/bin/env python3
"""Install optional plugins through Codex's native plugin manager."""

import json
from pathlib import Path
import re
import shlex
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
KINDS = {"bundled", "marketplace", "host", "directory"}


def load_catalog(root=ROOT):
    data = json.loads((root / "plugins/catalog.json").read_text(encoding="utf-8"))
    if data.get("schema_version") != 1:
        raise ValueError("Unsupported plugin catalog version")
    plugins = {}
    marketplace = json.loads((root / ".agents/plugins/marketplace.json").read_text(encoding="utf-8"))
    entries = {entry["name"]: entry for entry in marketplace["plugins"]}
    if len(entries) != len(marketplace["plugins"]):
        raise ValueError("Duplicate entries in local plugin marketplace")
    bundled = set()
    for item in data["plugins"]:
        name, kind = item["name"], item["kind"]
        if not isinstance(name, str) or not SLUG.fullmatch(name) or name in plugins:
            raise ValueError(f"Invalid or duplicate plugin name: {name}")
        if kind not in KINDS:
            raise ValueError(f"Unsupported plugin kind: {kind}")
        if kind in {"bundled", "marketplace"}:
            market = item["marketplace"]
            if not isinstance(market, str) or not SLUG.fullmatch(market):
                raise ValueError(f"Invalid marketplace for {name}")
        if kind == "bundled":
            relative = Path(item["path"])
            path = root / relative
            if relative.is_absolute() or ".." in relative.parts or path.is_symlink():
                raise ValueError(f"Plugin must remain inside the checkout: {name}")
            if (not path.resolve().is_relative_to(root.resolve()) or
                    not path.resolve().is_relative_to((root / "plugins").resolve())):
                raise ValueError(f"Plugin must remain inside plugins/: {name}")
            if any(p.is_symlink() for p in path.rglob("*")):
                raise ValueError(f"Bundled plugin resources must be real files: {name}")
            manifest = json.loads((path / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
            if manifest.get("name") != name or manifest.get("skills") != "./skills/":
                raise ValueError(f"Invalid bundled skill plugin: {name}")
            if not (path / "LICENSE").is_file():
                raise ValueError(f"Bundled plugin license missing: {name}")
            if not list((path / "skills").glob("*/SKILL.md")):
                raise ValueError(f"Bundled plugin has no skills: {name}")
            entry = entries.get(name, {})
            if (item["marketplace"] != marketplace["name"] or
                    entry.get("source") != {"source": "local", "path": "./" + relative.as_posix()} or
                    entry.get("policy", {}).get("installation") != "AVAILABLE" or
                    entry.get("policy", {}).get("authentication") != "ON_INSTALL" or
                    not entry.get("category")):
                raise ValueError(f"Marketplace entry disagrees with plugin catalog: {name}")
            bundled.add(name)
        plugins[name] = item
    if set(entries) != bundled:
        raise ValueError("Local marketplace must contain exactly the bundled plugins")
    return plugins


def show_catalog(root=ROOT):
    for item in load_catalog(root).values():
        print(f"{item['name']}: {item['display_name']} [{item['kind']}; {item['observed']}]")
    print("bundled = included in ECC; marketplace = downloaded by Codex; "
          "host = supplied by the app; directory = connect through Plugins.")


def select(names, catalog):
    unknown = set(names) - catalog.keys() - {"all"}
    if unknown:
        raise ValueError(f"Unknown plugins: {', '.join(sorted(unknown))}; use --list-plugins")
    selected = sorted(catalog) if "all" in names else list(dict.fromkeys(names))
    return [catalog[name] for name in selected]


def selector(item):
    return item["name"] + "@" + item["marketplace"]


def print_command(args):
    print("  " + " ".join(shlex.quote(str(arg)) for arg in args), flush=True)


def read_json(args, runner):
    result = runner(args, capture_output=True, text=True)
    if result.returncode:
        raise ValueError(f"Codex could not inspect plugins: {result.stderr.strip()[:2000]}")
    try:
        return json.loads(result.stdout)
    except ValueError as error:
        raise ValueError("Codex returned invalid JSON; update to a CLI with native plugin commands") from error


def run_plugins(names, dry_run=False, root=ROOT, runner=None, executable=None):
    catalog = load_catalog(root)
    selected = select(names, catalog)
    runner = runner or subprocess.run
    installable = []
    for item in selected:
        if item["kind"] == "host":
            print(f"host: {item['name']} — supplied by a supported Codex/ChatGPT runtime")
        elif item["kind"] == "directory":
            print(f"connect: {item['display_name']} — {item['url']}")
        else:
            installable.append(item)
    if not installable:
        return
    if dry_run:
        if any(p["kind"] == "bundled" for p in installable):
            print_command(["codex", "plugin", "marketplace", "add", str(root)])
        for item in installable:
            print_command(["codex", "plugin", "add", selector(item)])
        print("Dry run: no commands executed. Actual installation skips plugins already installed.")
        return
    executable = executable or shutil.which("codex")
    if not executable:
        raise ValueError("Codex CLI not found. Use --dry-run for commands or install via the Plugins UI.")
    state = read_json([executable, "plugin", "list", "--json"], runner)
    installed = state.get("installed")
    if (not isinstance(installed, list) or
            any(not isinstance(p, dict) or not isinstance(p.get("pluginId"), str) or
                not isinstance(p.get("installed"), bool) for p in installed)):
        raise ValueError("Unsupported Codex plugin list format; expected an 'installed' array")
    existing = {p.get("pluginId") for p in installed if p.get("installed") is True}
    pending = []
    for item in installable:
        if selector(item) in existing:
            print(f"keep: {selector(item)} (existing enabled/disabled preference preserved)")
        else:
            pending.append(item)
    bundled = [p for p in pending if p["kind"] == "bundled"]
    register = False
    if bundled:
        state = read_json([executable, "plugin", "marketplace", "list", "--json"], runner)
        markets = state.get("marketplaces")
        if (not isinstance(markets, list) or
                any(not isinstance(m, dict) or not isinstance(m.get("name"), str) for m in markets)):
            raise ValueError("Unsupported Codex marketplace list format")
        market_name = bundled[0]["marketplace"]
        current = [m for m in markets if m.get("name") == market_name]
        if len(current) > 1:
            raise ValueError(f"Ambiguous existing marketplace: {market_name}")
        if current:
            location = current[0].get("root")
            if not location or Path(location).resolve() != root.resolve():
                raise ValueError(f"Marketplace {market_name} already points to another checkout; "
                                 "review it with 'codex plugin marketplace list' before changing it")
        else:
            register = True
    commands = []
    if register:
        commands.append([executable, "plugin", "marketplace", "add", str(root)])
    commands.extend([executable, "plugin", "add", selector(item)] for item in pending)
    completed = []
    for args in commands:
        print_command(args)
        result = runner(args)
        if result.returncode:
            previous = "; ".join(completed) or "none"
            raise ValueError(f"Codex command failed ({result.returncode}). Completed commands: {previous}. "
                             "Earlier successful native operations remain in place; no automatic uninstall was attempted.")
        completed.append(" ".join(args[1:]))
    print("Plugin installation finished. Complete any requested account connection in Codex. "
          "Start a new chat if the plugin does not appear.")
