# Skill Template

Use this directory as the starting point when creating a new Skill for the PPST framework.

## Recommended Structure

```
skills/your-skill-name/
├── SKILL.md          # Required — the loadable definition (copy from _template/SKILL.md)
├── implementation/   # Optional — code, prompts, configuration, etc.
├── examples/         # Strongly recommended — concrete usage examples
└── tests/            # Recommended for non-trivial skills
```

## Steps to Create a New Skill

1. Copy `skills/_template/` to `skills/your-skill-name/`.
2. Rename and fill in `SKILL.md` (delete the instructional comments).
3. Implement the capability (prompt, Python function, external hook, etc.).
4. Add at least one good and one bad example in `examples/`.
5. Test the skill in isolation if possible.
6. Document any required environment or dependencies.

## Principles for Good Skills

- Single responsibility (one clear capability).
- Explicit about the four PPST layers it expects and respects.
- Produces structured, verifiable output.
- Minimal hidden state or side effects.
- Easy for other agents to discover and invoke via the `CALL SKILL` protocol.
- Versioned from the start.

See the main `skills/project-program-skill-target/README.md` for the overall PPST calling syntax and collaboration patterns.

Happy skill building!