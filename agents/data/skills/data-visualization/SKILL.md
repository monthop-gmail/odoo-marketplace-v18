---
name: data-visualization
description: Activate when creating charts, graphs, or visual data representations
  for the marketplace. Covers chart type selection, Chart.js patterns, Odoo graph views,
  ASCII tables, and Markdown formatting for dashboards and reports.
---

# Data Visualization (Chart Specialist)

You are a data visualization specialist who selects the right chart type for each dataset and produces clean, readable visualizations using Chart.js, Odoo graph views, or text-based formats.

> If you see unfamiliar `~~category` placeholders, see [CONNECTORS.md](../../../CONNECTORS.md).

## Chart Type by Data Type

| Data Pattern | Recommended Chart | Example Use Case |
|-------------|-------------------|------------------|
| Trend over time | Line chart | Daily GMV, Monthly revenue |
| Category comparison | Bar chart (vertical) | Revenue by seller, Orders by status |
| Part of whole | Doughnut / Pie | Order status distribution, Category share |
| Ranking / leaderboard | Horizontal bar | Top 10 sellers, Top products |
| Distribution | Histogram | Order value distribution |
| Correlation | Scatter plot | Price vs sales volume |
| Progress / target | Gauge / Progress bar | KPI target completion |
| Geographic | Map (future) | Orders by province |
| Funnel | Funnel chart | Conversion funnel |
| Multiple series time | Stacked area | Revenue by category over time |

## Tools and When to Use

| Tool | Context | Pros | Cons |
|------|---------|------|------|
| Chart.js | LIFF dashboards | Interactive, mobile-friendly | Requires JS |
| Odoo Graph View | Backend dashboards | Integrated, no extra code | Limited customization |
| ASCII Table | Terminal / logs | No dependencies | No interactivity |
| Markdown Table | Documentation / reports | Readable everywhere | Static only |
| Odoo Pivot View | Backend analysis | Drill-down, flexible | Backend only |

## Chart.js Code Pattern

```html
<canvas id="revenueChart" width="400" height="200"></canvas>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
const ctx = document.getElementById('revenueChart').getContext('2d');
new Chart(ctx, {
    type: 'line',
    data: {
        labels: data.map(d => d.date),
        datasets: [{
            label: 'Revenue (THB)',
            data: data.map(d => d.revenue),
            borderColor: '#4CAF50',
            backgroundColor: 'rgba(76, 175, 80, 0.1)',
            fill: true,
            tension: 0.3
        }]
    },
    options: {
        responsive: true,
        plugins: { legend: { position: 'top' } },
        scales: {
            y: { beginAtZero: true,
                 ticks: { callback: v => v.toLocaleString() + ' THB' } }
        }
    }
});
</script>
```

## Color Palette

| Role | Primary | Secondary | Use |
|------|---------|-----------|-----|
| Buyer | `#4CAF50` (green) | `#81C784` | Buyer LIFF, revenue charts |
| Seller | `#FF9800` (orange) | `#FFB74D` | Seller LIFF, seller metrics |
| Admin | `#1A237E` (dark blue) | `#5C6BC0` | Admin LIFF, platform charts |
| Danger | `#F44336` (red) | `#EF9A9A` | Negative trends, alerts |
| Neutral | `#9E9E9E` (gray) | `#E0E0E0` | Backgrounds, borders |

## Odoo Graph View Pattern

```xml
<record id="view_seller_payment_graph" model="ir.ui.view">
    <field name="name">seller.payment.graph</field>
    <field name="model">seller.payment</field>
    <field name="arch" type="xml">
        <graph string="Commission Revenue" type="bar">
            <field name="payment_date" interval="month"/>
            <field name="seller_commission" type="measure"/>
        </graph>
    </field>
</record>
```

## Formatting Standards

- Always include axis labels and units (THB, count, %)
- Use thousand separators for currency: `1,234,567 THB`
- Date format: `DD/MM/YYYY` for Thai locale
- Mobile-first: charts must be readable on 375px width
- Max 7 segments in pie/doughnut charts; group small slices as "Other"

## Cross-References

- [marketplace-analytics](../marketplace-analytics/SKILL.md) for KPI definitions
- [dashboard-builder](../dashboard-builder/SKILL.md) for full dashboard assembly
- [sales-reporting](../sales-reporting/SKILL.md) for report chart requirements
- ~~liff-app for LIFF dashboard integration
