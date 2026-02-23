# /start

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).

Daily kickoff — check platform health, review pending actions, and set today's priorities.

## Usage

```
/start                            # Full daily briefing
/start --quick                    # Compact summary only
```

## How It Works

```
┌─────────────────────────────────────────────────────┐
│                     START                             │
├─────────────────────────────────────────────────────┤
│  STANDALONE (always works)                           │
│  ✓ Report known status from MEMORY.md                │
│  ✓ List pending tasks from backlog                   │
│  ✓ Suggest priorities based on project phase         │
├─────────────────────────────────────────────────────┤
│  SUPERCHARGED (when codebase + ~~api connected)      │
│  + Scan pending sellers (seller_status='pending')    │
│  + Check products awaiting review                    │
│  + Count pending withdrawals                         │
│  + Verify system uptime and API health               │
│  + Show recent git activity                          │
└─────────────────────────────────────────────────────┘
```

## Daily Checklist

| Check | Source | Priority |
|-------|--------|----------|
| Pending seller applications | res.partner (seller_status='pending') | High |
| Products awaiting review | product.template (status='pending') | Medium |
| Pending withdrawals | seller.withdrawal.request (state='pending') | High |
| Unresolved support tickets | Support queue | Medium |
| System errors (last 24h) | Odoo logs | Critical if any |
| Module completeness | MEMORY.md status table | Low |

## Output

```markdown
## Daily Briefing

**Date:** [date]
**Phase:** Phase 2 — Wallet + Staff System

### Platform Health
| Indicator | Status |
|-----------|--------|
| Core Marketplace | [ok/warning/error] |
| LINE Integration | [ok/warning/error] |
| REST API | [ok/warning/error] |
| LIFF Apps | [n]/5 active |

### Pending Actions
| Type | Count | Oldest | Priority |
|------|-------|--------|----------|
| Seller Applications | [n] | [date] | [priority] |
| Product Reviews | [n] | [date] | [priority] |
| Withdrawals | [n] | ฿[total] | [priority] |
| Support Tickets | [n] | [date] | [priority] |

### Today's Priorities
1. [Priority item with context]
2. [Priority item with context]
3. [Priority item with context]

### Quick Stats
| Metric | Today | Yesterday | Trend |
|--------|-------|-----------|-------|
| Orders | [n] | [n] | [up/down] |
| New Users | [n] | [n] | [up/down] |
| GMV | ฿[amount] | ฿[amount] | [up/down] |
```

## Next Steps

- Want me to process pending seller applications?
- Should I review the pending withdrawals?
- Want to see the full backlog?

## Related Skills

- Uses [productivity](../skills/) for task management
- Cross-references all domain skills for health checks
