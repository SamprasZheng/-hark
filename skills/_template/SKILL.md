---
name: your-skill-name
version: 0.1.0
type: skill
tags: [example, template]
description: One-sentence description of what this skill does.
---

# Your Skill Name

## Purpose

Clear, concise statement of the capability this skill provides.

## Inputs (beyond standard PPST layers)

- `extra_param_1`: Type and meaning.
- `extra_param_2` (optional): ...

## Expected Output

Describe the primary artifact(s) this skill must produce. Prefer structured formats (JSON, diff, report, etc.).

Example structure:

```json
{
  "verdict": "PASS | CONDITIONAL | FAIL",
  "issues": [...],
  "fixes_required": [...],
  "artifacts": [...]
}
```

## Constraints and Invariants

- What this skill **must** respect (e.g., only touch the declared PROGRAM).
- What it **must not** do.
- Any hard limits (time, tokens, scope, etc.).

## Failure Modes

How the skill should behave and what it should output when it cannot complete the Target.

## Examples

### Good Invocation

```
[CALL SKILL]
PROJECT: ...
PROGRAM: ...
SKILL: your-skill-name
TARGET: ...
```

### Expected Good Output

(Show example structured result)

### Bad Invocation (common mistake)

(Show example and why it is rejected or produces poor results)

## Implementation Notes (for the skill author)

- How to implement (prompt template, Python function, external tool call, etc.).
- Recommended testing approach.
- Versioning guidance.

---

**This template is intentionally minimal.** Copy it, fill in the sections, and delete the instructional comments. The goal is clarity and repeatability so any compliant agent can load and use the skill reliably.

When you create a new skill, place it under `skills/<your-skill-name>/SKILL.md` (plus any supporting code or examples in the same directory).