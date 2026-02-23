---
name: wallet-system
description: Wallet balance and transaction management. Activate when working on
  seller.wallet, seller.wallet.transaction, atomic balance updates, auto-create
  on approval, auto-credit on commission, or wallet API endpoints.
---

# Wallet System (ระบบกระเป๋าเงิน)

You are an expert at managing seller wallets in a multi-vendor marketplace, handling balance integrity with atomic operations, auto-creation on seller approval, and the full transaction audit trail.

> If you see unfamiliar `~~category` placeholders, see [CONNECTORS.md](../../CONNECTORS.md).

## Wallet Architecture

```
              ┌─────────────┐
Commission ──→│   Wallet     │──→ Withdrawal
  (credit)    │   Balance    │     (debit)
              └─────────────┘
                    │
              ┌─────────────┐
              │ Transaction  │  (full audit log)
              │   History    │
              └─────────────┘
```

## Atomic Balance Updates (Critical)

**NEVER use ORM `write()` for balance changes.** Use raw SQL with WHERE guard:

```sql
UPDATE seller_wallet
SET balance = balance - %(amount)s,
    write_date = NOW(),
    write_uid = %(uid)s
WHERE id = %(wallet_id)s
  AND balance >= %(amount)s
RETURNING id;
```

If `RETURNING` returns no rows → insufficient balance → raise error.

## Key Models

### seller.wallet
```python
seller_id = fields.Many2one('res.partner', required=True, unique=True)
balance = fields.Float(digits=(16, 2))  # atomic updates only
currency_id = fields.Many2one('res.currency')
```

### seller.wallet.transaction
```python
wallet_id = fields.Many2one('seller.wallet')
type = fields.Selection([('credit', 'Credit'), ('debit', 'Debit')])
amount = fields.Float()
reference = fields.Char()       # e.g., "commission:SO123" or "withdrawal:WD45"
balance_after = fields.Float()  # snapshot for audit
```

## Auto-Create on Approval

When `res_partner.write()` sets `seller_status='approved'`:
```python
# In res_partner.py write() override
if 'seller_status' in vals and vals['seller_status'] == 'approved':
    self.env['seller.wallet'].create({'seller_id': partner.id})
```

## Auto-Credit on Commission

In `account_move.create_seller_payment_new()`:
1. Commission calculated and payment created
2. `seller.wallet.transaction` (credit) recorded
3. Balance atomically incremented via SQL

## API Endpoints (via ~~api)

### Seller Wallet API
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/line-seller/wallet` | GET | Balance + recent transactions |
| `/api/line-seller/wallet/transactions` | GET | Full transaction history (paginated) |
| `/api/line-seller/wallet/withdraw` | POST | Create withdrawal request |
| `/api/line-seller/wallet/withdrawals` | GET | Withdrawal request history |

### Admin Wallet API
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/line-admin/wallets` | GET | All seller wallets overview |
| `/api/line-admin/wallets/<id>` | GET | Specific wallet detail |

## Owned Files

| File | Purpose |
|------|---------|
| `core_marketplace/models/seller_wallet.py` | seller.wallet model + atomic SQL |
| `core_marketplace/models/seller_wallet_transaction.py` | Transaction audit log |
| `core_line_integration/controllers/api_seller_wallet.py` | Seller wallet API |
| `core_line_integration/controllers/api_admin_wallets.py` | Admin wallet API |

## Anti-Patterns

| Don't | Do Instead |
|-------|-----------|
| Use ORM `write()` for balance | Raw SQL `UPDATE WHERE balance >= amount` |
| Create wallet manually | Auto-created on seller approval |
| Skip transaction audit record | Every balance change = transaction record |
| Let staff access wallet | Use `@owner_only` decorator |
| Allow negative balance | SQL WHERE guard prevents this |

## Cross-References

| Direction | Skill | Interaction |
|-----------|-------|-------------|
| ← | [commission-engine](../commission-engine/SKILL.md) | Commission paid → credit wallet |
| → | [withdrawal-processing](../withdrawal-processing/SKILL.md) | Withdrawal → debit wallet |
| ← | [seller-lifecycle](../../../seller-engine/skills/seller-lifecycle/SKILL.md) | Approval → auto-create wallet |
| → | [financial-reporting](../financial-reporting/SKILL.md) | Wallet balances → financial dashboards |
