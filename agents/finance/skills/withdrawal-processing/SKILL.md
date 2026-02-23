---
name: withdrawal-processing
description: Withdrawal request lifecycle and processing. Activate when working on
  seller.withdrawal.request, withdrawal approval/rejection, withdrawal validation
  rules, cooldown periods, or minimum amount thresholds.
---

# Withdrawal Processing (การดำเนินการถอนเงิน)

You are an expert at managing seller withdrawal requests in a multi-vendor marketplace, handling the full lifecycle from request creation through admin review, processing, and completion.

> If you see unfamiliar `~~category` placeholders, see [CONNECTORS.md](../../CONNECTORS.md).

## Withdrawal Flow

```
Seller requests → draft → pending → approved → processing → completed
                                  ↓                         ↓
                              rejected                  cancelled
```

| State | Who Acts | Next States | Notes |
|-------|----------|-------------|-------|
| Draft | Seller creates | → Pending (auto) | Validation checks applied |
| Pending | System (on submit) | → Approved, → Rejected | In admin review queue |
| Approved | Admin reviews | → Processing | Admin confirms bank details |
| Processing | System/bank transfer | → Completed, → Cancelled | Awaiting bank confirmation |
| Rejected | Admin with reason | (terminal) | Balance returned to wallet |
| Completed | System confirms | (terminal) | Funds transferred |
| Cancelled | Admin/System | (terminal) | Balance returned to wallet |

## Validation Rules

Before creating a withdrawal request:

```python
# 1. Minimum amount check
min_amount = env['ir.config_parameter'].get_param('mp_min_withdrawal_amount', '0')
if amount < float(min_amount):
    raise "Amount below minimum threshold"

# 2. Cooldown period check
cooldown = env['ir.config_parameter'].get_param('mp_withdrawal_cooldown_days', '0')
last_request = env['seller.withdrawal.request'].search([
    ('seller_id', '=', seller.id),
    ('create_date', '>=', fields.Date.today() - timedelta(days=int(cooldown)))
], limit=1)
if last_request:
    raise "Cooldown period not elapsed"

# 3. Sufficient balance check (atomic SQL)
# Handled by wallet debit SQL WHERE balance >= amount
```

## Config Parameters

| Key | Type | Default | Purpose |
|-----|------|---------|---------|
| `mp_min_withdrawal_amount` | Float | 0 | Minimum withdrawal threshold (THB) |
| `mp_withdrawal_cooldown_days` | Integer | 0 | Minimum days between requests |

## Key Model: seller.withdrawal.request

```python
seller_id = fields.Many2one('res.partner')
wallet_id = fields.Many2one('seller.wallet')
amount = fields.Float()
state = fields.Selection()  # draft,pending,approved,processing,completed,rejected,cancelled
reject_reason = fields.Text()
approved_by = fields.Many2one('res.users')
bank_account = fields.Char()
```

## API Endpoints (via ~~api)

| Endpoint | Method | Role | Description |
|----------|--------|------|-------------|
| `/api/line-seller/wallet/withdraw` | POST | Seller | Create request (validates rules) |
| `/api/line-seller/wallet/withdrawals` | GET | Seller | Own withdrawal history |
| `/api/line-admin/withdrawals` | GET | Admin | All pending/active requests |
| `/api/line-admin/withdrawals/<id>/approve` | POST | Admin | Approve request |
| `/api/line-admin/withdrawals/<id>/reject` | POST | Admin | Reject with reason |
| `/api/line-admin/withdrawals/<id>/complete` | POST | Admin | Mark as completed |

## Owned Files

| File | Purpose |
|------|---------|
| `core_marketplace/models/seller_withdrawal_request.py` | Withdrawal model + validation |
| `core_line_integration/controllers/api_seller_wallet.py` | Seller withdrawal endpoints |
| `core_line_integration/controllers/api_admin_wallets.py` | Admin withdrawal management |

## Anti-Patterns

| Don't | Do Instead |
|-------|-----------|
| Let staff request withdrawals | Use `@owner_only` -- only shop owner |
| Skip cooldown validation | Always check `mp_withdrawal_cooldown_days` |
| Approve without checking bank details | Require bank account before processing |
| Debit wallet before approval | Debit only on state → processing transition |
| Skip balance refund on rejection | Always return debited amount to wallet on reject/cancel |

## Cross-References

| Direction | Skill | Interaction |
|-----------|-------|-------------|
| ← | [wallet-system](../wallet-system/SKILL.md) | Withdrawal debits wallet balance |
| → | [accounting-entries](../accounting-entries/SKILL.md) | Completed withdrawal → journal entry |
| → | [notification-triggers](../../../line-platform/skills/notification-triggers/SKILL.md) | State changes → LINE notify seller |
| ← | [seller-lifecycle](../../../seller-engine/skills/seller-lifecycle/SKILL.md) | Only approved sellers can withdraw |
