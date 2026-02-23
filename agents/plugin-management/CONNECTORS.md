# Connectors — Plugin Management

Maps `~~category` placeholders used in this plugin's skills and commands.

| Category | Concrete Tool | Location | Description |
|----------|--------------|----------|-------------|
| `~~agents` | Plugin System | `agents/` | 11 marketplace plugins |
| `~~memory` | Claude Memory | `memory/` | Plugin documentation and patterns |

## Plugin Structure Reference
```
plugin-name/
├── plugin.json          # Manifest (name, version, description)
├── CONNECTORS.md        # Tool category mapping
├── skills/              # Auto-activated domain knowledge
│   └── skill-name/
│       └── SKILL.md     # YAML frontmatter + role persona
└── commands/            # Explicit slash commands
    └── command-name.md  # Standalone/supercharged workflow
```

## Key Files
- `agents/marketplace.json` — Root manifest listing all plugins
- `agents/*/plugin.json` — Per-plugin manifests
- `memory/plugin_patterns.md` — Anthropic plugin pattern reference
