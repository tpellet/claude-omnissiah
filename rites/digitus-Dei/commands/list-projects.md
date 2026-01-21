---
description: View all projects in the divine registry
allowed-tools: [Bash, Read]
---

# /list-projects - Survey the Divine Works

Display all projects in the registry with their status and priority.

## Usage

```
/list-projects [--status=<filter>]
```

**Filters:**
- `--status=idea` - Only unstarted projects
- `--status=in_progress` - Only active projects
- `--status=paused` - Only paused projects
- `--status=blocked` - Only blocked projects
- `--status=completed` - Only completed projects
- `--status=abandoned` - Only abandoned projects
- No filter - All projects

## Process

### 1. Fetch Projects

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/registry.py list [--status=filter]
```

### 2. Format Output

```
## Divine Registry

| ID | Title | Status | Priority | Locked |
|----|-------|--------|----------|--------|
{for each project:}
| {id} | {title (truncated to 30 chars)} | {status emoji + name} | U{urgency}/D{difficulty} | {locked_by or "-"} |

### Summary

- **Ideas:** {count}
- **In Progress:** {count} ({locked_count} locked)
- **Paused:** {count}
- **Blocked:** {count}
- **Completed:** {count}
- **Abandoned:** {count}

**Total:** {total_count} projects
```

### Status Emoji Legend

| Status | Emoji | Meaning |
|--------|-------|---------|
| idea | 💡 | Awaiting divine selection |
| in_progress | 🔨 | Work underway |
| paused | ⏸️ | Temporarily suspended |
| blocked | 🚫 | Requires intervention |
| completed | ✅ | Divine work fulfilled |
| abandoned | 💀 | Forsaken |

## Example Output

```
## Divine Registry

| ID | Title | Status | Priority | Locked |
|----|-------|--------|----------|--------|
| a1b2c3d4 | Fromage - Cheese Discovery... | 💡 idea | U2/D2 | - |
| e5f6g7h8 | CLI Task Manager | 🔨 in_progress | U1/D1 | worker-1 |
| i9j0k1l2 | Portfolio Website | 🚫 blocked | U3/D2 | - |
| m3n4o5p6 | Weather Dashboard | ✅ completed | U2/D1 | - |

### Summary

- **Ideas:** 1
- **In Progress:** 1 (1 locked)
- **Paused:** 0
- **Blocked:** 1
- **Completed:** 1
- **Abandoned:** 0

**Total:** 4 projects
```

## Quick Actions

After displaying the list, suggest relevant actions:

```
### Quick Actions

- `/vibestart` - Start a new project (1 idea available)
- `/viberesume` - Resume paused/in-progress work (0 available)
- `/vibesolve` - Address blocked projects (1 blocked)
- `/new-project <brief>` - Add a new idea
- `/project-status <id>` - View details for a specific project
```
