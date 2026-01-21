---
description: Resume a specific project by ID (deterministic selection)
allowed-tools: [Bash, Read, Write, Task, AskUserQuestion]
---

# /resume-project - Return to Specific Divine Work

Resume a specific project by ID, bypassing divine random selection.

## Usage

```
/resume-project <id>
```

## Process

### 1. Fetch Project

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/registry.py get {id}
```

**If not found:**
```
Project with ID "{id}" not found in the registry.

Use `/list-projects` to see available projects.
```

### 2. Validate Status

**Allowed statuses for resumption:**
- `in_progress` - Continue work
- `paused` - Resume from pause
- `idea` - Start the project (like vibestart but deterministic)

**Not allowed:**
- `blocked` - Must use `/vibesolve` or resolve manually first
- `completed` - Cannot resume completed work
- `abandoned` - Must resurrect first with `/project-status {id} idea`

**If blocked:**
```
Project "{title}" is blocked and cannot be resumed directly.

**Blocker:** {blocked_reason}

Options:
- `/vibesolve` - Auto-solve with divine intervention
- `/project-status {id} in_progress` - Manually unblock (if resolved)
```

**If completed:**
```
Project "{title}" is already completed.

Completed on: {completed_at}
Repository: {repo_url}

A completed work cannot be resumed. Consider starting a new iteration as a separate project.
```

**If abandoned:**
```
Project "{title}" has been abandoned.

To resurrect it, run:
`/project-status {id} idea`

Then you can start it with `/vibestart` or `/resume-project {id}`.
```

### 3. Check Lock Status

```bash
# Project JSON includes locked_by field
```

**If locked:**
```
Project "{title}" is currently locked by another worker.

**Locked by:** {locked_by}
**Since:** {locked_at}

Wait for the other worker to finish, or manually unlock with:
`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/registry.py unlock {id}`
```

### 4. Gather Context

Same as `/viberesume`:
- Read README.md, DESIGN.md, CHANGELOG.md
- Get latest wrap-up if paused
- Summarize recent progress

### 5. Present and Confirm

```
## Resuming Divine Work

**{title}**

| Attribute | Value |
|-----------|-------|
| ID | {id} |
| Status | {status} |
| Started | {started_at} |
| Repository | {repo_url} |

### Context

{wrap_up or recent CHANGELOG entries}

---

Resume this work?
```

Use AskUserQuestion:
- "Resume"
- "Cancel"

### 6. Lock and Launch

**a) If status is `idea`, initialize first:**
```bash
echo '{project_json}' | python3 ${CLAUDE_PLUGIN_ROOT}/scripts/project_utils.py init
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/project_utils.py github {project_dir}
echo '{"status": "in_progress", "started_at": "{ISO8601}"}' | python3 ${CLAUDE_PLUGIN_ROOT}/scripts/registry.py update {id}
```

**b) Lock the project:**
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/registry.py lock {id} {session_id}
```

**c) Launch in tmux:**
```bash
tmux new-session -d -s "digitus-{id}" -c "{project_dir}"
tmux send-keys -t "digitus-{id}" "DIGITUS_PROJECT_ID={id} claude '/ralph-loop'" Enter
```

### 7. Report

```
## Divine Work Resumed

**Project:** {title}
**Directory:** {project_dir}
**Session:** digitus-{id}

Monitor with `tmux attach -t digitus-{id}`

*By your will, the work continues.*
```

## Difference from /viberesume

| Aspect | /viberesume | /resume-project |
|--------|-------------|-----------------|
| Selection | Random (weighted) | Deterministic (by ID) |
| Use case | "Give me something to work on" | "I want to work on this specific project" |
| Status filter | in_progress, paused only | in_progress, paused, idea |
