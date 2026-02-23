---
name: seller-ranking
description: Activate when designing or querying seller performance scoring, ranking
  algorithms, tier assignments, or seller quality metrics. Covers weighted scoring,
  tier thresholds, and promotion/demotion rules.
---

# Seller Ranking (Performance Analyst)

You are a seller performance scoring specialist who designs fair, transparent ranking algorithms that incentivize quality sellers and protect buyers from poor experiences.

> If you see unfamiliar `~~category` placeholders, see [CONNECTORS.md](../../../CONNECTORS.md).

## Ranking Factors

| Factor | Weight | Source | Measurement |
|--------|--------|--------|-------------|
| Rating | 30% | seller.review avg_rating | Average buyer rating (1-5 stars) |
| Order Completion | 25% | sale.order completed / total | % of orders fulfilled successfully |
| Response Time | 15% | Future: support ticket response | Avg hours to first response |
| Product Quality | 15% | Returns / total orders | % return rate (lower is better) |
| Activity Level | 15% | Products listed + orders in 30d | Active engagement score |

## Scoring Formula

```
score = (rating_norm * 0.30) +
        (completion_norm * 0.25) +
        (response_norm * 0.15) +
        (quality_norm * 0.15) +
        (activity_norm * 0.15)

# Normalization: each factor scaled to 0-100
rating_norm = (avg_rating / 5.0) * 100
completion_norm = (completed_orders / total_orders) * 100
response_norm = max(0, 100 - (avg_response_hours * 2))
quality_norm = max(0, 100 - (return_rate * 500))
activity_norm = min(100, (products_listed * 2) + (orders_30d * 10))
```

## Seller Tiers

| Tier | Score Range | Badge | Benefits |
|------|------------|-------|----------|
| Gold | 80 - 100 | Gold badge | Featured placement, lower commission rate |
| Silver | 60 - 79 | Silver badge | Standard placement, standard commission |
| Bronze | 40 - 59 | Bronze badge | Standard placement, standard commission |
| Probation | 0 - 39 | Warning icon | Restricted visibility, review required |

## Promotion and Demotion Rules

| Rule | Condition | Action |
|------|-----------|--------|
| Promotion | Score above tier threshold for 2 consecutive weeks | Move up one tier |
| Demotion | Score below tier threshold for 2 consecutive weeks | Move down one tier |
| Instant Demotion | Completion rate < 50% in any week | Drop to Probation |
| Suspension | Probation for 4 consecutive weeks | Account review by Officer |
| New Seller Grace | First 30 days after approval | Minimum Bronze tier |

## SQL: Calculate Seller Scores

```sql
WITH seller_metrics AS (
    SELECT rp.id AS seller_id, rp.name,
        COALESCE(AVG(sr.rating), 3.0) AS avg_rating,
        COUNT(CASE WHEN so.state = 'done' THEN 1 END)::float /
            NULLIF(COUNT(so.id), 0) * 100 AS completion_pct,
        COUNT(DISTINCT CASE WHEN so.date_order >= NOW() - INTERVAL '30d'
            THEN so.id END) AS orders_30d,
        COUNT(DISTINCT pt.id) AS products_listed
    FROM res_partner rp
    LEFT JOIN seller_review sr ON sr.marketplace_seller_id = rp.id
    LEFT JOIN sale_order so ON so.marketplace_seller_id = rp.id
    LEFT JOIN product_template pt ON pt.marketplace_seller_id = rp.id
        AND pt.website_published = true
    WHERE rp.seller_status = 'approved'
    GROUP BY rp.id, rp.name
)
SELECT seller_id, name,
    ROUND((avg_rating / 5.0 * 30) +
          (COALESCE(completion_pct, 50) * 0.25) +
          (LEAST(100, products_listed * 2 + orders_30d * 10) * 0.15)
    , 1) AS score
FROM seller_metrics
ORDER BY score DESC;
```

## Display Locations

| Location | Format | Update Frequency |
|----------|--------|-----------------|
| Seller LIFF Dashboard | Tier badge + score | Real-time |
| Admin LIFF Seller List | Score column, sortable | Hourly |
| Buyer Product Card | Seller tier badge | Cached 1h |
| Odoo Backend | Full metrics table | On demand |

## Cross-References

- [marketplace-analytics](../marketplace-analytics/SKILL.md) for KPI context
- [sql-queries](../sql-queries/SKILL.md) for query patterns
- ~~marketplace-engine for seller data model
- [dashboard-builder](../dashboard-builder/SKILL.md) for visual display
