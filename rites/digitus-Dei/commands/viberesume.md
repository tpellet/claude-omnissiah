---
description: Resume a paused or in-progress project by divine selection
allowed-tools: [Bash, Read, Write, Task, AskUserQuestion]
---

# /viberesume - Return to Unfinished Work

Let divine providence select an unfinished project to resume.

## Usage

```
/viberesume
```

## Process

### 1. Divine Selection

Select from in_progress or paused projects that are not locked:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/selector.py --status=in_progress,paused --unlocked
```

**If no projects available:**
```
No resumable projects available.

Possible reasons:
- All in-progress projects are locked by other workers
- No paused projects exist
- All projects are either ideas, blocked, or completed

Try `/vibestart` for a new project or `/vibesolve` for blocked ones.
```

### 2. Gather Context

**a) Get project directory:**
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/project_utils.py slugify "{title}"
```

**b) Read existing context:**
- `README.md` - Original specification
- `DESIGN.md` - Design decisions made
- `CHANGELOG.md` - Work completed
- Latest wrap-up (if paused)

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/project_utils.py get-wrap-up {project_dir}
```

### 3. Present the Chosen Work

```
## The Finger of God Returns To...

**{title}**

| Attribute | Value |
|-----------|-------|
| ID | {id} |
| Status | {status} |
| Started | {started_at} |
| Repository | {repo_url} |

### Last Session Summary

{wrap_up_content or "No wrap-up found - review CHANGELOG.md"}

### Recent Progress (from CHANGELOG.md)

{last few entries from CHANGELOG.md}

---

Resume this divine work?
```

Use AskUserQuestion:
- "Resume"
- "Choose another"
- "Cancel"

### 4. Launch

Launch in new tmux session, passing the project ID for automatic locking:

```bash
tmux new-session -d -s "digitus-{id}" -c "{project_dir}"
tmux send-keys -t "digitus-{id}" "DIGITUS_PROJECT_ID={id} claude --plugin-dir ${CLAUDE_PLUGIN_ROOT}/.. '/ralph-loop'" Enter
```

The SessionStart hook automatically locks the project using DIGITUS_PROJECT_ID.
When the session ends, the SessionEnd hook unlocks it.

### 5. Report Launch

```
## Divine Work Resumed

**Project:** {title}
**Directory:** {project_dir}
**Session:** digitus-{id}

Context provided to agent:
- Specification from README.md
- Design decisions from DESIGN.md
- Previous progress from CHANGELOG.md
- Last wrap-up summary (if available)

Monitor with `tmux attach -t digitus-{id}`

*The work continues.*
```

## Context Injection

The spawned agent receives this context at startup:

```markdown
# Resuming Project: {title}

## Specification
{README.md content}

## Design Decisions Made
{DESIGN.md content}

## Work Completed
{CHANGELOG.md content}

## Last Session Notes
{wrap-up content if available}

---

Continue the work. Maintain DESIGN.md and CHANGELOG.md as you progress.
```
