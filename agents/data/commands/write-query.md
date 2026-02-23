# /write-query

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).

Write a safe, optimized PostgreSQL query for marketplace data analysis.

## Usage

```
/write-query "ยอดขายรายเดือนแยกตามผู้ขาย"
/write-query "top 10 สินค้าขายดี"
/write-query "สถานะ wallet ทุก seller"
```

## How It Works

```
┌─────────────────────────────────────────────────────┐
│                  WRITE QUERY                         │
├─────────────────────────────────────────────────────┤
│  STANDALONE (always works)                           │
│  ✓ Translate Thai/English description to SQL         │
│  ✓ Use correct Odoo table and column names           │
│  ✓ Add safety guards (LIMIT, read-only)              │
│  ✓ Explain query logic step by step                  │
├─────────────────────────────────────────────────────┤
│  SUPERCHARGED (when ~~marketplace-engine connected)  │
│  + Validate table/column names against actual schema │
│  + Execute query and return results                  │
│  + Format output as markdown table                   │
│  + Suggest indexes for slow queries                  │
└─────────────────────────────────────────────────────┘
```

## Table Reference

| Table | Key Columns | Purpose |
|-------|------------|---------|
| `res_partner` | id, name, email, seller_status, marketplace_seller_id | Customers and sellers |
| `product_template` | id, name, list_price, categ_id, marketplace_seller_id | Product catalog |
| `product_product` | id, product_tmpl_id | Product variants |
| `sale_order` | id, name, partner_id, amount_total, state, date_order | Orders |
| `sale_order_line` | id, order_id, product_id, price_subtotal, product_uom_qty | Order lines |
| `seller_wallet` | id, seller_id, balance | Seller wallet balances |
| `seller_wallet_transaction` | id, wallet_id, amount, transaction_type, state | Wallet transactions |
| `seller_withdrawal_request` | id, wallet_id, amount, state | Withdrawal requests |
| `seller_payment` | id, seller_id, payment_method, state | Seller commission payments |
| `seller_shop` | id, seller_id, name, url_handler | Seller shops |

## Safety Rules

| Rule | Reason |
|------|--------|
| Always include `LIMIT` | Prevent runaway queries |
| SELECT only (no INSERT/UPDATE/DELETE) | Read-only analysis |
| Use explicit column names | Avoid `SELECT *` |
| Add `WHERE` filters | Reduce scan scope |

## Warning: ir_config_parameter

```
NEVER update ir_config_parameter via raw SQL.
Odoo ORM cache won't invalidate. Use Odoo shell instead:
env['ir.config_parameter'].set_param(key, value)
```

## Output

```markdown
## Query: [description]

### SQL
\`\`\`sql
SELECT ...
FROM ...
WHERE ...
ORDER BY ...
LIMIT ...;
\`\`\`

### Explanation
1. [What the query does step by step]

### Results
| col1 | col2 | col3 |
|------|------|------|
| [data] | [data] | [data] |
```

## Next Steps

- Want me to run this query?
- Should I add more filters or aggregations?
- Want to save this as a recurring report?

## Related Skills

- Uses [data](../skills/) for schema knowledge and query patterns
- Cross-references [commerce](../../commerce/skills/) for order models
- Cross-references [finance](../../finance/skills/) for financial models
