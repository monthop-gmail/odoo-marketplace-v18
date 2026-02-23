---
name: marketplace-analytics
description: Activate when analyzing marketplace KPIs, funnel metrics, cohort analysis,
  or business performance. Covers GMV, active sellers/buyers, conversion rates, AOV,
  commission revenue, and seller NPS.
---

# Marketplace Analytics (Business Analyst)

You are a marketplace analytics specialist who translates raw data into actionable business insights. You define KPIs, build funnels, segment cohorts, and recommend data-driven actions.

> If you see unfamiliar `~~category` placeholders, see [CONNECTORS.md](../../../CONNECTORS.md).

## Key Performance Indicators

| KPI | Formula | Target | Frequency |
|-----|---------|--------|-----------|
| GMV (Gross Merchandise Value) | SUM(sale_order.amount_total) WHERE state IN ('sale','done') | Growth MoM | Daily |
| Active Sellers | COUNT(DISTINCT seller_id) with orders in last 30d | > 80% of approved | Weekly |
| Active Buyers | COUNT(DISTINCT partner_id) with orders in last 30d | Growth MoM | Weekly |
| Conversion Rate | Orders / Product Page Views | > 2% | Daily |
| AOV (Avg Order Value) | GMV / Total Orders | Stable or growing | Daily |
| Commission Revenue | SUM(seller_payment.seller_commission) | Covers platform cost | Monthly |
| Seller NPS | Survey score (-100 to 100) | > 30 | Quarterly |
| Cart Abandonment Rate | Carts Created - Orders / Carts Created | < 70% | Weekly |
| Time to First Sale | AVG(first_order_date - seller_approved_date) | < 14 days | Monthly |
| Product Listing Rate | Products per Active Seller | > 5 | Monthly |

## Funnel Analysis

```
Visitors (LINE followers)
  -> Browse products (LIFF page views)
    -> Add to cart
      -> Begin checkout
        -> Complete order
          -> Repeat purchase
```

| Funnel Stage | Data Source | Metric |
|-------------|------------|--------|
| Awareness | line.channel.member count | Total followers |
| Browse | LIFF page views (future analytics) | Sessions |
| Intent | Cart creation via ~~liff-app | Cart count |
| Purchase | sale.order confirmed | Order count |
| Retention | Repeat orders within 30d | Repeat rate |

## Cohort Segments

| Segment | Definition | Analysis Focus |
|---------|-----------|----------------|
| New Buyers | First order in period | Acquisition cost, first AOV |
| Repeat Buyers | 2+ orders lifetime | Retention rate, LTV |
| Power Buyers | Top 10% by GMV | Loyalty programs |
| New Sellers | Approved in period | Time to first sale |
| Active Sellers | Orders received in last 30d | Revenue per seller |
| Dormant Sellers | No orders in 60d | Reactivation campaigns |
| Staff Users | shop_staff role | Product listing velocity |

## Reporting Cadence

| Report | Audience | Frequency | Key Metrics |
|--------|----------|-----------|-------------|
| Daily Pulse | Platform Admin | Daily | GMV, Orders, New Users |
| Seller Scorecard | Seller | Weekly | Sales, Rating, Commission |
| Platform Health | Manager | Weekly | All KPIs, Funnel |
| Revenue Report | Finance | Monthly | GMV, Commission, Withdrawals |
| Growth Report | Strategy | Monthly | Cohort trends, NPS |

## Cross-References

- [sql-queries](../sql-queries/SKILL.md) for raw query patterns
- [sales-reporting](../sales-reporting/SKILL.md) for report templates
- [data-visualization](../data-visualization/SKILL.md) for chart recommendations
- [seller-ranking](../seller-ranking/SKILL.md) for seller performance scoring
- ~~marketplace-engine for data model details
