---
description: Validate digitus-Dei plugin structure and configuration
allowed-tools: [Bash]
---

# /test - Validate Plugin

Run comprehensive validation of the digitus-Dei plugin.

## Usage

```
/test
```

## Process

Execute the validation script:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/test_plugin.py
```

## What It Checks

1. **Plugin Manifest** - plugin.json exists and has required fields
2. **Hooks Configuration** - hooks.json has correct structure
3. **Python Scripts** - All .py files compile without syntax errors
4. **Command Files** - All commands have YAML frontmatter
5. **User Config** - ~/.claude/digitus-Dei.local.md exists and is valid
6. **Registry Operations** - Can read/write to registry

## Output

Reports pass/fail for each check:
- ✓ = passed
- ✗ = failed (critical)
- ! = warning (non-critical)

## When to Run

- After updating the plugin
- After changing hooks or scripts
- When debugging issues
- Before pushing changes
