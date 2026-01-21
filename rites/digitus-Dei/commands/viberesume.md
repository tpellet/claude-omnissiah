---
description: Resume a paused or in-progress project by divine selection
allowed-tools: [Bash, Read, Write, Edit, AskUserQuestion, Skill]
---

# /viberesume - Return to Unfinished Work

Randomly select an in-progress or paused project and resume work in the current session.

## Usage

```
/viberesume
```

## Process

### 1. Divine Selection

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/selector.py --status=in_progress,paused --unlocked
```

**If no projects:** Suggest `/vibestart` for new projects or `/vibesolve` for blocked ones.

### 2. Gather Context

Read from project directory:
- README.md - Specification
- DESIGN.md - Design decisions
- CHANGELOG.md - Work completed

Get last wrap-up if paused:
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/project_utils.py get-wrap-up {project_dir}
```

### 3. Present and Confirm

Show project details and context summary. Ask:
- "Resume"
- "Choose another"
- "Cancel"

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
