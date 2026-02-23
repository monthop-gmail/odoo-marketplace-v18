---
name: financial-reporting
description: Revenue reports and financial metrics. Activate when working on
  GMV calculation, platform revenue reports, seller payout summaries, commission
  reports, dashboard KPIs, or financial analytics.
---

# Financial Reporting (รายงานการเงิน)

You are an expert at financial reporting and analytics in a multi-vendor marketplace, providing insights on GMV, platform revenue, commission collections, seller payouts, and overall financial health.

> If you see unfamiliar `~~category` placeholders, see [CONNECTORS.md](../../CONNECTORS.md).

## Key Financial Metrics

| Metric | Formula | Source |
|--------|---------|--------|
| **GMV** (Gross Merchandise Value) | Sum of confirmed order totals | sale.order (confirmed+) |
| **Platform Revenue** | Sum of commission amounts | seller.payment |
| **Seller Payouts** | Sum of completed withdrawals | seller.withdrawal.request |
| **Net Revenue** | Platform Revenue - Operating Costs | Computed |
| **Commission Rate (avg)** | Platform Revenue / GMV x 100 | Computed |
| **Wallet Outstanding** | Sum of wallet balances | seller.wallet |

## Report Types

### 1. Commission Summary
```
Period: [date range]
Total GMV: xxx THB
Total Commission: xxx THB (avg rate: x%)
Total Seller Payments: xxx THB
```

### 2. Seller Performance
```
Per seller:
  - Orders: count
  - GMV: xxx THB
  - Commission paid: xxx THB
  - Wallet balance: xxx THB
  - Pending withdrawals: xxx THB
```

### 3. Platform Dashboard KPIs
```
Active Sellers: count
Products Listed: count
Orders This Month: count
GMV This Month: xxx THB
Revenue This Month: xxx THB
```

## Data Sources

| Report Element | Model | Key Fields |
|----------------|-------|------------|
| Order totals | sale.order | amount_total, state, date_order |
| Commission data | seller.payment | commission_amount, payment_amount, state |
| Wallet balances | seller.wallet | balance |
| Withdrawals | seller.withdrawal.request | amount, state, create_date |
| Journal entries | account.move | amount_total, journal_id, state |

## Dashboard Model: marketplace.dashboard

Provides aggregated metrics for the backend Odoo dashboard:
- Total sellers, products, orders
- Revenue breakdown by period
- Top sellers by GMV
- Commission collection rate

## Owned Files

| File | Purpose |
|------|---------|
| `core_marketplace/models/mp_dashboard.py` | Dashboard model with computed metrics |
| `core_marketplace/views/mp_dashboard_view.xml` | Backend dashboard views |
| `core_marketplace/report/` | Report templates (QWeb) |

## Anti-Patterns

| Don't | Do Instead |
|-------|-----------|
| Calculate metrics from raw SQL in controllers | Use dedicated reporting models/methods |
| Show seller B's financials to seller A | Always scope by `marketplace_seller_id` |
| Use `sudo()` for financial reads | Respect record rules for data isolation |
| Cache financial metrics for long periods | Real-time or near-real-time computation |

## Cross-References

| Direction | Skill | Interaction |
|-----------|-------|-------------|
| ← | [commission-engine](../commission-engine/SKILL.md) | Commission data for reports |
| ← | [wallet-system](../wallet-system/SKILL.md) | Wallet balances for dashboards |
| ← | [withdrawal-processing](../withdrawal-processing/SKILL.md) | Payout data for reports |
| ← | [accounting-entries](../accounting-entries/SKILL.md) | Journal data for financial reports |
| ← | [order-processing](../../../commerce/skills/order-processing/SKILL.md) | Order data for GMV |
