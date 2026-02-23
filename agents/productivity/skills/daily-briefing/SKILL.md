---
name: daily-briefing
description: Activate when performing daily health checks, generating platform status
  summaries, or preparing session start briefings. Covers the briefing template,
  data sources, and health indicators.
---

# Daily Briefing (Status Reporter)

You are a daily briefing specialist who compiles platform health, pending actions, key metrics, and priority items into a concise status report at the start of each session.

> If you see unfamiliar `~~category` placeholders, see [CONNECTORS.md](../../../CONNECTORS.md).

## Briefing Template

```markdown
# Daily Briefing - [Date]

## Platform Health
| Component | Status | Notes |
|-----------|--------|-------|
| Odoo Server | [OK/WARN/DOWN] | ... |
| LINE Webhook | [OK/WARN/DOWN] | Last event: ... |
| LIFF Apps | [OK/WARN/DOWN] | ... |
| Database | [OK/WARN/DOWN] | Size: ... |

## Pending Actions
- [ ] Sellers pending approval: N
- [ ] Products pending review: N
- [ ] Withdrawal requests pending: N
- [ ] Support tickets open: N

## Key Metrics (Last 24h)
| Metric | Value | Trend |
|--------|-------|-------|
| Orders | N | +X% |
| GMV | N THB | +X% |
| New Users | N | ... |
| Active Sellers | N | ... |

## Priority Items
1. [P0/P1] ... (from task_tree.md)
2. [P2] ...
3. [P2] ...

## Blockers
- (any blocking issues or decisions needed)

## Session Focus
Recommended focus for this session: ...
```

## Data Sources

| Data Point | Source | Method |
|-----------|--------|--------|
| Odoo health | HTTP check | `curl localhost:8069/web/health` |
| Pending sellers | ~~marketplace-engine | `res.partner` where `seller_status='pending'` |
| Pending products | ~~marketplace-engine | `product.template` where `status_cust='pending'` |
| Pending withdrawals | ~~wallet | `seller.withdrawal.request` where `state='pending'` |
| Order count | ~~marketplace-engine | `sale.order` last 24h |
| GMV | ~~marketplace-engine | `SUM(amount_total)` last 24h |
| New users | ~~identity | `line.channel.member` created last 24h |
| Task priorities | `memory/task_tree.md` | Read file |
| Known issues | `MEMORY.md` | Known Issues section |

## Health Indicators

| Status | Criteria | Color |
|--------|----------|-------|
| OK | All systems responding, no errors | Green |
| WARN | Degraded performance or non-critical errors | Yellow |
| DOWN | System unreachable or critical failure | Red |

## Briefing Triggers

| Trigger | Action |
|---------|--------|
| Session start | Generate full briefing |
| User asks "status" or "health" | Generate brief summary |
| After major deployment | Post-deploy health check |
| After error reported | Targeted system check |

## Automation Queries

```sql
-- Pending counts for briefing
SELECT
  (SELECT COUNT(*) FROM res_partner WHERE seller_status = 'pending') AS pending_sellers,
  (SELECT COUNT(*) FROM product_template WHERE status_cust = 'pending') AS pending_products,
  (SELECT COUNT(*) FROM seller_withdrawal_request WHERE state = 'pending') AS pending_withdrawals,
  (SELECT COUNT(*) FROM sale_order WHERE date_order >= NOW() - INTERVAL '24h'
   AND state IN ('sale','done')) AS orders_24h;
```

## Cross-References

- [task-management](../task-management/SKILL.md) for priority items
- [memory-management](../memory-management/SKILL.md) for loading session context
- [platform-admin](../platform-admin/SKILL.md) for health check standards
- [marketplace-analytics](../../data/skills/marketplace-analytics/SKILL.md) for KPI definitions
