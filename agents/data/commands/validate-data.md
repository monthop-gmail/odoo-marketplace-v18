# /validate-data

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).

Run data integrity checks across the marketplace platform and optionally auto-fix issues.

## Usage

```
/validate-data                   # Run all checks
/validate-data --sellers         # Seller data only
/validate-data --wallets         # Wallet integrity only
/validate-data --orders          # Order consistency only
/validate-data --fix             # Auto-fix where possible
```

## How It Works

```
┌─────────────────────────────────────────────────────┐
│                VALIDATE DATA                         │
├─────────────────────────────────────────────────────┤
│  STANDALONE (always works)                           │
│  ✓ Define all integrity checks and expected states   │
│  ✓ List what each check validates                    │
│  ✓ Describe fix procedures for each issue type       │
├─────────────────────────────────────────────────────┤
│  SUPERCHARGED (when ~~marketplace-engine connected)  │
│  + Execute checks against real Odoo database         │
│  + Report violations with specific record IDs        │
│  + Auto-fix safe issues (with --fix flag)            │
│  + Generate fix scripts for manual issues            │
└─────────────────────────────────────────────────────┘
```

## Integrity Checks

| # | Check | Severity | Auto-Fix |
|---|-------|----------|----------|
| 1 | Approved seller without seller.shop | Critical | Yes — create shop |
| 2 | Approved seller without seller.wallet | Critical | Yes — create wallet |
| 3 | Seller with wallet but status != approved | Warning | No — manual review |
| 4 | Wallet balance < 0 | Critical | No — investigate |
| 5 | Wallet balance != SUM(transactions) | Critical | No — investigate |
| 6 | Withdrawal request > wallet balance | High | No — reject request |
| 7 | Product without marketplace_seller_id | Warning | Yes — set from template |
| 8 | Order line referencing deleted product | High | No — manual review |
| 9 | LINE member without partner | Warning | Yes — create partner |
| 10 | Partner with seller_status but no security group | High | Yes — assign group |
| 11 | Shop without url_handler | Warning | Yes — generate from partner_id |
| 12 | Duplicate url_handler in seller.shop | Critical | No — manual resolve |

## Check Categories

| Category | Checks | Description |
|----------|--------|-------------|
| `--sellers` | 1, 2, 3, 10, 11, 12 | Seller lifecycle consistency |
| `--wallets` | 2, 4, 5, 6 | Wallet balance integrity |
| `--orders` | 7, 8 | Order and product consistency |
| `--line` | 9 | LINE member data |

## Output

```markdown
## Data Validation Report

**Date:** [datetime]
**Scope:** [all/sellers/wallets/orders]
**Mode:** [check-only/auto-fix]

### Results Summary
| Status | Count |
|--------|-------|
| Passed | [n] |
| Warnings | [n] |
| Failures | [n] |
| Auto-Fixed | [n] |

### Issues Found
| # | Check | Severity | Records | Status |
|---|-------|----------|---------|--------|
| [n] | [description] | [sev] | [ids] | [pass/fail/fixed] |

### Fix Log (if --fix)
| Record | Issue | Action Taken |
|--------|-------|-------------|
| partner [id] | Missing shop | Created seller.shop |

### Manual Action Required
1. [Issue description + fix instructions]
```

## Next Steps

- Want me to auto-fix the safe issues now?
- Should I investigate any critical failures?
- Want to schedule regular validation runs?

## Related Skills

- Uses [data](../skills/) for validation logic and query patterns
- Cross-references [seller-engine](../../seller-engine/skills/) for seller lifecycle
- Cross-references [finance](../../finance/skills/) for wallet integrity
