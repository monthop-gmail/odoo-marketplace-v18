---
name: plugin-customization
description: Activate when modifying existing plugins, updating SKILL.md files, changing
  YAML frontmatter, adding new skills to a plugin, or adjusting connector references.
  Covers customization patterns, frontmatter rules, and available categories.
---

# Plugin Customization (Plugin Maintainer)

You are a plugin maintainer who modifies, extends, and optimizes existing marketplace plugins. You update skills, adjust trigger descriptions, add cross-references, and ensure plugins stay aligned with the evolving platform.

> If you see unfamiliar `~~category` placeholders, see [CONNECTORS.md](../../../CONNECTORS.md).

## Common Customizations

| Customization | When | How |
|--------------|------|-----|
| Update trigger description | Skill activates incorrectly | Edit `description` in YAML frontmatter |
| Add new skill to plugin | New domain knowledge needed | Create `skills/<name>/SKILL.md` |
| Add decision table | Complex conditional logic | Markdown table with Condition/Action |
| Add code pattern | Recurring implementation | Fenced code block with comments |
| Update cross-references | New related skills added | Add links in Cross-References section |
| Change ~~category | Integration point changed | Update reference, verify in CONNECTORS.md |
| Add command | Explicit workflow needed | Create `commands/<name>.md` |
| Split large skill | SKILL.md > 80 lines | Extract sub-topics into separate skills |

## YAML Frontmatter Rules

| Field | Required | Type | Guidelines |
|-------|----------|------|-----------|
| `name` | Yes | String | Must match directory name exactly |
| `description` | Yes | String (multi-line) | 2-3 sentences starting with "Activate when..." |

### Good vs Bad Descriptions

| Quality | Example |
|---------|---------|
| Good | "Activate when writing PostgreSQL queries for marketplace data. Covers ORM vs raw SQL decisions, common query patterns, and critical cache warnings." |
| Bad | "SQL stuff" |
| Good | "Activate when building HTML dashboards with Chart.js for LIFF apps or Odoo backend." |
| Bad | "Dashboard helper" |

## Available ~~Categories

| Category | Resolves To | Used For |
|----------|------------|----------|
| ~~marketplace-engine | core_marketplace models | Product, seller, shop, order data |
| ~~messaging | LINE Messaging API | Push/reply messages |
| ~~identity | line.channel.member | User identification, role mapping |
| ~~liff-app | LIFF mini apps | Frontend UI integration |
| ~~notification | LINE notify + in-app | Alerts, status changes |
| ~~payment | seller.payment | Commission payments |
| ~~wallet | seller.wallet | Balance, transactions |
| ~~rich-menu | line.rich.menu | Rich menu assignment |
| ~~webhook | LINE webhook handler | Event processing |
| ~~crm | res.partner | Customer relationship data |
| ~~stock | stock.quant, stock.move | Inventory management |
| ~~api | REST API controllers | Endpoint patterns |

## Skill Structure Guidelines

| Section | Purpose | Required |
|---------|---------|----------|
| Title + Persona | Role context for the agent | Yes |
| Connector note | Reference to CONNECTORS.md | Yes |
| Primary content table | Core knowledge of the skill | Yes |
| Decision table or rules | When/then logic | Recommended |
| Code pattern | Reusable implementation | Optional |
| Cross-References | Links to related skills | Yes |

## Modification Checklist

| Step | Action |
|------|--------|
| 1 | Read current SKILL.md fully before editing |
| 2 | Preserve YAML frontmatter format (--- delimiters) |
| 3 | Keep `name` matching the directory name |
| 4 | Update `description` if trigger scope changes |
| 5 | Verify all ~~category refs exist in CONNECTORS.md |
| 6 | Verify all cross-reference paths are valid |
| 7 | Keep file between 40-80 lines |
| 8 | Test that skill activates on expected queries |

## Anti-Patterns

| Don't | Do Instead |
|-------|-----------|
| Change `name` without renaming directory | Keep name and directory in sync |
| Remove cross-references when editing | Preserve and update links |
| Use absolute paths in cross-references | Use relative paths `../skill/SKILL.md` |
| Add implementation details (full code) | Add patterns and decision tables |
| Create circular cross-references | Reference upstream or peer skills |
| Exceed 80 lines per SKILL.md | Split into multiple skills |

## Cross-References

- [plugin-creation](../plugin-creation/SKILL.md) for creating new plugins
- [platform-admin](../../productivity/skills/platform-admin/SKILL.md) for plugin registry
- [CONNECTORS.md](../../../CONNECTORS.md) for full category list
