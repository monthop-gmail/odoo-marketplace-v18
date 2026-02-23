---
name: seller-dashboard
description: Seller analytics and performance dashboard. Activate when working on seller sales metrics, order statistics, revenue tracking, or seller performance analytics.
---

# Seller Dashboard (แดชบอร์ดผู้ขาย)

You manage the seller analytics dashboard — providing sellers with insights into their sales performance, order statistics, and revenue metrics.

> If you see unfamiliar `~~category` placeholders, see [CONNECTORS.md](../../CONNECTORS.md).

## Dashboard Metrics

| Metric | Source | Description |
|--------|--------|-------------|
| Total Orders | sale.order.line | Count of seller's order lines |
| Total Revenue | sale.order.line | Sum of seller's order amounts |
| Pending Orders | sale.order.line | Orders not yet shipped |
| Products Listed | product.template | Active product count |
| Average Rating | seller.review | Mean star rating |
| Wallet Balance | seller.wallet | Current balance |

## API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/line-seller/dashboard` | GET | Dashboard summary data |

## Key Model: marketplace.dashboard

Computed model that aggregates seller performance data.

## Owned Files

| File | Purpose |
|------|---------|
| `core_marketplace/models/marketplace_dashboard.py` | Dashboard model |
| `core_marketplace/views/mp_dashboard_view.xml` | Backend dashboard views |

## LIFF Display

Seller LIFF app shows dashboard on the main page:
- Sales summary cards
- Recent orders list
- Quick action buttons (post product, view orders)

## Cross-References

- ← [commerce/order-processing](../../commerce/skills/order-processing/SKILL.md) — Order data feeds dashboard
- ← [finance/wallet-system](../../finance/skills/wallet-system/SKILL.md) — Wallet balance shown
- → [data/marketplace-analytics](../../data/skills/marketplace-analytics/SKILL.md) — Advanced analytics
