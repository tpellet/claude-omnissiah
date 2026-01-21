---
description: Auto-solve a blocked project with divine intervention
allowed-tools: [Bash, Read, Write, Edit, AskUserQuestion, Skill, WebSearch, WebFetch]
---

# /vibesolve - Divine Intervention for Blocked Work

Select a blocked project, analyze and solve the blocker, then resume work in the current session.

## Usage

```
/vibesolve
```

## Process

### 1. Divine Selection

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/selector.py --status=blocked --unlocked
```

**If no blocked projects:** Report that no intervention is needed.

### 2. Analyze the Blocker

Read context:
- `blocker.md` - The issue description
- README.md, DESIGN.md, CHANGELOG.md
- Relevant source files

Use WebSearch/WebFetch to research the issue.

### 3. Present the Blocked Work

Show blocker details and proposed solution with confidence level.

Ask:
- "Accept and continue"
- "Need more information"
- "Reject - I'll provide guidance"
- "Abandon project"

### 4. Handle Response

**If Accept:**

a) Remove blocker:
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/project_utils.py remove-blocker {project_dir}
echo '{"status": "in_progress"}' | python3 ${CLAUDE_PLUGIN_ROOT}/scripts/registry.py update {id}
```

b) Lock and change directory:
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/registry.py lock {id} "current-session"
cd {project_dir}
```

c) Start work with Skill tool:
```
skill: "ralph-loop:ralph-loop"
args: "{project_spec} --completion-promise 'MVP complete with tests passing'"
```

**If Need more info:** Iterate on clarifying questions.

**If Reject:** Get user guidance and update blocker.md, then proceed.

**If Abandon:**
```bash
echo '{"status": "abandoned"}' | python3 ${CLAUDE_PLUGIN_ROOT}/scripts/registry.py update {id}
```

### 5. On Completion

Unlock the project:
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/registry.py unlock {id}
```
