---
name: commerce
description: Product and order lifecycle management. Activate when working on product
  creation/approval, order processing, stock/inventory, pricing, delivery, cart operations,
  checkout flow, or marketplace product moderation.
---

# S2: Commerce (ระบบการค้า)

You are an expert at managing the product and order lifecycle in a multi-vendor marketplace. You handle product creation and approval, order processing with per-seller line splitting, stock management, pricing, and delivery workflows.

> If you see unfamiliar `~~category` placeholders, see [CONNECTORS.md](../../CONNECTORS.md).

## Product Lifecycle

```
Seller creates → pending review → Officer approves → published on website
                                → Officer rejects → back to seller
```

| State | Who Can Act | Next States |
|-------|------------|-------------|
| Draft | Seller | → Pending |
| Pending | Officer/Manager | → Approved, → Rejected |
| Approved | Officer/Manager | → Published, → Pending |
| Rejected | Seller (edit & resubmit) | → Pending |
| Published | Officer/Manager | → Unpublished |

## Order Flow

```
LIFF browse → add to cart → checkout → sale.order → stock.picking → delivered → invoiced
```

| Stage | Key Action | Model |
|-------|-----------|-------|
| Cart | Add/update/remove items | sale.order (draft) via ~~api |
| Checkout | Place order, select address | sale.order.confirm() |
| Processing | Split order lines per seller | sale.order.line.marketplace_seller_id |
| Shipping | Create stock.picking per seller | ~~stock |
| Delivery | Mark delivered | stock.picking.button_validate() |
| Invoice | Generate invoice | account.move via ~~payment |

## Owned Files

### Models (~~marketplace-engine)
| File | Model | Purpose |
|------|-------|---------|
| `core_marketplace/models/marketplace_product.py` | product.template (ext) | Multi-vendor products |
| `core_marketplace/models/sale.py` | sale.order / sale.order.line (ext) | Marketplace orders |
| `core_marketplace/models/stock.py` | marketplace.stock / stock.picking (ext) | Inventory & delivery |
| `core_marketplace/models/mp_pricelist_item.py` | mp.pricelist.item | Seller pricing rules |
| `core_marketplace/models/ir_attachment.py` | ir.attachment (ext) | Product image handling |

### Views
| File | Purpose |
|------|---------|
| `views/mp_product_view.xml` | Product management |
| `views/mp_sol_view.xml` | Sale order line views |
| `views/mp_stock_view.xml` | Stock management |
| `views/website_mp_product_template.xml` | Product frontend |

## Key Data Models

### product.template (marketplace extension)
```python
marketplace_seller_id = fields.Many2one('res.partner')
status = fields.Selection()  # pending, approved, rejected
website_published = fields.Boolean()
```

### sale.order.line (marketplace extension)
```python
marketplace_seller_id = fields.Many2one('res.partner')
marketplace_state = fields.Selection()  # new, pending, shipped, delivered
```

## Product API (via ~~api)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/line-buyer/products` | GET | List products (paginated, filterable) |
| `/api/line-buyer/products/<id>` | GET | Product detail with images[] |
| `/api/line-buyer/products/categories` | GET | Category list |
| `/api/line-seller/products` | GET | Seller's own products |
| `/api/line-seller/products` | POST | Create product (accepts `categ_name` for auto-create) |
| `/api/line-seller/products/<id>` | PUT | Update product |
| `/api/line-seller/products/<id>/images` | GET/POST/PUT/DELETE | Gallery management |

## Cart Bug Fix (critical knowledge)

Products API returns `product.template.id`, but cart operations need `product.product` (variant).
Always browse `product.template` first, then get `.product_variant_id` for cart line creation.

## Interfaces

| Direction | Agent | What |
|-----------|-------|------|
| ← | [seller-engine](../seller-engine/SKILL.md) | Only approved sellers create products |
| → | [commission-wallet](../commission-wallet/SKILL.md) | Order confirmed → trigger commission |
| ← | [line-integration](../line-integration/SKILL.md) | New order → ~~messaging to seller |
| ← | [liff-frontend](../liff-frontend/SKILL.md) | Product/cart/checkout/order APIs |

## Anti-Patterns

| Don't | Do Instead |
|-------|-----------|
| Browse `product.product` with template ID | Browse `product.template` → `.product_variant_id` |
| Skip seller scoping on product queries | Always filter by `marketplace_seller_id` |
| Let sellers see other sellers' products in API | Use record rules + domain filters |
| Skip product approval step | Always require Officer/Manager approval |
| Create category without dedup | Check existing by name before creating |

## Related Commands

- [/review-product](../../commands/review-product.md) — Product moderation workflow
- [/quick-post](../../commands/quick-post.md) — Mobile-first product posting
