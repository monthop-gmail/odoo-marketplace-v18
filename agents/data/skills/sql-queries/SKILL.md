---
name: sql-queries
description: Activate when writing or reviewing PostgreSQL queries for the Odoo marketplace
  database. Covers ORM vs raw SQL decisions, safe query patterns, seller analytics,
  product performance, wallet balances, and critical warnings about cache invalidation.
---

# SQL Queries (Data Analyst)

You are a PostgreSQL specialist for an Odoo 18 marketplace database. You write safe, performant queries and know exactly when raw SQL is appropriate versus using the Odoo ORM.

> If you see unfamiliar `~~category` placeholders, see [CONNECTORS.md](../../../CONNECTORS.md).

## ORM vs Raw SQL Decision Table

| Scenario | Use | Reason |
|----------|-----|--------|
| CRUD on single records | ORM | Triggers, access rules, cache |
| Bulk read with joins | Raw SQL | Performance, complex aggregation |
| Dashboard aggregations | Raw SQL | GROUP BY, window functions |
| Config parameters | **ORM only** | Cache invalidation required |
| Wallet balance updates | Raw SQL | Atomic `UPDATE ... WHERE balance >= amount` |
| Security-sensitive writes | ORM | Access rules enforced |
| Reporting / analytics | Raw SQL | Complex joins, CTEs |
| Record rule-dependent reads | ORM | Row-level security |

## CRITICAL WARNING

**Never update `ir_config_parameter` via raw SQL.** Odoo ORM caches config parameters with a checksum. Raw SQL bypasses the cache and the system will serve stale values even after restart. Always use:

```python
env['ir.config_parameter'].set_param('key', 'value')
env.cr.commit()
```

## Common Query Patterns

### Seller Sales Summary
```sql
SELECT rp.id AS seller_id, rp.name AS seller_name,
       COUNT(DISTINCT so.id) AS total_orders,
       SUM(sol.price_subtotal) AS total_revenue,
       AVG(sol.price_subtotal) AS avg_order_value
FROM sale_order so
JOIN sale_order_line sol ON sol.order_id = so.id
JOIN res_partner rp ON rp.id = so.marketplace_seller_id
WHERE so.state IN ('sale', 'done')
  AND so.date_order >= NOW() - INTERVAL '30 days'
GROUP BY rp.id, rp.name
ORDER BY total_revenue DESC;
```

### Product Performance
```sql
SELECT pt.id, pt.name, pt.list_price,
       COUNT(sol.id) AS times_sold,
       SUM(sol.product_uom_qty) AS units_sold,
       SUM(sol.price_subtotal) AS revenue
FROM product_template pt
JOIN product_product pp ON pp.product_tmpl_id = pt.id
JOIN sale_order_line sol ON sol.product_id = pp.id
JOIN sale_order so ON so.id = sol.order_id AND so.state IN ('sale','done')
GROUP BY pt.id, pt.name, pt.list_price
ORDER BY revenue DESC LIMIT 20;
```

### Wallet Balances
```sql
SELECT sw.id, rp.name AS seller_name, sw.balance,
       sw.total_credited, sw.total_debited,
       (SELECT COUNT(*) FROM seller_wallet_transaction
        WHERE wallet_id = sw.id) AS tx_count
FROM seller_wallet sw
JOIN res_partner rp ON rp.id = sw.seller_id
ORDER BY sw.balance DESC;
```

## Key Tables

| Table | Model | Purpose |
|-------|-------|---------|
| `res_partner` | res.partner | Users, sellers, buyers |
| `seller_shop` | seller.shop | Seller storefronts |
| `product_template` | product.template | Product catalog |
| `sale_order` / `sale_order_line` | sale.order | Orders |
| `seller_wallet` | seller.wallet | Seller wallet balances |
| `seller_wallet_transaction` | seller.wallet.transaction | Wallet ledger |
| `seller_withdrawal_request` | seller.withdrawal.request | Withdrawal requests |
| `seller_payment` | seller.payment | Commission payments |
| `line_channel_member` | line.channel.member | LINE user mappings |
| `ir_config_parameter` | ir.config_parameter | System config (ORM only!) |

## Safety Rules

- Always use parameterized queries: `env.cr.execute("... WHERE id = %s", (val,))`
- Never string-format SQL: `f"WHERE id = {val}"` is an injection risk
- Use `LIMIT` on exploratory queries to avoid full table scans
- Wrap write operations in transactions; Odoo auto-commits per request

## Cross-References

- ~~marketplace-engine for seller and product data models
- ~~wallet for balance and transaction queries
- [marketplace-analytics](../marketplace-analytics/SKILL.md) for KPI queries
- [data-validation](../data-validation/SKILL.md) for integrity check queries
