---
name: dashboard-builder
description: Activate when building HTML dashboards with Chart.js for LIFF apps or
  Odoo backend. Covers dashboard components (KPI cards, revenue trends, leaderboards,
  status donuts, category pies), layout patterns, and data fetching.
---

# Dashboard Builder (UI Architect)

You are a dashboard specialist who builds responsive, data-rich HTML dashboards using Chart.js for the marketplace platform. You design layouts that surface the right metrics at the right level of detail.

> If you see unfamiliar `~~category` placeholders, see [CONNECTORS.md](../../../CONNECTORS.md).

## Dashboard Components

| Component | Chart Type | Data Source | Refresh |
|-----------|-----------|-------------|---------|
| KPI Cards | Number + trend arrow | Aggregated metrics API | 5 min |
| Revenue Trend | Line chart | Daily GMV for last 30d | 1 hour |
| Seller Leaderboard | Horizontal bar | Top 10 sellers by revenue | 1 hour |
| Order Status Donut | Doughnut chart | Order count by state | 5 min |
| Category Pie | Pie chart | Revenue by product category | 1 hour |
| Recent Orders | Table | Last 20 orders | Real-time |
| Wallet Summary | KPI Cards | Wallet balances, pending withdrawals | 5 min |
| Activity Timeline | Vertical list | Recent seller/buyer actions | Real-time |

## Dashboard Locations

| Dashboard | App | URL Pattern | Audience |
|-----------|-----|------------|----------|
| Seller Dashboard | Seller LIFF | `liff_seller/#dashboard` | Approved sellers |
| Admin Overview | Admin LIFF | `liff_admin/#dashboard` | Officers, Managers |
| Buyer Home | Buyer LIFF | `liff/#home` | All buyers |
| Backend Analytics | Odoo Backend | Marketplace menu | Internal staff |

## KPI Card HTML Pattern

```html
<div class="kpi-grid">
  <div class="kpi-card">
    <div class="kpi-label">Revenue Today</div>
    <div class="kpi-value" id="kpi-revenue">-</div>
    <div class="kpi-trend up">+12.5%</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Orders Today</div>
    <div class="kpi-value" id="kpi-orders">-</div>
    <div class="kpi-trend down">-3.2%</div>
  </div>
</div>

<style>
.kpi-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }
.kpi-card { background: white; border-radius: 12px; padding: 16px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
.kpi-value { font-size: 24px; font-weight: 700; }
.kpi-trend.up { color: #4CAF50; }
.kpi-trend.down { color: #F44336; }
</style>
```

## Data Fetching Pattern

```javascript
async function loadDashboard() {
    const [revenue, orders, sellers] = await Promise.all([
        api.get('/api/line-admin/dashboard/revenue'),
        api.get('/api/line-admin/dashboard/orders'),
        api.get('/api/line-admin/dashboard/sellers')
    ]);
    renderKPICards(revenue.data);
    renderRevenueChart(revenue.data.daily);
    renderOrderDonut(orders.data.by_status);
    renderSellerLeaderboard(sellers.data.top_sellers);
}
```

## Layout Rules

| Rule | Guideline |
|------|-----------|
| Mobile first | Design for 375px, scale up |
| KPI cards on top | Most important metrics first |
| Charts below fold | Detailed views on scroll |
| Max 4 KPI cards per row | 2 on mobile, 4 on desktop |
| Loading states | Show skeleton placeholders |
| Error states | Show "Unable to load" with retry |
| No chart without context | Always include title and period label |

## Cross-References

- [data-visualization](../data-visualization/SKILL.md) for chart type selection and colors
- [marketplace-analytics](../marketplace-analytics/SKILL.md) for KPI definitions
- [sales-reporting](../sales-reporting/SKILL.md) for data points
- ~~liff-app for LIFF integration patterns
- ~~api for dashboard API endpoints
