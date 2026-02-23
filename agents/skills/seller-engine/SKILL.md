---
name: seller-engine
description: Seller lifecycle and experience management. Activate when working on
  seller registration, approval/rejection, shop profiles, reviews, ratings, seller
  dashboard, seller onboarding, or seller status transitions.
---

# S1: Seller Engine (ระบบผู้ขาย)

You are an expert at managing the complete seller lifecycle — from application to active selling. You handle seller registration, approval workflows, shop profile management, customer reviews, and seller analytics dashboards.

> If you see unfamiliar `~~category` placeholders, see [CONNECTORS.md](../../CONNECTORS.md).

## Seller Status Flow

```
none → draft (สมัคร) → pending (รอตรวจ) → approved (อนุมัติ)
                                          ↓
                                     denied (ปฏิเสธ)
```

| Transition | Trigger | Side Effects |
|-----------|---------|-------------|
| none → draft | Buyer clicks "สมัครเป็นผู้ขาย" | Create draft seller record |
| draft → pending | Seller submits documents | ~~notification to admin |
| pending → approved | Officer approves | Assign `marketplace_seller_group`, create seller.shop, create ~~wallet, ~~rich-menu switch, ~~messaging notify seller |
| pending → denied | Officer rejects | ~~messaging notify seller with reason |
| approved → pending | Re-review needed | Temporarily suspend selling |

## Owned Files

### Models (~~marketplace-engine)
| File | Model | Purpose |
|------|-------|---------|
| `core_marketplace/models/res_partner.py` | res.partner (ext) | Seller profile, status, approval |
| `core_marketplace/models/seller_shop.py` | seller.shop | Shop branding, settings, URL |
| `core_marketplace/models/seller_review.py` | seller.review | Customer reviews, ratings |
| `core_marketplace/models/marketplace_dashboard.py` | marketplace.dashboard | Sales analytics |
| `core_marketplace/models/res_users.py` | res.users (ext) | User extensions for sellers |

### Views
| File | Purpose |
|------|---------|
| `views/seller_view.xml` | Seller management backend |
| `views/res_partner_view.xml` | Partner/seller form |
| `views/seller_shop_view.xml` | Shop configuration |
| `views/seller_review_view.xml` | Review management |
| `views/mp_dashboard_view.xml` | Dashboard views |

### Email Templates (~~notification)
| File | Trigger |
|------|---------|
| `edi/seller_creation_mail_to_admin.xml` | New seller application |
| `edi/seller_creation_mail_to_seller.xml` | Application confirmation |
| `edi/seller_status_change_mail_to_admin.xml` | Status changed |
| `edi/seller_status_change_mail_to_seller.xml` | Approval/rejection notice |

## Key Data Models

### res.partner (seller extension)
```python
seller_status = fields.Selection([
    ('none', 'None'), ('draft', 'Draft'), ('pending', 'Pending'),
    ('approved', 'Approved'), ('denied', 'Denied'),
])
seller = fields.Boolean()
marketplace_seller_id = fields.Many2one('res.partner')
```

### seller.shop
```python
seller_id = fields.Many2one('res.partner')
shop_name = fields.Char()
url_handler = fields.Char()  # required, e.g. "shop-46"
logo = fields.Binary()
banner = fields.Binary()
description = fields.Html()
```

### seller.review
```python
seller_id = fields.Many2one('res.partner')
customer_id = fields.Many2one('res.partner')
rating = fields.Float()
review_text = fields.Text()
```

## Shop Staff System

| Role | Can Do | Cannot Do |
|------|--------|-----------|
| **Owner** | Everything: wallet, withdrawal, shop settings, orders, approve | — |
| **Staff** | Post + edit products only | Wallet, withdrawal, shop settings, orders |

- Model: `seller.shop.staff` (shop_id, staff_partner_id, role, is_active)
- Constraint: `unique(staff_partner_id)` — 1 person = 1 shop only
- Pattern: `require_seller` decorator resolves staff → shop owner's partner

## Interfaces

| Direction | Agent | What |
|-----------|-------|------|
| → | [commerce](../commerce/SKILL.md) | Approved sellers can create products |
| → | [commission-wallet](../commission-wallet/SKILL.md) | Approved seller triggers wallet creation |
| → | [line-integration](../line-integration/SKILL.md) | Status changes trigger ~~messaging notifications |
| → | [liff-frontend](../liff-frontend/SKILL.md) | Seller data displayed in LIFF apps |

## Anti-Patterns

| Don't | Do Instead |
|-------|-----------|
| Change seller status without wizard | Always use status wizard (audit trail) |
| Skip security group assignment on approval | Auto-assign in `res_partner.write()` |
| Let staff access wallet/withdrawal | Use `@owner_only` decorator |
| Create shop without `url_handler` | Always set `url_handler=f"shop-{partner.id}"` |
| Forget ~~wallet creation on approval | Auto-create in `res_partner.write()` |

## Related Commands

- [/approve-seller](../../commands/approve-seller.md) — Seller approval workflow
