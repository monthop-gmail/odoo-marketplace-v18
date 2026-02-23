# /create-plugin

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).

Scaffold a new plugin with the standard directory structure, manifest, connectors, and starter files.

## Usage

```
/create-plugin <name> "description"
/create-plugin logistics "Shipping, delivery, and logistics management"
/create-plugin analytics "Advanced analytics and reporting engine"
```

## How It Works

```
┌─────────────────────────────────────────────────────┐
│                CREATE PLUGIN                         │
├─────────────────────────────────────────────────────┤
│  STANDALONE (always works)                           │
│  ✓ Generate plugin directory structure               │
│  ✓ Create plugin.json manifest                       │
│  ✓ Create CONNECTORS.md with relevant categories     │
│  ✓ Scaffold starter skill and command files           │
├─────────────────────────────────────────────────────┤
│  SUPERCHARGED (when filesystem connected)            │
│  + Write all files to agents/<name>/                 │
│  + Register in marketplace.json                      │
│  + Validate no naming conflicts with existing plugins│
│  + Create initial skill from description             │
└─────────────────────────────────────────────────────┘
```

## Generated Structure

```
agents/<name>/
├── plugin.json                   # Plugin manifest
├── CONNECTORS.md                 # Tool category mapping
├── skills/
│   ├── overview/
│   │   └── SKILL.md              # Primary domain skill
│   └── <sub-domain>/
│       └── SKILL.md              # Sub-domain skill
└── commands/
    └── <default-command>.md      # Starter command
```

## plugin.json Template

```json
{
  "name": "<name>",
  "description": "<description>",
  "version": "1.0.0",
  "skills_dir": "skills",
  "commands_dir": "commands"
}
```

## CONNECTORS.md Template

| Section | Content |
|---------|---------|
| Header | Connector category mapping for this plugin |
| Table | ~~category → Concrete Tool → Module → Description |
| Auth | Authentication modes relevant to this plugin |
| Base URLs | API base URLs if applicable |

## SKILL.md Template (YAML Frontmatter)

```yaml
---
name: <skill-name>
description: >
  Trigger description for auto-activation.
  When the user asks about [domain topic], activate this skill.
---
```

## Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Plugin dir | kebab-case | `logistics` |
| Skill dir | kebab-case | `shipping-management` |
| Command file | kebab-case.md | `track-shipment.md` |
| Skill name | Title Case | `Shipping Management` |
| Command name | /kebab-case | `/track-shipment` |

## Output

```markdown
## Plugin Created

**Name:** [name]
**Path:** agents/[name]/
**Description:** [description]

### Files Created
- agents/[name]/plugin.json
- agents/[name]/CONNECTORS.md
- agents/[name]/skills/overview/SKILL.md
- agents/[name]/commands/[command].md

### Registered In
- marketplace.json — entry added
```

## Next Steps

- Want me to add more skills or commands to this plugin?
- Should I define the connector categories for this domain?
- Want to see the full plugin catalog?

## Related Skills

- Uses [plugin-management](../skills/) for scaffold templates
- References [marketplace.json](../../marketplace.json) for registration
