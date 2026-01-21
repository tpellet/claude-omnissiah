#!/usr/bin/env python3
"""Validate digitus-Dei plugin structure and functionality."""

import json
import subprocess
import sys
from pathlib import Path

# Colors for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def ok(msg: str) -> None:
    print(f"{GREEN}✓{RESET} {msg}")

def fail(msg: str) -> None:
    print(f"{RED}✗{RESET} {msg}")

def warn(msg: str) -> None:
    print(f"{YELLOW}!{RESET} {msg}")

def get_plugin_root() -> Path:
    """Get plugin root directory."""
    return Path(__file__).parent.parent

def check_hooks_json() -> bool:
    """Validate hooks.json structure."""
    hooks_path = get_plugin_root() / "hooks" / "hooks.json"

    if not hooks_path.exists():
        fail(f"hooks.json not found at {hooks_path}")
        return False

    try:
        with open(hooks_path) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        fail(f"hooks.json invalid JSON: {e}")
        return False

    # Check wrapper structure
    if "hooks" not in data:
        fail("hooks.json missing 'hooks' wrapper (plugin format requires it)")
        return False

    hooks = data["hooks"]
    valid_events = {"PreToolUse", "PostToolUse", "Stop", "SubagentStop",
                    "UserPromptSubmit", "SessionStart", "SessionEnd",
                    "PreCompact", "Notification"}

    for event in hooks:
        if event not in valid_events:
            warn(f"Unknown hook event: {event}")

        for hook_config in hooks[event]:
            if "matcher" not in hook_config:
                fail(f"Hook in {event} missing 'matcher' field")
                return False
            if "hooks" not in hook_config:
                fail(f"Hook in {event} missing 'hooks' array")
                return False

            for hook in hook_config["hooks"]:
                if "type" not in hook:
                    fail(f"Hook in {event} missing 'type' field")
                    return False
                if hook["type"] == "command" and "command" not in hook:
                    fail(f"Command hook in {event} missing 'command' field")
                    return False

    ok("hooks.json structure valid")
    return True

def check_python_scripts() -> bool:
    """Check all Python scripts compile."""
    scripts_dir = get_plugin_root() / "scripts"
    all_ok = True

    for script in scripts_dir.glob("*.py"):
        try:
            result = subprocess.run(
                [sys.executable, "-m", "py_compile", str(script)],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                fail(f"{script.name}: {result.stderr}")
                all_ok = False
            else:
                ok(f"{script.name} compiles")
        except Exception as e:
            fail(f"{script.name}: {e}")
            all_ok = False

    return all_ok

def check_plugin_json() -> bool:
    """Validate plugin.json manifest."""
    manifest_path = get_plugin_root() / ".claude-plugin" / "plugin.json"

    if not manifest_path.exists():
        fail(f"plugin.json not found at {manifest_path}")
        return False

    try:
        with open(manifest_path) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        fail(f"plugin.json invalid JSON: {e}")
        return False

    required = ["name", "description"]
    for field in required:
        if field not in data:
            fail(f"plugin.json missing required field: {field}")
            return False

    ok(f"plugin.json valid (v{data.get('version', 'unknown')})")
    return True

def check_commands() -> bool:
    """Check all command files exist and have frontmatter."""
    commands_dir = get_plugin_root() / "commands"
    all_ok = True
    count = 0

    for cmd in commands_dir.glob("*.md"):
        count += 1
        content = cmd.read_text()
        if not content.startswith("---"):
            warn(f"{cmd.name} missing YAML frontmatter")
        if "description:" not in content[:500]:
            warn(f"{cmd.name} missing description in frontmatter")

    if count == 0:
        fail("No command files found")
        return False

    ok(f"{count} command files found")
    return all_ok

def check_config() -> bool:
    """Check if config file exists."""
    config_path = Path.home() / ".claude" / "digitus-Dei.local.md"

    if not config_path.exists():
        warn(f"Config not found: {config_path}")
        warn("Run /initialize to set up")
        return True  # Not a failure, just a warning

    content = config_path.read_text()
    if "registry_dir:" not in content:
        fail("Config missing registry_dir setting")
        return False

    # Extract registry_dir
    for line in content.split("\n"):
        if line.startswith("registry_dir:"):
            registry_dir = Path(line.split(":", 1)[1].strip())
            if not registry_dir.exists():
                warn(f"Registry dir does not exist: {registry_dir}")
            elif not (registry_dir / ".digitus-registry.json").exists():
                warn(f"Registry file not found in {registry_dir}")
            else:
                ok(f"Config valid, registry at {registry_dir}")
            break

    return True

def check_registry_operations() -> bool:
    """Test basic registry operations."""
    try:
        from registry import RegistryManager, get_registry_dir

        try:
            registry_dir = get_registry_dir()
            manager = RegistryManager(registry_dir)
            projects = manager.list()
            ok(f"Registry accessible ({len(projects)} projects)")
            return True
        except FileNotFoundError:
            warn("Registry not initialized (run /initialize)")
            return True
        except Exception as e:
            fail(f"Registry error: {e}")
            return False
    except ImportError as e:
        fail(f"Cannot import registry module: {e}")
        return False

def main() -> int:
    """Run all checks and return exit code."""
    print("=" * 50)
    print("digitus-Dei Plugin Validation")
    print("=" * 50)
    print()

    checks = [
        ("Plugin Manifest", check_plugin_json),
        ("Hooks Configuration", check_hooks_json),
        ("Python Scripts", check_python_scripts),
        ("Command Files", check_commands),
        ("User Config", check_config),
    ]

    # Add registry check only if we're in the right directory
    scripts_dir = get_plugin_root() / "scripts"
    if scripts_dir.exists():
        sys.path.insert(0, str(scripts_dir))
        checks.append(("Registry Operations", check_registry_operations))

    all_passed = True
    for name, check_fn in checks:
        print(f"\n## {name}")
        try:
            if not check_fn():
                all_passed = False
        except Exception as e:
            fail(f"Check failed with exception: {e}")
            all_passed = False

    print()
    print("=" * 50)
    if all_passed:
        print(f"{GREEN}All checks passed!{RESET}")
        return 0
    else:
        print(f"{RED}Some checks failed.{RESET}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
