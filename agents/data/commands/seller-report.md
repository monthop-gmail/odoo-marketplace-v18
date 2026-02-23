# /seller-report

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).

Generate a seller performance report with metrics, ranking, and comparison to platform averages.

## Usage

```
/seller-report "ร้านใหม่"            # Specific seller by name
/seller-report --partner 46          # Specific seller by ID
/seller-report --all                 # All active sellers
/seller-report --top 10              # Top 10 performers
/seller-report --period 2026-02      # Filter by period
```

## How It Works

```
┌─────────────────────────────────────────────────────┐
│                 SELLER REPORT                        │
├─────────────────────────────────────────────────────┤
│  STANDALONE (always works)                           │
│  ✓ Define seller KPIs and report structure           │
│  ✓ Calculate metrics from provided data              │
│  ✓ Generate comparison template                      │
├─────────────────────────────────────────────────────┤
│  SUPERCHARGED (when ~~marketplace-engine connected)  │
│  + Pull real seller data from Odoo                   │
│  + Aggregate orders, revenue, commission, reviews    │
│  + Calculate platform averages for comparison        │
│  + Rank sellers by composite score                   │
│  + Identify growth opportunities                     │
└─────────────────────────────────────────────────────┘
```

## Seller KPIs

| KPI | Source | Formula |
|-----|--------|---------|
| Total Revenue | sale.order_line | SUM(price_subtotal) for seller products |
| Order Count | sale.order | COUNT distinct orders with seller products |
| Avg Order Value | sale.order | Revenue / Order Count |
| Product Count | product.template | COUNT active products |
| Commission Paid | seller.payment | SUM paid commission |
| Wallet Balance | seller.wallet | Current balance |
| Avg Rating | seller.review | AVG(rating) |
| Response Time | support tickets | AVG time to first response |

## Ranking Composite Score

```
Score = (Revenue * 0.3) + (Orders * 0.2) + (Rating * 0.2) +
        (Products * 0.15) + (Response * 0.15)
Normalized to 0-100 scale
```

## Output

```markdown
## Seller Performance Report

**Seller:** [name] (partner_id: [id])
**Shop:** [shop_name]
**Period:** [start] — [end]

### Performance Metrics
| Metric | Seller | Platform Avg | vs Avg |
|--------|--------|-------------|--------|
| Revenue | ฿[amount] | ฿[avg] | [+/-]% |
| Orders | [count] | [avg] | [+/-]% |
| Avg Order Value | ฿[aov] | ฿[avg] | [+/-]% |
| Products Listed | [count] | [avg] | [+/-]% |
| Avg Rating | [rating]/5 | [avg]/5 | [+/-] |
| Wallet Balance | ฿[balance] | — | — |

### Ranking
**Overall Rank:** #[rank] of [total] sellers
**Composite Score:** [score]/100

### Top Products
| Product | Orders | Revenue | Rating |
|---------|--------|---------|--------|
| [name] | [count] | ฿[amount] | [rating] |

### Recommendations
1. [Growth opportunity based on data]
2. [Area for improvement]
```

## Next Steps

- Want to compare this seller with another?
- Should I generate reports for all sellers?
- Want to see commission and withdrawal details?

## Related Skills

- Uses [data](../skills/) for query building and aggregation
- Cross-references [seller-engine](../../seller-engine/skills/) for seller models
- Cross-references [finance](../../finance/skills/) for commission data
