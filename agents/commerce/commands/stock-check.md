# /stock-check

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).

Check stock levels for products, sellers, or the entire marketplace.

## Usage

```
/stock-check <product_name_or_id>   # Specific product stock
/stock-check --low                   # Products below threshold
/stock-check --seller <name>         # All stock for a seller
/stock-check --out-of-stock          # Products with zero stock
```

## How It Works

```
┌─────────────────────────────────────────────────────┐
│                  STOCK CHECK                         │
├─────────────────────────────────────────────────────┤
│  STANDALONE (always works)                           │
│  ✓ Explain marketplace stock management model        │
│  ✓ Describe seller-level stock isolation             │
│  ✓ Show stock threshold recommendations              │
├─────────────────────────────────────────────────────┤
│  SUPERCHARGED (when ~~marketplace-engine connected)  │
│  + Pull real ~~stock data from Odoo                  │
│  + Show per-product on-hand and forecasted qty       │
│  + Identify low-stock and out-of-stock items         │
│  + Show stock movements and incoming shipments       │
│  + Generate restock recommendations                  │
└─────────────────────────────────────────────────────┘
```

## Workflow

1. **Identify Scope** -- Product, seller, or marketplace-wide
2. **Query Stock** -- Pull from ~~stock (stock.quant, product.product)
3. **Analyze** -- Compare against thresholds, identify issues
4. **Report** -- Structured stock report with recommendations

## Stock Model

```
marketplace.stock → stock.quant → product.product
                                      ↓
                               marketplace_seller_id (res.partner)
```

## Output

```markdown
## Stock Report

**Scope:** [product/seller/marketplace]
**Date:** [timestamp]

### Stock Levels
| Product | Seller | On Hand | Forecasted | Reserved | Available | Status |
|---------|--------|---------|-----------|----------|-----------|--------|
| [name] | [seller] | [qty] | [qty] | [qty] | [qty] | OK/LOW/OUT |

### Low Stock Alerts
| Product | Seller | Available | Threshold | Action Needed |
|---------|--------|-----------|-----------|---------------|
| [name] | [seller] | [qty] | [threshold] | Restock [qty] units |

### Out of Stock
| Product | Seller | Last Sold | Days OOS |
|---------|--------|-----------|----------|
| [name] | [seller] | [date] | [days] |

### Summary
| Metric | Count |
|--------|-------|
| Total Products Checked | [n] |
| Healthy Stock | [n] |
| Low Stock | [n] |
| Out of Stock | [n] |
```

## Next Steps

- Want me to notify sellers about low stock items?
- Should I generate a restock report for a specific seller?
- Want to check incoming shipments?

## Related Skills

- Uses [inventory](../skills/inventory/SKILL.md) for stock data
- Uses [product-catalog](../skills/product-catalog/SKILL.md) for product info
- Cross-references [order-management](../skills/order-management/SKILL.md) for demand forecast
