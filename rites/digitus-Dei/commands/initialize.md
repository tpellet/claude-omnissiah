---
description: Setup the Divine Registry location
allowed-tools: [Bash, AskUserQuestion]
---

# /initialize - Setup the Divine Registry

Configure where digitus-Dei stores projects.

## Process

### 1. Check Current State

```bash
cat ~/.claude/digitus-Dei.local.md 2>/dev/null
```

If configured, show current location and ask: "Keep current" or "Reconfigure".

### 2. Detect Default

```bash
for dir in ~/Projects ~/projects ~/code ~/Code ~/dev; do
  [ -d "$dir" ] && echo "$dir" && break
done
```

Use first found + `/.digitus-dei`, or `~/Projects/.digitus-dei` if none found.

### 3. Ask User

Use AskUserQuestion:
- "Use {detected}/.digitus-dei (Recommended)"
- "Use ~/Projects/.digitus-dei"
- "Custom location"

### 4. Create Config and Registry

```bash
mkdir -p ~/.claude
cat > ~/.claude/digitus-Dei.local.md << EOF
---
registry_dir: {chosen_path}
---
EOF
mkdir -p {chosen_path}
echo '[]' > {chosen_path}/.digitus-registry.json
```

### 5. Confirm

```
## Registry Initialized

**Location:** {chosen_path}

Next: `/new-project <brief>` to add your first project.
```
