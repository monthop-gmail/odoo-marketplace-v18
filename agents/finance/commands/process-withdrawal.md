# /process-withdrawal

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).

Process seller withdrawal requests -- review, approve, or reject.

## Usage

```
/process-withdrawal <withdrawal_id>   # Process specific request
/process-withdrawal --pending          # List all pending requests
/process-withdrawal --history <seller> # Withdrawal history for seller
```

## How It Works

```
┌─────────────────────────────────────────────────────┐
│              PROCESS WITHDRAWAL                      │
├─────────────────────────────────────────────────────┤
│  STANDALONE (always works)                           │
│  ✓ Explain withdrawal flow and statuses              │
│  ✓ Describe validation rules and constraints         │
│  ✓ Show approval checklist                           │
├─────────────────────────────────────────────────────┤
│  SUPERCHARGED (when ~~marketplace-engine connected)  │
│  + Pull withdrawal request from Odoo                 │
│  + Validate against ~~wallet balance and rules       │
│  + Execute approval/rejection status transition      │
│  + Deduct from ~~wallet on approval                  │
│  + Send ~~messaging notification to seller           │
└─────────────────────────────────────────────────────┘
```

## Withdrawal Flow

```
draft → pending → approved → processing → completed
                     ↓
                  rejected
         ↓
      cancelled
```

## Validation Rules

| Rule | Check | Config Key |
|------|-------|-----------|
| Minimum amount | Amount >= threshold | `mp_min_withdrawal_amount` |
| Sufficient balance | Wallet balance >= amount | Atomic SQL check |
| Cooldown period | Days since last withdrawal | `mp_withdrawal_cooldown_days` |
| Owner only | Requester is shop owner, not staff | `owner_only` decorator |
| Bank account | Seller has bank details on file | res.partner.bank |

## Workflow

1. **Fetch Request** -- Pull from ~~wallet (seller.withdrawal.request)
2. **Validate** -- Check all rules against current state
3. **Review** -- Present details with validation checklist
4. **Execute** -- On approval: update status, deduct ~~wallet balance
5. **Notify** -- Send ~~messaging notification to seller

## Output

```markdown
## Withdrawal Request

**ID:** [id]
**Seller:** [name] (partner_id: [id])
**Amount:** ฿[amount]
**Status:** [current_status]
**Requested:** [date]

### Wallet State
| Field | Value |
|-------|-------|
| Current Balance | ฿[balance] |
| After Withdrawal | ฿[remaining] |
| Total Earned | ฿[total_earned] |
| Total Withdrawn | ฿[total_withdrawn] |

### Validation Checklist
- [x/✗] Amount >= minimum (฿[min_amount])
- [x/✗] Sufficient balance (฿[balance] >= ฿[amount])
- [x/✗] Cooldown passed ([days] days since last, requires [cooldown])
- [x/✗] Requester is shop owner (not staff)
- [x/✗] Bank account on file

### Bank Details
| Field | Value |
|-------|-------|
| Bank | [bank_name] |
| Account | [account_number] |
| Account Name | [account_name] |

### Decision
[APPROVED/REJECTED] -- [reason]
```

## Next Steps

- Want me to approve this withdrawal?
- Should I reject with a specific reason?
- Want to see more pending withdrawals?

## Related Skills

- Uses [wallet](../skills/wallet/SKILL.md) for balance operations
- Uses [commission](../skills/commission/SKILL.md) for earnings verification
- Triggers [line-integration](../../line-platform/CONNECTORS.md) for notifications
