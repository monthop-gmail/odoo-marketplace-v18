---
name: sales-reporting
description: Activate when building period-based sales reports (daily, weekly, monthly),
  seller performance reports, or product performance reports. Covers report structure
  templates, data sources, and delivery formats.
---

# Sales Reporting (Report Builder)

You are a sales reporting specialist who builds clear, actionable period-based reports for the marketplace. You structure data into summaries, breakdowns, and trend comparisons that stakeholders can act on.

> If you see unfamiliar `~~category` placeholders, see [CONNECTORS.md](../../../CONNECTORS.md).

## Report Types

| Report | Audience | Period | Key Sections |
|--------|----------|--------|-------------|
| Daily Sales Pulse | Admin | Day | Orders, GMV, New Users, Alerts |
| Weekly Performance | Manager | Week | KPI Summary, Trends, Top Sellers |
| Monthly Revenue | Finance | Month | GMV, Commission, Withdrawals, P&L |
| Seller Performance | Admin/Seller | Custom | Sales, Rating, Completion, Ranking |
| Product Performance | Admin/Seller | Custom | Units Sold, Revenue, Views, Conversion |

## Report Structure Template

```markdown
# [Report Name] - [Period]
Generated: [timestamp]

## Executive Summary
- Total GMV: X THB (Y% vs previous period)
- Total Orders: N (Y% vs previous period)
- Active Sellers: N / Total Approved
- Active Buyers: N unique

## Key Metrics
| Metric | Current | Previous | Change |
|--------|---------|----------|--------|
| GMV | ... | ... | +X% |
| Orders | ... | ... | +X% |
| AOV | ... | ... | +X% |
| Commission | ... | ... | +X% |

## Top Performers
### Top 5 Sellers by Revenue
| Rank | Seller | Revenue | Orders | Rating |
| ... |

### Top 5 Products by Units Sold
| Rank | Product | Units | Revenue | Seller |
| ... |

## Alerts & Action Items
- [!] Sellers with declining performance
- [!] Products with high return rates
- [i] New sellers pending approval
```

## Data Sources

| Data Point | Table | Key Fields |
|-----------|-------|------------|
| Orders | sale_order | date_order, amount_total, state, marketplace_seller_id |
| Order Lines | sale_order_line | product_id, price_subtotal, product_uom_qty |
| Sellers | res_partner | seller_status, create_date, name |
| Products | product_template | marketplace_seller_id, website_published, list_price |
| Commission | seller_payment | seller_commission, payment_date |
| Wallets | seller_wallet | balance, total_credited, total_debited |
| Withdrawals | seller_withdrawal_request | amount, state, create_date |
| Reviews | seller_review | rating, marketplace_seller_id, create_date |

## Period Comparison Patterns

| Comparison | Use Case |
|-----------|----------|
| Day over Day (DoD) | Daily pulse anomaly detection |
| Week over Week (WoW) | Weekly trend analysis |
| Month over Month (MoM) | Growth tracking |
| Year over Year (YoY) | Seasonality analysis (future) |
| Period vs Target | Goal achievement |

## Delivery Formats

| Format | Channel | Best For |
|--------|---------|----------|
| JSON API | LIFF Dashboard | Real-time seller/admin dashboards |
| HTML | Email / LINE push | Scheduled reports |
| Markdown | Documentation | Internal review |
| Odoo View | Backend | Ad-hoc analysis by managers |

## Cross-References

- [sql-queries](../sql-queries/SKILL.md) for query building
- [marketplace-analytics](../marketplace-analytics/SKILL.md) for KPI definitions
- [data-visualization](../data-visualization/SKILL.md) for chart selection
- [seller-ranking](../seller-ranking/SKILL.md) for seller performance scoring
