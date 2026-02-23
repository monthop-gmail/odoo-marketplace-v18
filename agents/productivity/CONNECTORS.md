# Connectors — Productivity

Maps `~~category` placeholders used in this plugin's skills and commands.

| Category | Concrete Tool | Location | Description |
|----------|--------------|----------|-------------|
| `~~marketplace-engine` | Odoo 18 | `core_marketplace/` + `core_line_integration/` | Full platform codebase |
| `~~api` | REST API | `controllers/api_*.py` | All API endpoints |
| `~~memory` | Claude Memory | `memory/` + `CLAUDE.md` | Persistent project knowledge |
| `~~agents` | Plugin System | `agents/` | 11 marketplace plugins |

## Key Files
- `CLAUDE.md` — Project instructions (hot cache)
- `memory/MEMORY.md` — Auto-memory (loaded every conversation)
- `memory/task_tree.md` — Task breakdown
- `memory/backlog.md` — Prioritized backlog
- `agents/marketplace.json` — Root plugin manifest
