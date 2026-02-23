---
name: pricing-rules
description: Seller pricing and pricelist management. Activate when working on
  mp.pricelist.item, seller-specific pricing, product price overrides, discount
  rules, or marketplace pricing hierarchy.
---

# Pricing Rules (กฎราคา)

You are an expert at managing pricing in a multi-vendor marketplace, handling seller-specific pricelists, discount rules, and the pricing hierarchy that determines the final price shown to buyers.

> If you see unfamiliar `~~category` placeholders, see [CONNECTORS.md](../../CONNECTORS.md).

## Pricing Hierarchy

```
Product Base Price (product.template.list_price)
    ↓ override?
mp.pricelist.item (seller-specific rule)
    ↓ override?
Odoo Pricelist (product.pricelist)
    ↓
Final Display Price
```

Priority: Seller pricelist item > Global pricelist > Base product price.

## Key Model: mp.pricelist.item

```python
class MpPricelistItem(models.Model):
    _name = 'mp.pricelist.item'

    seller_id = fields.Many2one('res.partner')
    product_id = fields.Many2one('product.template')
    price = fields.Float()               # fixed price override
    discount_percentage = fields.Float()  # percentage discount
    min_quantity = fields.Float()         # quantity threshold
    date_start = fields.Date()
    date_end = fields.Date()
```

## Price Resolution Logic

| Check | Condition | Result |
|-------|-----------|--------|
| 1 | Active `mp.pricelist.item` for seller+product | Use item price/discount |
| 2 | Active Odoo `product.pricelist.item` | Use pricelist rule |
| 3 | Fallback | Use `product.template.list_price` |

## Seller Pricing Operations

| Action | Who | Where |
|--------|-----|-------|
| Set base price | Seller (on product form) | `list_price` field |
| Create pricelist rule | Seller / Admin | mp.pricelist.item |
| View effective price | Buyer | Product listing API |
| Override pricing | Admin/Manager | Backend or Admin API |

## Owned Files

| File | Purpose |
|------|---------|
| `core_marketplace/models/mp_pricelist_item.py` | Seller pricelist item model |
| `core_marketplace/views/mp_pricelist_view.xml` | Pricelist management views |

## Anti-Patterns

| Don't | Do Instead |
|-------|-----------|
| Let sellers modify Odoo global pricelists | Use `mp.pricelist.item` for seller rules |
| Show different prices to same buyer role | Pricing is deterministic per product+qty+date |
| Skip date range validation | Always check `date_start`/`date_end` |
| Allow negative prices | Validate `price >= 0` |

## Cross-References

| Direction | Skill | Interaction |
|-----------|-------|-------------|
| ← | [product-lifecycle](../product-lifecycle/SKILL.md) | Product price set on creation |
| ← | [order-processing](../order-processing/SKILL.md) | Price resolved at cart/checkout |
| ← | [commission-engine](../../../finance/skills/commission-engine/SKILL.md) | Commission calculated on final price |
