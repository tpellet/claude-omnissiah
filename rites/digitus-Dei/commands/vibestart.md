---
description: Divine selection of a new project - The Finger of God points
allowed-tools: [Bash, Read, Write, Task, AskUserQuestion]
---

# /vibestart - The Finger of God Points

Let divine providence select your next project from unstarted ideas, then execute it autonomously.

## Usage

```
/vibestart
```

## Process

### 1. Divine Selection

Select a random project weighted by Eisenhower priority (easy + urgent first):

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/selector.py --status=idea
```

**If no projects available:**
```
No unstarted projects in the registry.
Add one with `/new-project <brief>` and let the Finger of God guide your work.
```

### 2. Present the Chosen Work

```
## The Finger of God Points To...

**{title}**

| Attribute | Value |
|-----------|-------|
| ID | {id} |
| Urgency | {urgency}/4 |
| Difficulty | {difficulty}/4 |
| Tech Stack | {tech_stack} |
| Created | {created_at} |

### Specification

{spec}

---

Accept this divine assignment?
```

Use AskUserQuestion:
- "Accept and begin"
- "Choose another" (re-roll)
- "Cancel"

### 3. Initialize Project

On acceptance:

**a) Create project directory structure:**
```bash
echo '{project_json}' | python3 ${CLAUDE_PLUGIN_ROOT}/scripts/project_utils.py init
```

This creates:
- `{registry_dir}/{project-slug}/`
- `README.md` (from spec)
- `DESIGN.md` (initialized)
- `CHANGELOG.md` (initialized)
- `src/`, `tests/`
- Git repository

**b) Create GitHub repository:**
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/project_utils.py github {project_dir}
```

**c) Update registry:**
```bash
echo '{"status": "in_progress", "started_at": "{ISO8601}", "repo_url": "{url}"}' | python3 ${CLAUDE_PLUGIN_ROOT}/scripts/registry.py update {id}
```

Note: Do NOT lock the project here. The spawned session will lock it via SessionStart hook.

### 4. Launch Autonomous Execution

Start a new tmux session with ralph-loop, passing the project ID for automatic locking:

```bash
tmux new-session -d -s "digitus-{id}" -c "{project_dir}"
tmux send-keys -t "digitus-{id}" "DIGITUS_PROJECT_ID={id} claude --plugin-dir ${CLAUDE_PLUGIN_ROOT}/.. '/ralph-loop'" Enter
```

The SessionStart hook automatically locks the project using DIGITUS_PROJECT_ID.
When the session ends, the SessionEnd hook unlocks it.

### 5. Report Launch

```
## Divine Work Commenced

**Project:** {title}
**Directory:** {project_dir}
**Repository:** {repo_url}
**Session:** digitus-{id}

The work proceeds autonomously. Monitor with:
- `tmux attach -t digitus-{id}` - Watch progress
- `/project-status {id}` - Check status
- `/list-projects` - View all projects

When pausing, the agent will create wrap-up documentation.
When blocked, a blocker.md will be created for `/vibesolve`.

*In nomine Omnissiah.*
```

## Tools Available to Executing Agent

The spawned agent has access to:
- **Bash** - git, gh, build tools
- **Read/Write/Edit** - File operations
- **Serena** - Code inspection and navigation
- **Task** - Subagent spawning
- **WebFetch/WebSearch** - Documentation lookup

## Design Document Requirements

The executing agent MUST maintain:

1. **DESIGN.md** - Append decisions as work progresses:
   ```markdown
   ## {date} - {decision title}
   
   **Context:** Why this decision was needed
   **Decision:** What was decided
   **Rationale:** Why this approach
   **Alternatives considered:** What else was evaluated
   ```

2. **CHANGELOG.md** - Append completed work:
   ```markdown
   ## {date} - {summary}
   
   - Completed: {list of completed items}
   - Files changed: {list}
   ```
