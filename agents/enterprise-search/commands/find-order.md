# /find-order

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).

Find and display full order details including items, seller info, and shipping status.

## Usage

```
/find-order <order_id>
/find-order SO-1234
/find-order --buyer "Jacks Sparrow"     # Find by buyer name
/find-order --seller "ร้านใหม่"          # Find by seller
/find-order --status pending             # Find by status
/find-order --recent 10                  # Last 10 orders
```

## How It Works

```
┌─────────────────────────────────────────────────────┐
│                  FIND ORDER                          │
├─────────────────────────────────────────────────────┤
│  STANDALONE (always works)                           │
│  ✓ Explain order status flow and fields              │
│  ✓ Build query from search criteria                  │
│  ✓ Format order detail template                      │
├─────────────────────────────────────────────────────┤
│  SUPERCHARGED (when ~~marketplace-engine connected)  │
│  + Query sale.order by ID, buyer, seller, or status  │
│  + Pull sale.order.line for item details             │
│  + Resolve seller via marketplace_seller_id          │
│  + Check stock.picking for shipping status           │
│  + Look up payment status from account.move          │
└─────────────────────────────────────────────────────┘
```

## Order Status Flow

```
draft → sent → sale → done
                 ↘ cancel
```

| Status | Description | Thai |
|--------|-------------|------|
| `draft` | Quotation created | ใบเสนอราคา |
| `sent` | Quotation sent to customer | ส่งใบเสนอราคา |
| `sale` | Confirmed order | ยืนยันแล้ว |
| `done` | Completed and delivered | เสร็จสมบูรณ์ |
| `cancel` | Cancelled | ยกเลิก |

## Lookup Strategies

| Input | Query |
|-------|-------|
| Order ID (SO-1234) | `sale.order WHERE name = 'SO-1234'` |
| Buyer name | `sale.order WHERE partner_id.name ILIKE '%name%'` |
| Seller name | `sale.order.line WHERE product_id.marketplace_seller_id.name ILIKE` |
| Status | `sale.order WHERE state = 'status'` |
| Recent | `sale.order ORDER BY date_order DESC LIMIT n` |

## Output

```markdown
## Order Details

**Order:** [SO-number]
**Date:** [date]
**Status:** [status]

### Customer
| Field | Value |
|-------|-------|
| Name | [name] |
| Partner ID | [id] |
| Phone | [phone] |
| Address | [address] |

### Items
| # | Product | Seller | Qty | Unit Price | Subtotal |
|---|---------|--------|-----|-----------|----------|
| 1 | [name] | [seller] | [qty] | ฿[price] | ฿[subtotal] |

### Totals
| | Amount |
|--|--------|
| Subtotal | ฿[amount] |
| Tax | ฿[tax] |
| **Total** | **฿[total]** |

### Shipping
| Field | Value |
|-------|-------|
| Carrier | [carrier] |
| Tracking | [number] |
| Status | [status] |
| Expected Delivery | [date] |
```

## Next Steps

- Want to see the payment details for this order?
- Should I check the shipping tracking?
- Want to contact the buyer or seller about this order?

## Related Skills

- Uses [enterprise-search](../skills/) for order lookup logic
- Cross-references [commerce](../../commerce/skills/) for order models
- Cross-references [finance](../../finance/skills/) for payment status
