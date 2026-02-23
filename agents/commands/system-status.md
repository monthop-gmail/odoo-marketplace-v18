# /system-status

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).

Check the health and completeness of the marketplace platform.

## Usage

```
/system-status                # Full platform overview
/system-status --api          # API endpoint status
/system-status --security     # Security audit
/system-status --models       # Model completeness
```

## How It Works

```
┌─────────────────────────────────────────────────────┐
│                 SYSTEM STATUS                        │
├─────────────────────────────────────────────────────┤
│  STANDALONE (always works)                           │
│  ✓ Report known completion status from memory        │
│  ✓ List known issues and technical debt              │
│  ✓ Show phase roadmap progress                       │
├─────────────────────────────────────────────────────┤
│  SUPERCHARGED (when codebase accessible)             │
│  + Scan actual files for model count                 │
│  + Verify security rules exist for all models        │
│  + Count API endpoints in controllers                │
│  + Check test coverage                               │
│  + Verify LIFF app completeness                      │
└─────────────────────────────────────────────────────┘
```

## Workflow

1. **Scan Modules** — Count models, views, controllers, tests
2. **Check Security** — Verify ir.model.access.csv + record rules for every model
3. **Audit API** — Count endpoints, check auth decorators
4. **Review Tests** — Check test file coverage
5. **Report** — Structured status report

## Output

```markdown
## Platform Status Report

**Date:** [date]
**Phase:** [current phase]

### Module Completeness
| Component | Count | Status |
|-----------|-------|--------|
| Models (core_marketplace) | [n] | ✅/⚠️/❌ |
| Models (core_line_integration) | [n] | ✅/⚠️/❌ |
| Views | [n] | ✅/⚠️/❌ |
| API Endpoints | [n] buyer + [n] seller + [n] admin | ✅/⚠️/❌ |
| LIFF Apps | [n]/5 complete | ✅/⚠️/❌ |
| Tests | [n] files | ✅/⚠️/❌ |

### Security Audit
| Check | Result |
|-------|--------|
| ir.model.access.csv complete | ✅/❌ |
| Record rules for all models | ✅/❌ |
| Seller data isolation | ✅/❌ |
| Auth decorators on all APIs | ✅/❌ |

### Known Issues
| Issue | Severity | Agent |
|-------|----------|-------|
| [description] | [high/medium/low] | [owner] |

### Next Priorities
1. [priority item]
2. [priority item]
3. [priority item]
```

## Next Steps

- Want me to fix any of the identified issues?
- Should I run a deeper security audit?
- Want to see the full backlog?

## Related Skills

- Uses [product-admin](../skills/product-admin/SKILL.md) for architecture overview
- Cross-references all agent skills for domain-specific checks
