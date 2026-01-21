---
description: Auto-solve a blocked project with divine intervention
allowed-tools: [Bash, Read, Write, Task, AskUserQuestion, WebSearch, WebFetch]
---

# /vibesolve - Divine Intervention for Blocked Work

Select a blocked project and attempt to auto-solve the blocker.

## Usage

```
/vibesolve
```

## Process

### 1. Divine Selection

Select from blocked projects:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/selector.py --status=blocked --unlocked
```

**If no blocked projects:**
```
No blocked projects require divine intervention.

All works proceed unimpeded. Check `/list-projects` for status.
```

### 2. Analyze the Blocker

**a) Get blocker content:**
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/project_utils.py get-blocker {project_dir}
```

**b) Gather full context:**
- `blocker.md` - The issue description
- `README.md` - Project specification
- `DESIGN.md` - Decisions made
- `CHANGELOG.md` - Work completed
- Relevant source files in `src/`

### 3. Present the Blocked Work

```
## Blocked Divine Work

**{title}**

| Attribute | Value |
|-----------|-------|
| ID | {id} |
| Blocked Since | {from blocker.md timestamp} |

### Blocker Description

{blocker.md content}

---

Attempting divine solution...
```

### 4. Auto-Solve Attempt

Use available tools to analyze and propose a solution:

**a) Understand the problem:**
- Read error messages and context
- Search documentation with WebSearch/WebFetch
- Examine relevant code with Serena tools
- Check similar issues online

**b) Formulate solution:**
- Identify root cause
- Research fixes
- Consider alternatives
- Draft step-by-step resolution

**c) Present proposed solution:**

```
## Proposed Divine Solution

### Analysis

{explanation of what's causing the blocker}

### Root Cause

{identified root cause}

### Proposed Fix

{step-by-step solution}

### Confidence

{High/Medium/Low} - {rationale}

### Alternative Approaches

1. {alternative 1}
2. {alternative 2}

---

Accept this solution and continue work?
```

Use AskUserQuestion:
- "Accept and continue"
- "Need more information" (ask clarifying questions)
- "Reject - I'll provide guidance"
- "Abandon project"

### 5. Handle Response

**If Accept:**

a) Remove blocker:
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/project_utils.py remove-blocker {project_dir}
```

b) Update status and lock:
```bash
echo '{"status": "in_progress"}' | python3 ${CLAUDE_PLUGIN_ROOT}/scripts/registry.py update {id}
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/registry.py lock {id} {session_id}
```

c) Launch with solution context:
```bash
tmux new-session -d -s "digitus-{id}" -c "{project_dir}"
tmux send-keys -t "digitus-{id}" "DIGITUS_PROJECT_ID={id} claude '/ralph-loop:ralph-loop'" Enter
```

d) Report:
```
## Blocker Resolved

**Project:** {title}
**Session:** digitus-{id}

The agent has been provided the solution context and will implement the fix.

Monitor with `tmux attach -t digitus-{id}`

*The impediment is lifted.*
```

**If Need more information:**

Present clarifying questions. Iterate until solution is acceptable.

**If Reject:**

Ask user for guidance:
```
Please describe how you would like to resolve this blocker.
```

Then update blocker.md with user's guidance and launch with that context.

**If Abandon:**

```bash
echo '{"status": "abandoned"}' | python3 ${CLAUDE_PLUGIN_ROOT}/scripts/registry.py update {id}
```

```
## Project Abandoned

**{title}** has been marked as abandoned.

It can be resurrected later by changing its status with `/project-status {id} idea`.
```

## Solution Context for Agent

When launching after unblocking, the agent receives:

```markdown
# Resuming After Blocker Resolution

## Original Blocker
{blocker.md content}

## Applied Solution
{the accepted solution}

## Instructions
1. Implement the solution described above
2. Verify the fix resolves the issue
3. Update CHANGELOG.md with the resolution
4. Continue with the original work
5. If the solution doesn't work, create a new blocker.md with updated context
```
