---
name: commission-engine
description: Commission rate configuration and calculation. Activate when working on
  commission rates (global/per-seller), commission calculation formulas, seller.payment
  settlement records, or commission reporting.
---

# Commission Engine (เครื่องยนต์ค่าคอมมิชชัน)

You are an expert at commission calculation and settlement in a multi-vendor marketplace. You manage rate configuration, per-order calculation, payment record creation, and commission reporting.

> If you see unfamiliar `~~category` placeholders, see [CONNECTORS.md](../../CONNECTORS.md).

## Commission Formula

```
Commission Amount = Order Line Total x Commission Rate (%)
Seller Receives   = Order Line Total - Commission Amount
Platform Revenue   = Sum of Commission Amounts
```

## Rate Configuration Hierarchy

| Level | Setting Location | Priority |
|-------|-----------------|----------|
| Global default | `res.config.settings` → `mp_commission_rate` | Lowest |
| Per-seller override | `res.partner.commission_rate` | Highest |
| Per-product override | Future Phase 3 | -- |

```python
# Resolution logic
rate = seller.commission_rate or config.mp_commission_rate or 0.0
```

## Commission Flow

```
Order Delivered + Invoiced
    ↓
Calculate commission per seller line
    ↓
Create seller.payment record
    ↓
Create ~~payment journal entry (account.move)
    ↓
Credit ~~wallet (auto)
    ↓
Seller sees balance in LIFF wallet
```

## Key Model: seller.payment

```python
class SellerPayment(models.Model):
    _name = 'seller.payment'

    seller_id = fields.Many2one('res.partner')
    payment_amount = fields.Float()      # seller receives
    commission_amount = fields.Float()   # platform keeps
    state = fields.Selection([
        ('draft', 'Draft'),
        ('requested', 'Requested'),
        ('approved', 'Approved'),
        ('paid', 'Paid'),
    ])
    sale_order_ids = fields.Many2many('sale.order')
    invoice_id = fields.Many2one('account.move')
```

## Settlement Trigger

`account_move.py:create_seller_payment_new()`:
1. Groups confirmed order lines by seller
2. Calculates commission at seller's rate
3. Creates `seller.payment` record
4. Creates journal entry via ~~payment
5. Auto-credits ~~wallet balance

## Owned Files

| File | Purpose |
|------|---------|
| `core_marketplace/models/seller_payment.py` | seller.payment model |
| `core_marketplace/models/seller_payment_method.py` | Payment method configuration |
| `core_marketplace/models/account_move.py` | create_seller_payment_new() settlement |
| `core_marketplace/models/res_config.py` | Global commission rate setting |
| `core_marketplace/views/mp_seller_payment_view.xml` | Commission management views |

## Anti-Patterns

| Don't | Do Instead |
|-------|-----------|
| Hard-code commission rate | Use config hierarchy (per-seller > global) |
| Calculate commission before delivery | Only after delivery + invoice confirmed |
| Skip journal entry creation | Every commission must have an `account.move` |
| Allow rate change to affect past orders | Rate locked at settlement time |
| Let seller modify commission records | Read-only for sellers, managed by system |

## Cross-References

| Direction | Skill | Interaction |
|-----------|-------|-------------|
| ← | [order-processing](../../../commerce/skills/order-processing/SKILL.md) | Order delivered → trigger commission |
| → | [wallet-system](../wallet-system/SKILL.md) | Commission paid → auto-credit wallet |
| → | [accounting-entries](../accounting-entries/SKILL.md) | Commission → journal entry |
| → | [financial-reporting](../financial-reporting/SKILL.md) | Commission data → revenue reports |
| ← | [seller-lifecycle](../../../seller-engine/skills/seller-lifecycle/SKILL.md) | Seller approval sets commission rate |
