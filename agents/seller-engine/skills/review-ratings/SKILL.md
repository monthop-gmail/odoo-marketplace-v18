---
name: review-ratings
description: Customer reviews and star ratings for sellers. Activate when working on review submission, rating display, review moderation, or seller reputation scoring.
---

# Review & Ratings (รีวิวและคะแนน)

You manage customer reviews and star ratings for sellers — enabling trust signals in the marketplace.

> If you see unfamiliar `~~category` placeholders, see [CONNECTORS.md](../../CONNECTORS.md).

## Key Model: seller.review

```python
seller_id = fields.Many2one('res.partner')
customer_id = fields.Many2one('res.partner')
rating = fields.Float()        # 1.0 - 5.0
review_text = fields.Text()
state = fields.Selection()     # draft, published, hidden
```

## Review Flow

```
Buyer completes order → Can submit review → Officer moderates → Published
```

## Rules

- Only buyers who completed an order can review
- One review per buyer per seller
- Reviews can be moderated by Officer/Manager
- Seller cannot delete reviews
- Average rating computed on seller profile

## Owned Files

| File | Purpose |
|------|---------|
| `core_marketplace/models/seller_review.py` | Review model |
| `core_marketplace/views/seller_review_view.xml` | Review backend views |

## Cross-References

- ← [commerce/order-processing](../../commerce/skills/order-processing/SKILL.md) — Reviews only after order completion
- → [data/seller-ranking](../../data/skills/seller-ranking/SKILL.md) — Ratings feed ranking algorithm
