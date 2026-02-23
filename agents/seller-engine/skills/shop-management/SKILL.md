---
name: shop-management
description: Shop profile and branding management. Activate when working on seller shop creation, shop profile editing, shop URL, logo, banner, description, or shop settings.
---

# Shop Management (จัดการร้านค้า)

You manage seller shop profiles — branding, URLs, logos, banners, and shop settings. Each approved seller gets exactly one shop.

> If you see unfamiliar `~~category` placeholders, see [CONNECTORS.md](../../CONNECTORS.md).

## Shop Lifecycle

```
Seller approved → seller.shop created (auto) → Owner edits profile → Published
```

## Key Model: seller.shop

```python
seller_id = fields.Many2one('res.partner')  # owner
shop_name = fields.Char(required=True)
url_handler = fields.Char(required=True)    # e.g. "shop-46"
logo = fields.Binary()
banner = fields.Binary()
description = fields.Html()
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/line-seller/shop` | GET | Get shop profile |
| `/api/line-seller/shop` | PUT | Update shop profile |

## Owned Files

| File | Purpose |
|------|---------|
| `core_marketplace/models/seller_shop.py` | Shop model |
| `core_marketplace/views/seller_shop_view.xml` | Shop backend views |
| `core_line_integration/controllers/api_seller_shop.py` | Shop API |

## Rules

- One shop per approved seller (auto-created on approval)
- `url_handler` is required and immutable after creation
- Only owner can edit shop profile (not staff)
- Logo/banner images should be reasonable size

## Anti-Patterns

| Don't | Do Instead |
|-------|-----------|
| Create shop without seller approval | Auto-create only on approval |
| Allow staff to edit shop settings | Use `@owner_only` decorator |
| Make url_handler editable | Set once at creation |

## Cross-References

- ← [seller-lifecycle](../seller-lifecycle/SKILL.md) — Shop created on approval
- → [staff-management](../staff-management/SKILL.md) — Staff belongs to shop
- → [liff-apps/seller-app](../../liff-apps/skills/seller-app/SKILL.md) — Shop profile in LIFF
