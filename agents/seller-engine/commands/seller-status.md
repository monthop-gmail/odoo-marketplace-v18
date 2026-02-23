# /seller-status

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).

Check seller status, details, and related information.

## Usage

```
/seller-status <seller_name_or_id>    # Specific seller
/seller-status --pending              # All pending applications
/seller-status --all                  # All sellers overview
```

## How It Works

```
┌─────────────────────────────────────────────────────┐
│                  SELLER STATUS                       │
├─────────────────────────────────────────────────────┤
│  STANDALONE (always works)                           │
│  ✓ Explain seller status flow and transitions        │
│  ✓ Describe each status meaning and requirements     │
│  ✓ List available actions per status                 │
├─────────────────────────────────────────────────────┤
│  SUPERCHARGED (when ~~marketplace-engine connected)  │
│  + Pull real seller data from Odoo                   │
│  + Show shop details and product count               │
│  + Show ~~wallet balance and transactions            │
│  + List staff members and their roles                │
│  + Show recent orders and commission earned           │
└─────────────────────────────────────────────────────┘
```

## Status Flow

```
none → draft → pending → approved
                  ↓
               denied
```

| Status | Meaning | Available Actions |
|--------|---------|-------------------|
| none | Not a seller | Can apply |
| draft | Started application | Complete form, submit |
| pending | Awaiting review | Admin reviews |
| approved | Active seller | Full seller access |
| denied | Rejected | Can re-apply |

## Output

```markdown
## Seller Details

**Name:** [name] (partner_id: [id])
**Status:** [status]
**LINE:** [line_user_id]
**Member Type:** [buyer/seller/admin]
**Since:** [approval_date]

### Shop
| Field | Value |
|-------|-------|
| Shop Name | [name] |
| URL Handler | [shop-id] |
| Products | [count] active / [count] total |
| Rating | [stars] ([review_count] reviews) |

### Wallet
| Field | Value |
|-------|-------|
| Balance | ฿[amount] |
| Total Earned | ฿[amount] |
| Total Withdrawn | ฿[amount] |
| Pending Withdrawal | ฿[amount] |

### Staff
| Name | Role | Status | Since |
|------|------|--------|-------|
| [name] | owner/staff | active | [date] |

### Recent Orders
| Order | Date | Amount | Commission | Status |
|-------|------|--------|------------|--------|
| [SO-xxx] | [date] | ฿[amount] | ฿[comm] | [status] |
```

## Next Steps

- Want to approve/reject this seller?
- Should I check their product listings?
- Want to see their commission history?

## Related Skills

- Uses [seller-lifecycle](../skills/seller-lifecycle/SKILL.md) for status flow
- Uses [shop-management](../skills/shop-management/SKILL.md) for shop data
- Cross-references [wallet](../../finance/CONNECTORS.md) for financial data
