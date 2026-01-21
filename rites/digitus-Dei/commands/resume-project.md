---
description: Resume a specific project by ID (deterministic selection)
allowed-tools: [Bash, Read, Write, Edit, AskUserQuestion, Skill]
---

# /resume-project - Resume Specific Project

Resume a specific project by ID in the current session.

## Usage

```
/resume-project <id>
```

## Process

### 1. Fetch Project

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/registry.py get {id}
```

**If not found:** Report error and suggest `/list-projects`.

### 2. Validate Status

**Allowed:** `in_progress`, `paused`, `idea`

**Not allowed:**
- `blocked` → Tell user to use `/vibesolve` or manually unblock
- `completed` → Cannot resume completed work
- `abandoned` → Must resurrect with `/project-status {id} idea` first

### 3. Check Lock

If `locked_by` is set, warn user and offer to unlock or cancel.

### 4. Gather Context

For `in_progress` or `paused` projects:
- Read README.md, DESIGN.md, CHANGELOG.md from project directory
- Summarize current state

### 5. Confirm with User

Present project details and ask:
- "Resume"
- "Cancel"

### 6. Initialize (if status is `idea`)

```bash
echo '{project_json}' | python3 ${CLAUDE_PLUGIN_ROOT}/scripts/project_utils.py init
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/project_utils.py github {project_dir}
echo '{"status": "in_progress", "started_at": "{ISO8601}", "repo_url": "{url}"}' | python3 ${CLAUDE_PLUGIN_ROOT}/scripts/registry.py update {id}
```

### 7. Lock Project

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/registry.py lock {id} "current-session"
```

### 8. Change to Project Directory

```bash
cd {project_dir}
```

### 9. Start Work

Use the Skill tool to invoke ralph-loop in the current session:

```
skill: "ralph-loop:ralph-loop"
args: "{project_spec} --completion-promise 'MVP complete with tests passing'"
```

The project spec from the registry becomes the ralph-loop prompt.

### 10. On Completion

When ralph-loop completes, unlock the project:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/registry.py unlock {id}
```
