# /analyze

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).

Analyze marketplace data — GMV, sellers, orders, conversion, products, and revenue breakdowns.

## Usage

```
/analyze gmv                     # Gross Merchandise Value
/analyze sellers                 # Seller performance overview
/analyze orders                  # Order volume and status
/analyze conversion              # Funnel conversion rates
/analyze products                # Product catalog health
/analyze revenue                 # Platform revenue breakdown
/analyze --period 2026-02        # Filter by period
```

## How It Works

```
┌─────────────────────────────────────────────────────┐
│                    ANALYZE                            │
├─────────────────────────────────────────────────────┤
│  STANDALONE (always works)                           │
│  ✓ Define metrics and KPIs for each analysis type    │
│  ✓ Build query plan from description                 │
│  ✓ Generate sample analysis with mock data           │
├─────────────────────────────────────────────────────┤
│  SUPERCHARGED (when ~~marketplace-engine connected)  │
│  + Query real data from Odoo via ~~api               │
│  + Aggregate sale.order, product.template, res.partner│
│  + Calculate trends vs previous period               │
│  + Generate actionable recommendations               │
└─────────────────────────────────────────────────────┘
```

## Available Analyses

| Analysis | Key Metrics | Source Models |
|----------|------------|---------------|
| **GMV** | Total sales, avg order value, growth % | sale.order, sale.order.line |
| **Sellers** | Active count, new signups, approval rate | res.partner (seller) |
| **Orders** | Volume, status breakdown, completion rate | sale.order |
| **Conversion** | Visit→cart→order→paid funnel | sale.order, website |
| **Products** | Listed count, active, out-of-stock, avg price | product.template |
| **Revenue** | Commission earned, wallet payouts, net revenue | seller.payment, seller.wallet |

## Output

```markdown
## Marketplace Analysis: [type]

**Period:** [start] — [end]
**Generated:** [datetime]

### Key Metrics
| Metric | Value | vs Previous | Trend |
|--------|-------|-------------|-------|
| [metric] | [value] | [+/-]% | [up/down/flat] |

### Breakdown
[Type-specific breakdown table or chart data]

### Insights
1. [Key finding with data support]
2. [Key finding with data support]

### Recommendations
1. [Actionable recommendation]
2. [Actionable recommendation]
```

## Next Steps

- Want me to drill down into a specific metric?
- Should I build a dashboard with these numbers?
- Want to compare with a different period?

## Related Skills

- Uses [data](../skills/) for query building and analysis
- Cross-references [commerce](../../commerce/skills/) for order models
- Cross-references [finance](../../finance/skills/) for revenue models
