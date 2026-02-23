# /check-commission

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).

Review commission overview, seller earnings, and platform revenue.

## Usage

```
/check-commission                    # Platform overview
/check-commission <seller_name>      # Specific seller
/check-commission --period monthly   # Period filter
```

## How It Works

```
┌─────────────────────────────────────────────────────┐
│               CHECK COMMISSION                       │
├─────────────────────────────────────────────────────┤
│  STANDALONE (always works)                           │
│  ✓ Explain commission structure and rates            │
│  ✓ Calculate commission from provided order data     │
├─────────────────────────────────────────────────────┤
│  SUPERCHARGED (when ~~marketplace-engine connected)  │
│  + Pull real commission data from Odoo               │
│  + Show per-seller earnings breakdown                │
│  + Show wallet balances and pending withdrawals      │
│  + Generate revenue reports                          │
└─────────────────────────────────────────────────────┘
```

## Workflow

1. **Gather Data** — Pull from ~~marketplace-engine (seller.payment, seller.wallet)
2. **Summarize** — Aggregate by seller, period, status
3. **Analyze** — Identify trends, outstanding settlements
4. **Report** — Structured commission overview

## Output

```markdown
## Commission Report

**Period:** [start] — [end]
**Global Rate:** [rate]%

### Platform Revenue
| Metric | Amount |
|--------|--------|
| Total Order Value | ฿[amount] |
| Platform Commission | ฿[amount] |
| Seller Earnings | ฿[amount] |

### Per-Seller Breakdown
| Seller | Orders | Order Value | Commission | Earnings | Wallet Balance |
|--------|--------|-------------|------------|----------|---------------|
| [name] | [n] | ฿[val] | ฿[comm] | ฿[earn] | ฿[bal] |

### Pending Settlements
| Seller | Amount | Status | Since |
|--------|--------|--------|-------|
| [name] | ฿[amount] | [status] | [date] |

### Pending Withdrawals
| Seller | Amount | Status | Requested |
|--------|--------|--------|-----------|
| [name] | ฿[amount] | [status] | [date] |
```

## Next Steps

- Want to approve any pending withdrawals?
- Should I adjust commission rates for a specific seller?
- Want to see historical trends?

## Related Skills

- Uses [commission-wallet](../skills/commission-wallet/SKILL.md) for financial data
- Cross-references [commerce](../skills/commerce/SKILL.md) for order data
