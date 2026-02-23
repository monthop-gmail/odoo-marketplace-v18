# /order-status

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).

Check order details, items, and fulfillment status.

## Usage

```
/order-status <order_id>       # Specific order (SO number or ID)
/order-status --recent          # Recent orders (last 7 days)
/order-status --pending         # Orders awaiting fulfillment
/order-status --seller <name>   # Orders for a specific seller
```

## How It Works

```
┌─────────────────────────────────────────────────────┐
│                  ORDER STATUS                        │
├─────────────────────────────────────────────────────┤
│  STANDALONE (always works)                           │
│  ✓ Explain order lifecycle and states                │
│  ✓ Describe multi-vendor order splitting             │
│  ✓ Show commission calculation logic                 │
├─────────────────────────────────────────────────────┤
│  SUPERCHARGED (when ~~marketplace-engine connected)  │
│  + Pull real order data from Odoo (sale.order)       │
│  + Show line items grouped by seller                 │
│  + Show ~~stock picking and delivery status          │
│  + Show ~~payment and commission breakdown           │
│  + Track fulfillment per seller                      │
└─────────────────────────────────────────────────────┘
```

## Order Lifecycle

```
draft → sent → sale → done
                 ↓
              cancel
```

## Workflow

1. **Fetch Order** -- Pull from ~~marketplace-engine (sale.order)
2. **Group by Seller** -- Split order lines by marketplace_seller_id
3. **Check Fulfillment** -- Query ~~stock for picking/delivery status
4. **Commission** -- Calculate platform commission per seller
5. **Report** -- Structured order details

## Output

```markdown
## Order Details

**Order:** [SO-xxx] (id: [id])
**Customer:** [name] (partner_id: [id])
**Date:** [date]
**Status:** [state]
**Payment:** [payment_status]

### Items by Seller
#### Seller: [seller_name]
| Product | Qty | Unit Price | Subtotal | Commission |
|---------|-----|-----------|----------|------------|
| [name] | [qty] | ฿[price] | ฿[subtotal] | ฿[comm] |
| **Subtotal** | | | **฿[total]** | **฿[comm_total]** |

#### Seller: [seller_name_2]
| Product | Qty | Unit Price | Subtotal | Commission |
|---------|-----|-----------|----------|------------|
| [name] | [qty] | ฿[price] | ฿[subtotal] | ฿[comm] |

### Order Summary
| Metric | Amount |
|--------|--------|
| Subtotal | ฿[amount] |
| Tax | ฿[amount] |
| Total | ฿[amount] |
| Platform Commission | ฿[amount] |
| Seller Earnings | ฿[amount] |

### Fulfillment
| Seller | Picking | Status | Tracking |
|--------|---------|--------|----------|
| [name] | [picking_ref] | [status] | [tracking_no] |
```

## Next Steps

- Want to see the delivery tracking details?
- Should I check the commission settlement for this order?
- Want to contact the buyer or seller about this order?

## Related Skills

- Uses [order-management](../skills/order-management/SKILL.md) for order lifecycle
- Uses [inventory](../skills/inventory/SKILL.md) for fulfillment tracking
- Cross-references [commission](../../finance/CONNECTORS.md) for earnings
