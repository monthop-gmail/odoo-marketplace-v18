# /financial-report

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).

Generate financial reports for the marketplace platform.

## Usage

```
/financial-report                       # Full platform report (current month)
/financial-report --period weekly        # Period: daily/weekly/monthly/yearly
/financial-report --seller <name>        # Seller-specific report
/financial-report --compare              # Compare with previous period
```

## How It Works

```
┌─────────────────────────────────────────────────────┐
│               FINANCIAL REPORT                       │
├─────────────────────────────────────────────────────┤
│  STANDALONE (always works)                           │
│  ✓ Explain revenue model and commission structure    │
│  ✓ Describe financial metrics and KPIs               │
│  ✓ Generate report template from provided data       │
├─────────────────────────────────────────────────────┤
│  SUPERCHARGED (when ~~marketplace-engine connected)  │
│  + Pull real financial data from Odoo                │
│  + Calculate GMV, commission, net revenue             │
│  + Show ~~wallet balances and outflows               │
│  + Generate seller earnings table                    │
│  + Compare period-over-period trends                 │
└─────────────────────────────────────────────────────┘
```

## Revenue Model

```
GMV (Gross Merchandise Value)
    ├── Platform Commission (rate%)  → Platform Revenue
    ├── Seller Earnings              → Seller Wallets
    └── Tax                          → Tax liability
```

## Workflow

1. **Set Period** -- Define date range (default: current month)
2. **Gather Data** -- Pull from ~~marketplace-engine + ~~wallet + ~~payment
3. **Calculate** -- GMV, commissions, net revenue, seller payouts
4. **Compare** -- Period-over-period if requested
5. **Report** -- Structured financial report

## Output

```markdown
## Financial Report

**Period:** [start] -- [end]
**Generated:** [timestamp]

### Revenue Summary
| Metric | This Period | Previous | Change |
|--------|------------|----------|--------|
| GMV (Total Sales) | ฿[amount] | ฿[prev] | [+/-]% |
| Total Orders | [n] | [prev] | [+/-]% |
| Avg Order Value | ฿[amount] | ฿[prev] | [+/-]% |
| Platform Commission | ฿[amount] | ฿[prev] | [+/-]% |
| Commission Rate | [rate]% | [prev]% | -- |

### Seller Earnings
| Seller | Orders | GMV | Commission | Net Earnings | Wallet Balance |
|--------|--------|-----|------------|-------------|---------------|
| [name] | [n] | ฿[gmv] | ฿[comm] | ฿[net] | ฿[balance] |
| **Total** | **[n]** | **฿[total]** | **฿[total]** | **฿[total]** | **฿[total]** |

### Wallet Outflows
| Type | Amount | Count |
|------|--------|-------|
| Withdrawals Completed | ฿[amount] | [n] |
| Withdrawals Pending | ฿[amount] | [n] |
| Total Wallet Balance (all sellers) | ฿[amount] | [n] wallets |

### Top Products (by revenue)
| Product | Seller | Units Sold | Revenue |
|---------|--------|-----------|---------|
| [name] | [seller] | [qty] | ฿[revenue] |

### Observations
- [Key insight about revenue trend]
- [Notable seller performance]
- [Risk or opportunity identified]
```

## Next Steps

- Want a detailed breakdown for a specific seller?
- Should I compare with a different period?
- Want to export this data?

## Related Skills

- Uses [commission](../skills/commission/SKILL.md) for commission data
- Uses [wallet](../skills/wallet/SKILL.md) for wallet balances
- Cross-references [order-management](../../commerce/CONNECTORS.md) for order metrics
