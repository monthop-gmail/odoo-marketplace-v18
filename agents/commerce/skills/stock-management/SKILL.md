---
name: stock-management
description: Inventory and stock picking management. Activate when working on marketplace
  stock levels, stock.picking extensions, warehouse operations, or inventory
  adjustments for multi-vendor products.
---

# Stock Management (การจัดการสต็อก)

You are an expert at inventory management in a multi-vendor marketplace, handling stock levels, warehouse picking operations, and per-seller stock tracking.

> If you see unfamiliar `~~category` placeholders, see [CONNECTORS.md](../../CONNECTORS.md).

## Stock Architecture

```
marketplace.stock (per-seller tracking)
    ↕ sync
product.product.qty_available (Odoo standard)
    ↓
stock.picking (per-seller fulfillment)
    ↓
stock.move (individual product moves)
```

## Key Models

### marketplace.stock
```python
seller_id = fields.Many2one('res.partner')
product_id = fields.Many2one('product.template')
quantity = fields.Float()        # available stock
reserved_quantity = fields.Float()  # reserved for orders
```

### stock.picking (marketplace extension)
```python
marketplace_seller_id = fields.Many2one('res.partner')  # seller who fulfills
sale_id = fields.Many2one('sale.order')                  # source order
```

## Stock Flow

| Step | Trigger | Action |
|------|---------|--------|
| Product created | Seller sets quantity | marketplace.stock record created |
| Order confirmed | sale.order.action_confirm() | stock.picking created per seller |
| Item reserved | Picking assigned | `reserved_quantity` increased |
| Shipped | Seller marks shipped | Picking in transit |
| Delivered | Delivery confirmed | button_validate(), stock decremented |
| Cancelled | Order cancelled | Reserved quantity released |

## Per-Seller Picking Split

When an order has items from multiple sellers:
1. `sale.order.action_confirm()` groups lines by `marketplace_seller_id`
2. Creates separate `stock.picking` for each seller
3. Each seller manages their own fulfillment independently

## Owned Files

| File | Purpose |
|------|---------|
| `core_marketplace/models/stock.py` | marketplace.stock + stock.picking extension |
| `core_marketplace/views/mp_stock_view.xml` | Stock management views |
| `core_marketplace/security/ir.model.access.csv` | Stock model ACL |

## Anti-Patterns

| Don't | Do Instead |
|-------|-----------|
| Update stock with ORM without lock | Use SQL or Odoo's `_update_available_quantity` |
| Let seller A see seller B's stock | Scope all queries by `marketplace_seller_id` |
| Skip reserved quantity on order confirm | Always reserve before fulfillment |
| Create one picking for multi-seller order | Split pickings by seller |

## Cross-References

| Direction | Skill | Interaction |
|-----------|-------|-------------|
| ← | [order-processing](../order-processing/SKILL.md) | Order confirm → create picking |
| → | [delivery-tracking](../delivery-tracking/SKILL.md) | Picking → shipping status |
| ← | [product-lifecycle](../product-lifecycle/SKILL.md) | Product stock quantity display |
