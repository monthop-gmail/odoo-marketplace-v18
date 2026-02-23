---
name: staff-management
description: Shop staff (ผู้ช่วย) permission system. Activate when working on owner vs staff roles, staff invitations, staff permissions, context switching, or the require_seller decorator.
---

# Staff Management (ระบบผู้ช่วย)

You manage the shop staff system — allowing shop owners to invite helpers who can post and edit products, while restricting access to sensitive operations like wallet and withdrawals.

> If you see unfamiliar `~~category` placeholders, see [CONNECTORS.md](../../CONNECTORS.md).

## Core Concept

**ยิ่งมีคนช่วย post → สินค้าเยอะ → Marketplace มีคุณค่า**

| Role | Can Do | Cannot Do |
|------|--------|-----------|
| **Owner** | Everything: wallet, withdrawal, shop settings, orders, approve | — |
| **Staff** | Post + edit products only | Wallet, withdrawal, shop settings, orders |

## Key Model: seller.shop.staff

```python
shop_id = fields.Many2one('seller.shop')
staff_partner_id = fields.Many2one('res.partner')
role = fields.Selection()
is_active = fields.Boolean()
invited_by = fields.Many2one('res.partner')
```

**Constraint:** `unique(staff_partner_id)` — 1 person = 1 shop only

## Context Switch Pattern

`require_seller` decorator resolves staff → shop owner's partner:
- `request.seller_partner` → owner partner (for all product operations)
- `request.is_shop_owner` → True/False
- `request.is_shop_staff` → True/False
- `request.staff_record` → staff record (if staff)

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/line-seller/staff` | GET | List shop staff |
| `/api/line-seller/staff` | POST | Invite new staff |
| `/api/line-seller/staff/<id>` | DELETE | Remove staff |
| `/api/line-seller/staff/my-status` | GET | Current user's staff status |
| `/api/line-admin/shops/<id>/staff` | GET | Admin: list staff |
| `/api/line-admin/shops/<id>/staff` | POST | Admin: add staff |
| `/api/line-admin/shops/<id>/staff/<id>` | DELETE | Admin: remove staff |

## LINE Sync

Staff gets `member_type='seller'` via `sync_member_type_from_partner()` → seller rich menu assigned.

## LIFF UI

- Staff sees "staff banner" in seller app
- Wallet nav button hidden for staff
- Shop settings button hidden for staff

## Owned Files

| File | Purpose |
|------|---------|
| `core_marketplace/models/seller_shop_staff.py` | Staff model |
| `core_line_integration/controllers/api_seller_staff.py` | Seller staff API |
| `core_line_integration/controllers/api_admin_staff.py` | Admin staff API |

## Anti-Patterns

| Don't | Do Instead |
|-------|-----------|
| Let staff access wallet/withdrawal | Use `@owner_only` decorator |
| Allow staff in multiple shops | Enforce `unique(staff_partner_id)` |
| Skip LINE sync for new staff | Call `sync_member_type_from_partner()` |
| Let staff edit shop profile | Check `is_shop_owner` before allowing |

## Cross-References

- ← [shop-management](../shop-management/SKILL.md) — Staff belongs to a shop
- → [commerce/product-lifecycle](../../commerce/skills/product-lifecycle/SKILL.md) — Staff can create/edit products
- → [line-platform/user-identity](../../line-platform/skills/user-identity/SKILL.md) — Staff member type sync
