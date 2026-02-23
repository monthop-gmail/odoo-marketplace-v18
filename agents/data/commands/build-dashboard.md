# /build-dashboard

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).

Build an HTML dashboard with Chart.js for seller or platform-level analytics.

## Usage

```
/build-dashboard seller           # Seller performance dashboard
/build-dashboard platform         # Platform overview dashboard
/build-dashboard seller --name "ร้านใหม่"
/build-dashboard platform --period monthly
```

## How It Works

```
┌─────────────────────────────────────────────────────┐
│                BUILD DASHBOARD                       │
├─────────────────────────────────────────────────────┤
│  STANDALONE (always works)                           │
│  ✓ Generate HTML + Chart.js dashboard template       │
│  ✓ Define KPI card layout and chart types            │
│  ✓ Create responsive grid with Thai labels           │
├─────────────────────────────────────────────────────┤
│  SUPERCHARGED (when ~~marketplace-engine connected)  │
│  + Query real data from Odoo for charts              │
│  + Populate KPI cards with live numbers              │
│  + Generate date-range comparisons                   │
│  + Export as standalone HTML file                    │
└─────────────────────────────────────────────────────┘
```

## Dashboard Components

| Component | Chart Type | Data Source |
|-----------|-----------|-------------|
| **KPI Cards** | Number + delta | sale.order, res.partner |
| **Revenue Trend** | Line chart | sale.order (monthly) |
| **Top Sellers** | Horizontal bar | seller.payment (aggregated) |
| **Order Status** | Donut chart | sale.order (by state) |
| **Category Split** | Pie chart | product.template (by categ_id) |
| **Recent Orders** | Table | sale.order (last 10) |

## KPI Cards (Platform)

| KPI | Query |
|-----|-------|
| Total GMV | SUM(sale.order.amount_total) WHERE state in ('sale','done') |
| Active Sellers | COUNT(res.partner) WHERE seller_status='approved' |
| Orders Today | COUNT(sale.order) WHERE date_order = today |
| Avg Order Value | AVG(sale.order.amount_total) |
| Commission Earned | SUM(seller.payment.commission_amount) |
| Pending Withdrawals | COUNT(seller.withdrawal.request) WHERE state='pending' |

## KPI Cards (Seller)

| KPI | Query |
|-----|-------|
| My Revenue | SUM(sale.order_line.price_subtotal) for seller |
| My Orders | COUNT(sale.order) for seller products |
| Wallet Balance | seller.wallet.balance |
| Products Listed | COUNT(product.template) for seller |
| Avg Rating | AVG(seller.review.rating) |
| Pending Orders | COUNT(sale.order) WHERE state='sale' for seller |

## Tech Stack

```
HTML5 + Chart.js 4.x + CSS Grid
- CDN: https://cdn.jsdelivr.net/npm/chart.js
- Responsive: CSS Grid auto-fit minmax(300px, 1fr)
- Colors: Platform blue (#2196F3), Seller orange (#FF9800)
- Font: NotoSansThai for Thai labels
```

## Output

```markdown
## Dashboard Generated

**Type:** [seller/platform]
**File:** [path to generated HTML]
**Charts:** [count] charts, [count] KPI cards

### Preview
[Description of dashboard layout and data shown]
```

## Next Steps

- Want me to add more chart types or KPIs?
- Should I embed this in a LIFF admin page?
- Want to set up auto-refresh with live data?

## Related Skills

- Uses [data](../skills/) for query building and aggregation
- Cross-references [commerce](../../commerce/skills/) for order models
- Cross-references [finance](../../finance/skills/) for revenue models
