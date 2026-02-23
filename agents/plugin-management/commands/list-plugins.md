# /list-plugins

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).

List all registered plugins with their skills, commands, and status.

## Usage

```
/list-plugins                     # Full plugin catalog
/list-plugins --skills            # List all skills across plugins
/list-plugins --commands          # List all commands across plugins
/list-plugins --plugin <name>     # Details for a specific plugin
```

## How It Works

```
┌─────────────────────────────────────────────────────┐
│                 LIST PLUGINS                         │
├─────────────────────────────────────────────────────┤
│  STANDALONE (always works)                           │
│  ✓ Report known plugins from marketplace.json        │
│  ✓ Show skill and command counts per plugin          │
│  ✓ Display connector categories used                 │
├─────────────────────────────────────────────────────┤
│  SUPERCHARGED (when filesystem connected)            │
│  + Scan agents/ directory for actual plugin dirs     │
│  + Count real skill and command files                │
│  + Verify plugin.json and CONNECTORS.md exist        │
│  + Detect orphaned or unregistered plugins           │
└─────────────────────────────────────────────────────┘
```

## Plugin Catalog (11 Plugins)

| # | Plugin | Skills | Commands | Description |
|---|--------|--------|----------|-------------|
| 1 | seller-engine | 5 | 3 | Seller lifecycle, shops, reviews, staff |
| 2 | commerce | 6 | 4 | Products, orders, stock, pricing, categories |
| 3 | finance | 5 | 4 | Commission, payments, wallet, withdrawals |
| 4 | line-platform | 5 | 3 | LINE OA, webhook, messaging, rich menus |
| 5 | liff-apps | 6 | 4 | LIFF frontends, REST API, UI/UX |
| 6 | marketing | 4 | 3 | Promotions, campaigns, content strategy |
| 7 | customer-support | 5 | 5 | Triage, responses, escalation, knowledge base |
| 8 | data | 7 | 5 | Analytics, dashboards, queries, reports |
| 9 | productivity | 4 | 3 | Daily ops, task management, system health |
| 10 | enterprise-search | 4 | 2 | Cross-marketplace search, order lookup |
| 11 | plugin-management | 2 | 2 | Plugin scaffold, catalog, maintenance |
| | **Total** | **53** | **38** | |

## Connector Categories Used

| Category | Used By |
|----------|---------|
| ~~marketplace-engine | seller-engine, commerce, finance, data |
| ~~messaging | line-platform, customer-support, marketing |
| ~~identity | line-platform, liff-apps |
| ~~liff-app | liff-apps, marketing |
| ~~notification | line-platform, customer-support |
| ~~payment | finance |
| ~~wallet | finance, seller-engine |
| ~~rich-menu | line-platform |
| ~~webhook | line-platform |
| ~~crm | customer-support, enterprise-search |
| ~~stock | commerce |
| ~~api | liff-apps, data, enterprise-search |

## Output

```markdown
## Plugin Catalog

**Total Plugins:** [count]
**Total Skills:** [count]
**Total Commands:** [count]

### Plugins
| Plugin | Skills | Commands | Status |
|--------|--------|----------|--------|
| [name] | [n] | [n] | [active/stub] |

### Unregistered (if any)
| Directory | Has plugin.json | Has CONNECTORS.md |
|-----------|----------------|-------------------|
| [dir] | [yes/no] | [yes/no] |
```

## Next Steps

- Want to see details for a specific plugin?
- Should I create a new plugin?
- Want to audit connector coverage?

## Related Skills

- Uses [plugin-management](../skills/) for catalog management
- References [marketplace.json](../../marketplace.json) for registry
