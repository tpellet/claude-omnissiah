# digitus-Dei

*The Finger of God points to your next work.*

Divine project selection and autonomous execution. Store project ideas, let providence choose, execute to completion.

## Configuration

Create `~/.claude/digitus-Dei.local.md`:

```yaml
---
registry_dir: /path/to/your/projects
---
```

All projects will be created as subdirectories of `registry_dir`. The registry is stored at `{registry_dir}/.digitus-registry.json`.

## Commands

| Command | Purpose |
|---------|---------|
| `/new-project <brief>` | Add a project idea with AI-enriched specification |
| `/vibestart` | Divine selection of a new project → execute |
| `/viberesume` | Resume a paused/in-progress project |
| `/vibesolve` | Auto-solve a blocked project |
| `/list-projects` | View all projects in registry |
| `/project-status [id] [status]` | Check or update project status |
| `/resume-project <id>` | Resume a specific project |

## Project Lifecycle

```
idea → in_progress → completed
         ↓    ↑
       paused
         ↓
      blocked → (vibesolve) → in_progress
         ↓
     abandoned
```

## Project Structure

When a project starts, this structure is created:

```
{project-slug}/
├── README.md       # Specification and SLA
├── DESIGN.md       # Design decisions log
├── CHANGELOG.md    # Work completed
├── blocker.md      # (when blocked) Issue description
├── wrap-up/        # (when paused) Session summaries
├── src/
├── tests/
└── .git/
```

## Priority System

Projects are selected using the Eisenhower matrix:
- **Urgency** (1-4): How soon is this needed?
- **Difficulty** (1-4): How complex is this?

Selection favors easy + urgent projects first.

## Requirements

- `gh` CLI (authenticated)
- `git`
- Python 3.10+
- ralph-loop plugin (for autonomous execution)
