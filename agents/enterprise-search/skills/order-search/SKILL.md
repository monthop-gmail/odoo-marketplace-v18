---
name: order-search
description: Activate when searching for orders in the marketplace. Covers search
  fields, status filtering, date ranges, role-specific access (buyer sees own,
  seller sees own shop, admin sees all), and API endpoints.
---

# Order Search (Order Lookup Specialist)

You are an order search specialist who queries marketplace orders by ID, buyer, seller, status, date, and amount, with strict role-based access ensuring buyers see only their own orders and sellers see only their shop's orders.

> If you see unfamiliar `~~category` placeholders, see [CONNECTORS.md](../../../CONNECTORS.md).

## Search Fields

| Field | DB Column | Type | Buyer | Seller | Admin |
|-------|-----------|------|-------|--------|-------|
| Order ID | `sale_order.name` | Text (exact) | Own | Own shop | All |
| Buyer Name | `sale_order.partner_id` | Many2one | Own only | Read | Search |
| Seller | `sale_order.marketplace_seller_id` | Many2one | N/A | Own only | Search |
| Status | `sale_order.state` | Selection | Filter | Filter | Filter |
| Date Range | `sale_order.date_order` | Date | Filter | Filter | Filter |
| Amount | `sale_order.amount_total` | Float range | N/A | Filter | Filter |
| Product | `sale_order_line.product_id` | Many2one | N/A | N/A | Search |
| Payment Status | `sale_order.invoice_status` | Selection | View | View | Filter |

## API Endpoints by Role

### Buyer
| Endpoint | Method | Parameters |
|----------|--------|-----------|
| `/api/line-buyer/orders` | GET | `status`, `page`, `limit` |
| `/api/line-buyer/orders/<id>` | GET | -- |

### Seller
| Endpoint | Method | Parameters |
|----------|--------|-----------|
| `/api/line-seller/orders` | GET | `status`, `date_from`, `date_to`, `page`, `limit` |
| `/api/line-seller/orders/<id>` | GET | -- |
| `/api/line-seller/orders/<id>/confirm` | POST | -- |

### Admin
| Endpoint | Method | Parameters |
|----------|--------|-----------|
| `/api/line-admin/orders` | GET | `search`, `seller_id`, `status`, `date_from`, `date_to`, `min_amount`, `max_amount`, `page`, `limit` |
| `/api/line-admin/orders/<id>` | GET | -- |

## Order Status Values

| State | Label | Meaning |
|-------|-------|---------|
| `draft` | Quotation | Cart / not confirmed |
| `sent` | Quotation Sent | Awaiting buyer confirmation |
| `sale` | Sales Order | Confirmed, processing |
| `done` | Done | Completed and delivered |
| `cancel` | Cancelled | Cancelled by buyer or admin |

## Access Control Rules

| Role | Domain Filter | Enforcement |
|------|--------------|-------------|
| Buyer | `partner_id = current_user.partner_id` | API + record rule |
| Seller | `marketplace_seller_id = seller_partner` | API + `require_seller` decorator |
| Staff | Same as seller (resolved via context switch) | `require_seller` resolves owner |
| Admin | No filter (all orders) | `require_admin` decorator |

## Search Domain Pattern

```python
# Buyer: own orders only
domain = [('partner_id', '=', buyer_partner.id)]

# Seller: own shop orders
domain = [('marketplace_seller_id', '=', seller_partner.id)]

# Common filters
if status:
    domain += [('state', '=', status)]
if date_from:
    domain += [('date_order', '>=', date_from)]
if date_to:
    domain += [('date_order', '<=', date_to)]
```

## Response Format

```json
{
  "success": true,
  "data": {
    "orders": [
      {"id": 1, "name": "S00001", "date": "2026-02-23",
       "amount_total": 1299.00, "state": "sale",
       "lines": [{"product": "...", "qty": 1, "subtotal": 1299.00}]}
    ],
    "total": 45, "page": 1
  }
}
```

## Cross-References

- [product-search](../product-search/SKILL.md) for product lookup in order lines
- [seller-search](../seller-search/SKILL.md) for seller context
- [cross-model-search](../cross-model-search/SKILL.md) for combined queries
- ~~marketplace-engine for order model details
- ~~stock for delivery status
