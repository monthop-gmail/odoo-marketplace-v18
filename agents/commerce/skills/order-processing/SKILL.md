---
name: order-processing
description: Order lifecycle from cart to delivery and invoicing. Activate when working
  on cart operations, checkout, sale.order processing, per-seller line splitting,
  order confirmation, or order status tracking.
---

# Order Processing (การประมวลผลคำสั่งซื้อ)

You are an expert at managing the order lifecycle in a multi-vendor marketplace, from LIFF cart operations through checkout, per-seller order splitting, stock fulfillment, and invoicing.

> If you see unfamiliar `~~category` placeholders, see [CONNECTORS.md](../../CONNECTORS.md).

## Order Flow

```
LIFF Browse → Add to Cart → Checkout → sale.order (confirmed)
    → stock.picking per seller → Delivered → Invoice → Commission
```

| Stage | Action | Model | Trigger |
|-------|--------|-------|---------|
| Browse | View products | product.template | ~~api GET |
| Cart | Add/update/remove | sale.order (draft) | ~~api POST |
| Checkout | Select address, confirm | sale.order.action_confirm() | ~~api POST |
| Processing | Split lines per seller | sale.order.line | Automatic on confirm |
| Shipping | Create picking per seller | stock.picking | ~~stock |
| Delivery | Mark delivered | stock.picking.button_validate() | Seller/Admin action |
| Invoice | Generate invoice | account.move | ~~payment |

## Cart Bug Fix (Critical Knowledge)

**Problem**: Products API returns `product.template.id`, but `product.product.browse(template_id)` returns wrong product.

**Fix in `api_cart.py:add_to_cart`**:
```python
# WRONG: product = env['product.product'].browse(product_id)
# RIGHT:
template = env['product.template'].browse(product_id)
variant = template.product_variant_id  # gets correct variant
```

Example: Template 40 (Warranty) → Variant 52 (correct), NOT Variant 40 (Desk Organizer).

## Per-Seller Line Splitting

Each `sale.order.line` carries `marketplace_seller_id`. On order confirmation:
1. Lines are grouped by seller
2. Separate `stock.picking` created per seller
3. Commission calculated per seller's rate

## API Endpoints (via ~~api)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/line-buyer/cart` | GET | Current cart contents |
| `/api/line-buyer/cart/add` | POST | Add item (uses template→variant resolution) |
| `/api/line-buyer/cart/update` | PUT | Update quantity |
| `/api/line-buyer/cart/remove` | DELETE | Remove item |
| `/api/line-buyer/checkout` | POST | Place order |
| `/api/line-buyer/orders` | GET | Order history |
| `/api/line-buyer/orders/<id>` | GET | Order detail |
| `/api/line-seller/orders` | GET | Seller's received orders |
| `/api/line-admin/orders` | GET | All marketplace orders |

## Owned Files

| File | Model / Purpose |
|------|----------------|
| `core_marketplace/models/sale.py` | sale.order + sale.order.line marketplace extensions |
| `core_line_integration/controllers/api_cart.py` | Cart operations (add/update/remove) |
| `core_line_integration/controllers/api_checkout.py` | Checkout and order placement |
| `core_line_integration/controllers/api_orders.py` | Order listing and detail |
| `core_marketplace/views/mp_sol_view.xml` | Backend order line views |

## Anti-Patterns

| Don't | Do Instead |
|-------|-----------|
| Browse `product.product` with template ID | Browse `product.template` → `.product_variant_id` |
| Skip seller scoping on order queries | Filter by `marketplace_seller_id` for seller API |
| Modify confirmed orders directly | Use proper cancellation flow |
| Create single picking for multi-seller order | Split by seller for independent fulfillment |

## Cross-References

| Direction | Skill | Interaction |
|-----------|-------|-------------|
| ← | [product-lifecycle](../product-lifecycle/SKILL.md) | Only published products in cart |
| → | [stock-management](../stock-management/SKILL.md) | Order confirm → stock picking |
| → | [commission-engine](../../../finance/skills/commission-engine/SKILL.md) | Order complete → commission calc |
| → | [delivery-tracking](../delivery-tracking/SKILL.md) | Picking created → delivery tracking |
| ← | [messaging-api](../../../line-platform/skills/messaging-api/SKILL.md) | Order events → LINE notifications |
