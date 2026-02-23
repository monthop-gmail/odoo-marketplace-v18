---
name: commission-wallet
description: Commission calculation, seller payments, accounting integration, and
  wallet system. Activate when working on commission rates, seller payment settlement,
  journal entries, wallet balance, withdrawal requests, or financial reporting.
---

# S3: Commission & Wallet (ค่าคอมมิชชัน และ กระเป๋าเงิน)

You are an expert at financial settlement in a multi-vendor marketplace. You manage commission calculation, seller payment records, accounting journal entries, the seller wallet system, and withdrawal workflows.

> If you see unfamiliar `~~category` placeholders, see [CONNECTORS.md](../../CONNECTORS.md).

## Commission Flow

```
Order Confirmed → Calculate Commission → Create seller.payment → ~~payment journal entry
                                                                → ~~wallet credit

Commission = Order Amount × Commission Rate (%)
Seller Receives = Order Amount - Commission
```

| Setting | Location | Default |
|---------|----------|---------|
| Global commission rate | `res.config.settings` | Configurable |
| Per-seller override | `res.partner.commission_rate` | Optional |
| Per-product override | Future Phase 3 | — |

## Wallet System

### Balance Management
```
                    ┌──────────┐
Commission paid ──→ │  Wallet  │ ──→ Withdrawal
                    │ Balance  │
                    └──────────┘
```

- **Atomic balance**: Raw SQL `UPDATE WHERE balance >= amount` (prevents race conditions)
- **Auto-create**: Wallet created on seller approval (`res_partner.write()`)
- **Auto-credit**: On commission payment (`account_move.create_seller_payment_new()`)

### Withdrawal Flow

```
draft → pending → approved → processing → completed
                ↓                         ↓
            rejected                  cancelled
```

| State | Who Acts | Next States |
|-------|----------|-------------|
| Draft | Seller creates | → Pending |
| Pending | Auto (on submit) | → Approved, → Rejected |
| Approved | Admin reviews | → Processing |
| Processing | System/bank | → Completed, → Cancelled |
| Rejected | Admin with reason | (terminal) |

### Config Parameters
| Key | Purpose |
|-----|---------|
| `mp_min_withdrawal_amount` | Minimum withdrawal threshold |
| `mp_withdrawal_cooldown_days` | Days between withdrawal requests |

## Owned Files

### Models (~~marketplace-engine)
| File | Model | Purpose |
|------|-------|---------|
| `core_marketplace/models/seller_payment.py` | seller.payment | Commission tracking & settlement |
| `core_marketplace/models/seller_payment_method.py` | seller.payment.method | Payment method config |
| `core_marketplace/models/account_move.py` | account.move (ext) | Invoice & journal entries |
| `core_marketplace/models/res_config.py` | res.config.settings (ext) | Commission rate settings |
| `core_marketplace/models/seller_wallet.py` | seller.wallet | Wallet balance |
| `core_marketplace/models/seller_wallet_transaction.py` | seller.wallet.transaction | Transaction history |
| `core_marketplace/models/seller_withdrawal_request.py` | seller.withdrawal.request | Withdrawal management |

## Key Data Models

### seller.payment
```python
seller_id = fields.Many2one('res.partner')
payment_amount = fields.Float()
commission_amount = fields.Float()
state = fields.Selection()  # draft, requested, approved, paid
sale_order_ids = fields.Many2many('sale.order')
invoice_id = fields.Many2one('account.move')
```

### seller.wallet
```python
seller_id = fields.Many2one('res.partner')
balance = fields.Float()  # atomic updates only
```

### seller.withdrawal.request
```python
seller_id = fields.Many2one('res.partner')
amount = fields.Float()
state = fields.Selection()  # draft, pending, approved, processing, completed, rejected, cancelled
```

## API Endpoints (via ~~api)

### Seller Wallet API (7 endpoints)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/line-seller/wallet` | GET | Wallet balance + recent transactions |
| `/api/line-seller/wallet/transactions` | GET | Full transaction history |
| `/api/line-seller/wallet/withdraw` | POST | Create withdrawal request |
| `/api/line-seller/wallet/withdrawals` | GET | Withdrawal history |

### Admin Wallet API (6 endpoints)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/line-admin/wallets` | GET | All seller wallets |
| `/api/line-admin/withdrawals` | GET | All withdrawal requests |
| `/api/line-admin/withdrawals/<id>/approve` | POST | Approve withdrawal |
| `/api/line-admin/withdrawals/<id>/reject` | POST | Reject withdrawal |

## Interfaces

| Direction | Agent | What |
|-----------|-------|------|
| ← | [seller-engine](../seller-engine/SKILL.md) | Approved seller → auto-create wallet |
| ← | [commerce](../commerce/SKILL.md) | Order confirmed → commission calculation |
| → | [line-integration](../line-integration/SKILL.md) | Payment/withdrawal status → ~~messaging notify |
| → | [liff-frontend](../liff-frontend/SKILL.md) | Wallet data → seller LIFF dashboard |

## Anti-Patterns

| Don't | Do Instead |
|-------|-----------|
| Update wallet balance with ORM `write()` | Use raw SQL `UPDATE WHERE balance >= amount` |
| Allow withdrawal without cooldown check | Enforce `mp_withdrawal_cooldown_days` |
| Skip audit trail on financial ops | Every transaction creates `seller.wallet.transaction` |
| Let staff access wallet/withdrawal | Use `@owner_only` decorator |
| Change commission rate without admin approval | Require Manager security group |

## Related Commands

- [/check-commission](../../commands/check-commission.md) — Commission overview and reporting
