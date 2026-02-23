---
name: campaign-management
description: Marketing campaign management. Activate when working on LINE broadcasts, featured banners, flash sales, spotlight promotions, campaign scheduling, or campaign performance metrics.
---

# Campaign Management (จัดการแคมเปญ)

You manage marketing campaigns that drive traffic and sales across the marketplace platform.

> If you see unfamiliar `~~category` placeholders, see [CONNECTORS.md](../../CONNECTORS.md).

## Campaign Types

| Type | Channel | Purpose | Audience |
|------|---------|---------|----------|
| LINE Broadcast | ~~messaging | Push message to segmented users | Buyers by behavior |
| Featured Banner | LIFF Home | Hero banner on buyer app homepage | All buyers |
| Flash Sale | LIFF + LINE | Time-limited discounts with countdown | All buyers |
| Spotlight | LIFF Category | Promoted seller/product in category | Category browsers |

## Campaign Lifecycle

```
Draft → Scheduled → Active → Completed
  ↓                   ↓
Cancelled          Paused → Active (resume)
```

## Future Model: `marketplace.campaign`

| Field | Type | Description |
|-------|------|-------------|
| name | Char | Campaign name |
| campaign_type | Selection | broadcast/banner/flash_sale/spotlight |
| status | Selection | draft/scheduled/active/paused/completed/cancelled |
| start_date | Datetime | Activation time |
| end_date | Datetime | Expiration time |
| target_segment | Selection | all/new_buyers/repeat_buyers/vip/sellers |
| product_ids | Many2many | Products included in campaign |
| seller_ids | Many2many | Sellers included in campaign |
| discount_pct | Float | Discount percentage (flash sale) |
| banner_image | Binary | Banner image (featured banner) |
| line_message_id | Many2one | LINE broadcast message template |
| budget | Float | Campaign budget |
| spent | Float | Amount spent so far |

## Key Metrics

| Metric | Description | Source |
|--------|-------------|--------|
| Reach | Users who saw the campaign | ~~messaging delivery reports |
| Click-through | Users who clicked CTA | LIFF page visit logs |
| Conversion | Orders placed from campaign | Order source tracking |
| Revenue | Total sales from campaign | ~~marketplace-engine |
| ROI | Revenue / Budget ratio | Calculated |

## LINE Broadcast Campaign Flow
1. Create campaign (draft)
2. Select target segment (buyer behavior / location / history)
3. Compose message (text + image + CTA button)
4. Schedule send time
5. System sends via ~~messaging at scheduled time
6. Track delivery + read + click metrics

## Decision Table

| Situation | Action |
|-----------|--------|
| New product launch | Featured Banner + LINE Broadcast |
| Slow-selling inventory | Flash Sale with countdown |
| New seller onboarding | Spotlight in relevant category |
| Holiday/seasonal event | Combined: Banner + Flash Sale + Broadcast |
| Re-engage dormant buyers | Targeted LINE Broadcast with coupon |

## Anti-Patterns

| Don't | Do Instead |
|-------|-----------|
| Broadcast to all users indiscriminately | Segment by behavior and preferences |
| Run flash sales without stock check | Verify inventory before scheduling |
| Skip A/B testing | Test message variants on small segment first |
| Forget timezone | All times in Asia/Bangkok (ICT) |

## Cross-References
- [discount-codes](../discount-codes/SKILL.md) — Coupon integration with campaigns
- [featured-products](../featured-products/SKILL.md) — Product boost placements
- [content-strategy](../content-strategy/SKILL.md) — 80/20 content balance
- [social-media](../social-media/SKILL.md) — Cross-platform promotion
