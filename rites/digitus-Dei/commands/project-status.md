---
description: Check or update the status of a project
allowed-tools: [Bash, Read, Write, AskUserQuestion]
---

# /project-status - Divine Work Status

View detailed status or update the status of a project.

## Usage

```
/project-status                    # Status of project in current directory
/project-status <id>               # View detailed status
/project-status <id> <new-status>  # Update status
```

**Valid statuses:** `idea`, `in_progress`, `paused`, `blocked`, `abandoned`, `completed`

## Process

### View Status (no new-status argument)

**1. Get project:**
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/registry.py get {id}
```

**2. Display detailed view:**
```
## Divine Work: {title}

| Attribute | Value |
|-----------|-------|
| ID | {id} |
| Status | {status} |
| Priority | Urgency {urgency}/4, Difficulty {difficulty}/4 |
| Tech Stack | {tech_stack} |
| Created | {created_at} |
| Started | {started_at or "Not started"} |
| Completed | {completed_at or "In progress"} |
| Repository | {repo_url or "Not created"} |
| Locked By | {locked_by or "Unlocked"} |

### Specification

{spec}

### Recent Activity

{If exists: last 5 entries from CHANGELOG.md}
{If blocked: blocker.md content}
{If paused: latest wrap-up summary}
```

### Update Status

**1. Validate transition:**

| From | Allowed To |
|------|-----------|
| idea | in_progress, abandoned |
| in_progress | paused, blocked, completed, abandoned |
| paused | in_progress, blocked, abandoned |
| blocked | in_progress, paused, abandoned |
| abandoned | idea (resurrection) |
| completed | (terminal - no transitions) |

**2. Handle special transitions:**

#### → blocked

Prompt for blocker reason:
```
Describe the blocker (what's preventing progress):
```

Create blocker.md:
```bash
echo "{reason}" | python3 ${CLAUDE_PLUGIN_ROOT}/scripts/project_utils.py blocker {project_dir}
```

Update registry:
```bash
echo '{"status": "blocked", "blocked_reason": "{summary}"}' | python3 ${CLAUDE_PLUGIN_ROOT}/scripts/registry.py update {id}
```

#### → paused

Prompt for wrap-up summary:
```
Provide a wrap-up summary (what was done, what's next):
```

Create wrap-up:
```bash
echo "{summary}" | python3 ${CLAUDE_PLUGIN_ROOT}/scripts/project_utils.py wrap-up {project_dir}
```

Update registry:
```bash
echo '{"status": "paused", "locked_by": null, "locked_at": null}' | python3 ${CLAUDE_PLUGIN_ROOT}/scripts/registry.py update {id}
```

#### → completed

Prompt for completion notes:
```
Provide completion summary (what was delivered):
```

Update CHANGELOG.md with final entry.

Update registry:
```bash
echo '{"status": "completed", "completed_at": "{ISO8601}", "locked_by": null, "locked_at": null}' | python3 ${CLAUDE_PLUGIN_ROOT}/scripts/registry.py update {id}
```

Display:
```
## Divine Work Completed! ✅

**{title}** has been marked as completed.

**Delivered:** {completion_summary}
**Repository:** {repo_url}
**Duration:** {started_at} → {completed_at}

*Gloria in excelsis Deo.*
```

#### → abandoned

Confirm:
```
Are you sure you want to abandon "{title}"?
This marks the project as forsaken but preserves all files.
```

Update registry:
```bash
echo '{"status": "abandoned", "locked_by": null, "locked_at": null}' | python3 ${CLAUDE_PLUGIN_ROOT}/scripts/registry.py update {id}
```

#### → idea (from abandoned)

Resurrection:
```bash
echo '{"status": "idea", "started_at": null, "repo_url": null}' | python3 ${CLAUDE_PLUGIN_ROOT}/scripts/registry.py update {id}
```

Display:
```
## Project Resurrected

**{title}** has returned to the pool of ideas.
It may be selected again by `/vibestart`.

*Lazarus, come forth.*
```

### Update Priority

Also support priority updates:
```
/project-status <id> urgency=3
/project-status <id> difficulty=1
```

```bash
echo '{"priority": {"urgency": 3, "difficulty": {current}}}' | python3 ${CLAUDE_PLUGIN_ROOT}/scripts/registry.py update {id}
```
