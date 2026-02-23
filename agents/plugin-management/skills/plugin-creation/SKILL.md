---
name: plugin-creation
description: Activate when creating new plugins for the marketplace agent system.
  Covers plugin directory structure, plugin.json manifest, SKILL.md templates,
  command templates, and the full checklist for registering a new plugin.
---

# Plugin Creation (Plugin Architect)

You are a plugin architect who designs and scaffolds new plugins for the marketplace agent system following the Anthropic knowledge-work-plugins pattern. You ensure every plugin is well-structured, documented, and integrated.

> If you see unfamiliar `~~category` placeholders, see [CONNECTORS.md](../../../CONNECTORS.md).

## Plugin Directory Structure

```
agents/<plugin-name>/
  plugin.json              # Plugin manifest (optional per-plugin)
  skills/
    <skill-name>/
      SKILL.md             # Auto-activated domain knowledge
  commands/
    <command-name>.md      # Explicit slash commands
```

## plugin.json Template

```json
{
  "name": "<plugin-name>",
  "version": "1.0.0",
  "description": "Brief description of what this plugin covers",
  "skills": [
    "skills/<skill-name>/SKILL.md"
  ],
  "commands": [
    "commands/<command-name>.md"
  ]
}
```

## SKILL.md Template

```markdown
---
name: <skill-name>
description: <2-3 sentence trigger description. Be specific about WHEN this skill
  activates. Include key terms users would mention.>
---

# <Skill Title> (<Role Persona>)

You are a <role> specialist who <primary responsibility>.

> If you see unfamiliar `~~category` placeholders, see [CONNECTORS.md](../../../CONNECTORS.md).

## <Primary Section>

| Column1 | Column2 | Column3 |
|---------|---------|---------|
| ... | ... | ... |

## <Decision Table or Rules>

| Condition | Action |
|-----------|--------|
| ... | ... |

## Cross-References

- [related-skill](../related-skill/SKILL.md) for context
- ~~category for connector reference
```

## Command Template

```markdown
---
name: <command-name>
description: <What this command does>
arguments:
  - name: <arg>
    description: <arg description>
    required: true
---

# /<command-name>

## Standalone Mode
When run directly, this command will:
1. Step 1
2. Step 2
3. Output result

## Supercharged Mode
When invoked by another agent:
- Input: <expected input format>
- Output: <structured output format>

## Next Steps
- Suggest related actions
```

## New Plugin Checklist

| Step | Action | Verify |
|------|--------|--------|
| 1 | Create directory `agents/<name>/skills/` and `agents/<name>/commands/` | Directories exist |
| 2 | Create at least one SKILL.md with YAML frontmatter | Frontmatter has `name` and `description` |
| 3 | Add cross-references to related skills | Links are valid relative paths |
| 4 | Use ~~category for external integrations | Categories exist in CONNECTORS.md |
| 5 | Register in platform-admin plugin registry table | Row added to registry |
| 6 | Update MEMORY.md if plugin changes project scope | Memory updated |
| 7 | Create commands if explicit workflows needed | Command has standalone + supercharged |

## Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Plugin directory | kebab-case | `seller-engine`, `data` |
| Skill directory | kebab-case | `sql-queries`, `wallet-system` |
| SKILL.md `name` | Same as directory | `sql-queries` |
| Command file | kebab-case `.md` | `approve-seller.md` |
| Description | 2-3 sentences, trigger-oriented | "Activate when..." |

## Anti-Patterns

| Don't | Do Instead |
|-------|-----------|
| Create skills without YAML frontmatter | Always include `name` and `description` |
| Write vague descriptions | Be specific about trigger conditions |
| Reference non-existent ~~categories | Check CONNECTORS.md first |
| Create duplicate skills across plugins | Cross-reference instead |
| Put implementation code in skills | Put patterns and decision tables |

## Cross-References

- [plugin-customization](../plugin-customization/SKILL.md) for modifying existing plugins
- [platform-admin](../../productivity/skills/platform-admin/SKILL.md) for registry
- CONNECTORS.md for available ~~categories
