---
name: featured-products
description: Featured product and boost placement system. Activate when working on homepage banners, category featured slots, search boost, new arrival highlights, or paid product promotion placements.
---

# Featured Products (สินค้าแนะนำ)

You manage the product boost and featured placement system — a core revenue stream for the marketplace platform.

> If you see unfamiliar `~~category` placeholders, see [CONNECTORS.md](../../CONNECTORS.md).

## Placement Types

| Placement | Location | Visibility | Revenue Model |
|-----------|----------|-----------|---------------|
| Homepage Banner | Buyer app home top | All buyers | Fixed fee/week |
| Category Featured | Category listing top 3 | Category browsers | Bid per impression |
| Search Boost | Search results priority | Searchers | Cost per click |
| New Arrival | "มาใหม่" section | All buyers | Free (time-limited) |

## Revenue Model Link
Product boost is Revenue Stream #3 in the platform business model:
1. Commission per order (core)
2. Premium Seller subscription
3. **Boost product placement** (this skill)
4. Featured store promotion
5. Affiliate system (future)

## Future Model: `marketplace.product.boost`

| Field | Type | Description |
|-------|------|-------------|
| product_id | Many2one | Boosted product (product.template) |
| seller_id | Many2one | Paying seller (res.partner) |
| placement | Selection | homepage_banner/category_featured/search_boost |
| start_date | Datetime | Boost activation |
| end_date | Datetime | Boost expiration |
| bid_amount | Float | Bid/fee amount in THB |
| impressions | Integer | Times shown to buyers |
| clicks | Integer | Times clicked by buyers |
| orders | Integer | Orders generated |
| status | Selection | draft/active/expired/cancelled |

## Boost Ranking Algorithm

For category featured and search boost, products are ranked by:

```
score = bid_amount * quality_factor

quality_factor = (
    0.4 * click_through_rate +
    0.3 * conversion_rate +
    0.2 * seller_rating +
    0.1 * product_freshness
)
```

Higher quality products get better placement at lower bids, encouraging sellers to maintain product quality.

## Display Rules

| Rule | Logic |
|------|-------|
| Max boosted per page | 3 featured + organic results |
| Label requirement | "แนะนำ" badge on boosted products |
| Rotation | Rotate banners every 5 seconds |
| Fallback | Show organic products if no active boosts |
| Seller cap | Max 2 boosted products per seller per category |

## Seller Self-Service Flow
1. Seller selects product to boost
2. Choose placement type and duration
3. Set bid amount (minimum shown)
4. Preview placement position
5. Confirm and pay from wallet balance
6. Boost activates at start_date

## Anti-Patterns

| Don't | Do Instead |
|-------|-----------|
| Show only boosted products | Mix featured + organic for trust |
| Hide the "แนะนำ" label | Always disclose paid placement |
| Allow indefinite boosts | Require end_date, max 30 days |
| Let low-quality products boost | Apply quality_factor minimum threshold |

## Cross-References
- [campaign-management](../campaign-management/SKILL.md) — Campaign-linked boosts
- [discount-codes](../discount-codes/SKILL.md) — Boost + coupon combos
- [content-strategy](../content-strategy/SKILL.md) — Organic vs paid content balance
