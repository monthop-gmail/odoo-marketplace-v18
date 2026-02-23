---
name: accounting-entries
description: Journal entries and accounting integration. Activate when working on
  account.move extensions, create_seller_payment_new(), commission journal structure,
  invoice generation, or marketplace accounting reconciliation.
---

# Accounting Entries (รายการบัญชี)

You are an expert at the accounting integration layer in a multi-vendor marketplace, managing journal entries for commission settlement, seller payments, withdrawal processing, and invoice generation.

> If you see unfamiliar `~~category` placeholders, see [CONNECTORS.md](../../CONNECTORS.md).

## Journal Entry Architecture

```
Order Invoiced → account.move (customer invoice)
    ↓
create_seller_payment_new()
    ↓
account.move (commission journal entry)
    ├── Debit: Seller Payable
    ├── Credit: Commission Revenue
    └── Credit: Seller Payment
    ↓
~~wallet credit (auto)
```

## create_seller_payment_new() Flow

This is the core settlement method in `account_move.py`:

```python
def create_seller_payment_new(self):
    # 1. Group confirmed lines by seller
    # 2. For each seller:
    #    a. Calculate commission = sum(line_total) x rate
    #    b. Calculate seller_amount = sum(line_total) - commission
    #    c. Create seller.payment record
    #    d. Create account.move (journal entry)
    #    e. Credit seller.wallet via atomic SQL
    # 3. Post journal entries
```

## Journal Structure

| Account | Debit | Credit | Purpose |
|---------|-------|--------|---------|
| Seller Payable (liability) | order_total | -- | Platform owes seller |
| Commission Revenue (income) | -- | commission_amount | Platform earnings |
| Seller Settlement (expense) | -- | seller_amount | Payout to seller wallet |

## Invoice Flow

| Stage | Model | Trigger |
|-------|-------|---------|
| Customer invoice | account.move (out_invoice) | Order delivered |
| Commission entry | account.move (entry) | create_seller_payment_new() |
| Withdrawal payout | account.move (entry) | Withdrawal completed |

## Owned Files

| File | Purpose |
|------|---------|
| `core_marketplace/models/account_move.py` | account.move extensions, create_seller_payment_new() |
| `core_marketplace/models/seller_payment.py` | seller.payment linked to journal entries |
| `core_marketplace/views/mp_account_move_view.xml` | Accounting views for marketplace |

## Key Relationships

```
sale.order → account.move (invoice)
         → seller.payment → account.move (commission entry)
                          → seller.wallet.transaction (credit)

seller.withdrawal.request → account.move (payout entry)
                          → seller.wallet.transaction (debit)
```

## Anti-Patterns

| Don't | Do Instead |
|-------|-----------|
| Create journal entries without proper accounts | Use configured marketplace accounts |
| Skip posting journal entries | Always post after creation |
| Modify posted journal entries | Create reversal entries instead |
| Calculate commission outside settlement method | All commission via create_seller_payment_new() |
| Mix customer invoice with commission entry | Separate account.move records |

## Cross-References

| Direction | Skill | Interaction |
|-----------|-------|-------------|
| ← | [commission-engine](../commission-engine/SKILL.md) | Commission calc → journal entry |
| ← | [wallet-system](../wallet-system/SKILL.md) | Settlement → wallet credit |
| ← | [withdrawal-processing](../withdrawal-processing/SKILL.md) | Withdrawal → payout entry |
| → | [financial-reporting](../financial-reporting/SKILL.md) | Journal data → financial reports |
