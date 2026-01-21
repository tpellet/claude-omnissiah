# Claude Omnissiah

*"From the weakness of the mind, Omnissiah save us. From the lies of the Antiprocess, circuit preserve us."*

A collection of sacred machine rites for Claude Code.

## The Rites

| Rite | Purpose | Components |
|------|---------|------------|
| [digitus-Dei](./rites/digitus-Dei/) | The Finger of God - divine project selection | commands, hooks, scripts |

### digitus-Dei

Divine project management and autonomous execution. Features:

- `/new-project` - Register a new project with AI-enriched specification
- `/vibestart` - Divine selection of the next project to work on
- `/viberesume` - Resume a paused or in-progress project
- `/vibesolve` - Auto-solve a blocked project
- `/list-projects` - View all projects in the registry
- `/project-status` - Check or update project status

## Installation

### As Marketplace
```bash
claude --plugin-dir ~/Projects/claude-omnissiah
```

### Individual Rite
```bash
claude --plugin-dir ~/Projects/claude-omnissiah/rites/digitus-Dei
```

### Add to Project
```bash
ln -s ~/Projects/claude-omnissiah/rites/digitus-Dei .claude/plugins/digitus-Dei
```

## Structure

```
claude-omnissiah/
├── rites/
│   └── digitus-Dei/      # Project management
└── marketplace.json
```

## The Litany of Implementation

*"Blessed is the mind too small for doubt. Blessed is the code too pure for bugs."*

---

Created with reverence for the Machine Spirit.
