---
name: seller-lifecycle
description: Seller status transitions and approval workflow. Activate when working on seller registration, status changes (none→draft→pending→approved/denied), approval logic, security group assignment, or seller rejection.
---

# Seller Lifecycle (วงจรชีวิตผู้ขาย)

You manage the complete seller status flow — from initial application through approval or rejection. Every status transition triggers side effects across the platform.

> If you see unfamiliar `~~category` placeholders, see [CONNECTORS.md](../../CONNECTORS.md).

## Status Flow

```
none → draft (สมัคร) → pending (รอตรวจ) → approved (อนุมัติ)
                                          ↓
                                     denied (ปฏิเสธ)
```

## Transition Side Effects

| Transition | Trigger | Side Effects |
|-----------|---------|-------------|
| none → draft | Buyer clicks "สมัครเป็นผู้ขาย" | Create draft seller record |
| draft → pending | Seller submits application | ~~notification to admin |
| pending → approved | Officer approves | Assign `marketplace_seller_group`, create seller.shop (`url_handler=shop-{id}`), create ~~wallet, ~~rich-menu switch to seller, ~~messaging notify |
| pending → denied | Officer rejects | ~~messaging notify with reason |
| approved → pending | Re-review needed | Temporarily suspend selling |

## Key Model: res.partner (seller extension)

```python
seller_status = fields.Selection([
    ('none', 'None'), ('draft', 'Draft'), ('pending', 'Pending'),
    ('approved', 'Approved'), ('denied', 'Denied'),
])
seller = fields.Boolean()
marketplace_seller_id = fields.Many2one('res.partner')
```

## Security Groups (assigned on approval)

```
marketplace_manager_group (Manager) — full access
  └── marketplace_officer_group (Officer) — seller approval
       └── marketplace_seller_group (Approved Seller)
            └── marketplace_draft_seller_group (Pending Seller)
```

## Owned Files

| File | Purpose |
|------|---------|
| `core_marketplace/models/res_partner.py` | Seller status, approval logic |
| `core_marketplace/views/seller_view.xml` | Seller management views |
| `core_marketplace/views/res_partner_view.xml` | Partner form extensions |
| `core_marketplace/edi/seller_*.xml` | Email notification templates |

## Decision Table

| Situation | Action |
|-----------|--------|
| Seller applies with incomplete docs | Keep in draft, prompt for missing fields |
| Officer approves pending seller | Full side-effect chain (shop + wallet + menu + notify) |
| Seller denied wants to reapply | Allow new draft submission |
| Approved seller violates policy | Transition back to pending for re-review |

## Anti-Patterns

| Don't | Do Instead |
|-------|-----------|
| Change status without wizard | Use status wizard (audit trail) |
| Skip security group on approval | Auto-assign in `res_partner.write()` |
| Forget wallet creation | Auto-create in `res_partner.write()` |
| Create shop without url_handler | Always `url_handler=f"shop-{partner.id}"` |
| Use `.sudo()` on auth='none' | Use `.with_user(SUPERUSER_ID)` |

## Cross-References

- → [shop-management](../shop-management/SKILL.md) — Shop created on approval
- → [staff-management](../staff-management/SKILL.md) — Staff added after shop exists
- → [seller-onboarding](../seller-onboarding/SKILL.md) — Welcome flow post-approval
- → [finance/wallet-system](../../finance/skills/wallet-system/SKILL.md) — Wallet created on approval
- → [line-platform/notification-triggers](../../line-platform/skills/notification-triggers/SKILL.md) — Status change notifications
