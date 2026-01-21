---
description: Add a new project idea with AI-enriched specification
allowed-tools: [Bash, Read, Write, AskUserQuestion]
---

# /new-project - Register a Divine Work

Add a new project to the registry with an AI-enriched specification.

## Usage

```
/new-project <brief description>
```

## Process

### 1. Parse the Brief

Extract the user's brief description from the command arguments.

### 2. Enrich the Brief

Generate a comprehensive project specification by analyzing the brief:

**Generate the following:**

- **Title**: A catchy, descriptive project name (e.g., "Fromage - Wine-style Cheese Discovery")
- **Spec**: 2-3 paragraphs describing:
  - What the project does
  - Key features
  - Target users
  - Success criteria
- **Tech Stack**: Inferred technologies based on the brief (follow user's CLAUDE.md preferences if available)
- **Difficulty**: 1-4 based on:
  - 1 = Simple (single feature, familiar tech)
  - 2 = Medium (multiple features, some learning)
  - 3 = Hard (complex architecture, new tech)
  - 4 = Very Hard (research required, cutting edge)

### 3. Present for Approval

Display the enriched specification to the user:

```
## Divine Work Proposed

**Title:** {title}

**Tech Stack:** {tech_stack as comma-separated list}

**Difficulty:** {difficulty}/4 - {rationale for difficulty}

**Urgency:** 2/4 (default - adjust if needed)

### Specification

{spec}

---

**Original brief:** "{brief}"

Confirm this specification? You may also request changes.
```

Use AskUserQuestion with options:
- "Confirm as-is"
- "Adjust priority"
- "Edit specification"

### 4. Handle User Response

**If Confirm:**

Write JSON with Python, then add via `--file`:

```bash
python3 -c "
import json
data = {
    'title': 'Project Title',
    'brief': 'Short description',
    'spec': '''First paragraph.

Second paragraph.''',
    'tech_stack': ['Flutter', 'SQLite'],
    'urgency': 2,
    'difficulty': 3
}
with open('/tmp/claude/project.json', 'w') as f:
    json.dump(data, f)
"

python3 ${CLAUDE_PLUGIN_ROOT}/scripts/registry.py add --file=/tmp/claude/project.json
```

**If Adjust priority:**
Ask for urgency (1-4) and difficulty (1-4), then save.

**If Edit:**
Let user provide corrections, regenerate or manually edit, then confirm again.

### 5. Confirm Registration

```
## Project Registered

**ID:** {id}
**Title:** {title}
**Status:** idea

The Finger of God awaits. Run `/vibestart` when ready.
```

## Example

```
> /new-project cheese app like Vivino for Android

## Divine Work Proposed

**Title:** Fromage - Cheese Discovery App

**Tech Stack:** Flutter, Firebase, Google ML Kit

**Difficulty:** 2/4 - Mobile app with ML features, moderate complexity

**Urgency:** 2/4 (default)

### Specification

Fromage is a mobile application that brings the Vivino experience to cheese lovers. Users can photograph any cheese to identify it, read reviews, track their tasting history, and discover new varieties based on their preferences.

Key features include image recognition for cheese identification, a social review system, personalized recommendations, and integration with local cheese shops for availability and pricing.

Target users are cheese enthusiasts who want to explore beyond their usual choices and remember what they've tried. Success means building a database of 1000+ cheeses with active user contributions.

---

**Original brief:** "cheese app like Vivino for Android"

Confirm this specification?
```
