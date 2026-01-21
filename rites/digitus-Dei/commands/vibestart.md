---
description: Divine selection of a new project - The Finger of God points
allowed-tools: [Bash, Read, Write, Edit, AskUserQuestion, Skill]
---

# /vibestart - The Finger of God Points

Randomly select an unstarted project (weighted by priority) and begin work in the current session.

## Usage

```
/vibestart
```

## Process

### 1. Divine Selection

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/selector.py --status=idea
```

**If no projects:** Tell user to add one with `/new-project <brief>`.

### 2. Present the Chosen Work

Display project details:
- Title, ID, priority, tech stack
- Full specification

Ask user:
- "Accept and begin"
- "Choose another" (re-roll)
- "Cancel"

### 3. Initialize Project

On acceptance:

```bash
# Create directory structure
echo '{project_json}' | python3 ${CLAUDE_PLUGIN_ROOT}/scripts/project_utils.py init

# Create GitHub repo
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/project_utils.py github {project_dir}

# Update registry
echo '{"status": "in_progress", "started_at": "{ISO8601}", "repo_url": "{url}"}' | python3 ${CLAUDE_PLUGIN_ROOT}/scripts/registry.py update {id}
```

### 4. Lock Project

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/registry.py lock {id} "current-session"
```

### 5. Change to Project Directory

```bash
cd {project_dir}
```

### 6. Start Work

Use the Skill tool to invoke ralph-loop:

```
skill: "ralph-loop:ralph-loop"
args: "{project_spec} --completion-promise 'MVP complete with tests passing'"
```

### 7. On Completion

Unlock the project:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/registry.py unlock {id}
```
