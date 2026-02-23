---
name: admin-app
description: Admin LIFF Mini App frontend. Activate when working on admin dashboard, member management, seller approval/rejection, product moderation, wallet oversight, withdrawal management, or admin app UI.
---

# Admin App (แอปผู้ดูแล)

You manage the admin LIFF Mini App — the platform moderation and oversight tool for officers and managers inside LINE.

> If you see unfamiliar `~~category` placeholders, see [CONNECTORS.md](../../CONNECTORS.md).

## App Location
`core_line_integration/static/liff_admin/` — Status: ✅ 100%

## Tech Stack
HTML5 + Vanilla JS: index.html, js/config.js, js/api.js, js/app.js, css/style.css

## Pages

| Page | Route | Features |
|------|-------|----------|
| Dashboard | dashboard | Platform metrics, pending counts, charts |
| Members | members | LINE member list, search, role filter |
| Sellers | sellers | Seller list with approve/reject actions |
| Seller Detail | seller/<id> | Full seller profile, documents, history |
| Products | products | Product queue with approve/reject actions |
| Product Detail | product/<id> | Product info, images, seller context |
| Wallets | wallets | All seller wallet balances |
| Withdrawals | withdrawals | Withdrawal requests with approve/process |
| Staff | staff/<shop_id> | View/manage shop staff members |

## Moderation Workflow

### Seller Approval
```
1. New seller application arrives (status=pending)
2. Admin reviews: name, ID card, shop info
3. Action: Approve → seller_status=approved, wallet created, rich menu assigned
         Reject → seller_status=denied, LINE notification sent
```

### Product Approval
```
1. Seller posts product (status=pending)
2. Admin reviews: images, name, price, category, description
3. Action: Approve → product published on marketplace
         Reject → seller notified with reason
```

### Withdrawal Processing
```
1. Seller requests withdrawal (status=pending)
2. Admin reviews: amount, balance check, cooldown period
3. Action: Approve → status=processing → Complete with ref number
         Reject → balance restored, seller notified
```

## Key API Endpoints (via ~~api)

| Action | Method | Endpoint |
|--------|--------|----------|
| Dashboard | GET | /api/line-admin/dashboard |
| Members | GET | /api/line-admin/members |
| Sellers list | GET | /api/line-admin/sellers |
| Approve seller | POST | /api/line-admin/sellers/<id>/approve |
| Reject seller | POST | /api/line-admin/sellers/<id>/reject |
| Products list | GET | /api/line-admin/products |
| Approve product | POST | /api/line-admin/products/<id>/approve |
| Reject product | POST | /api/line-admin/products/<id>/reject |
| Wallets | GET | /api/line-admin/wallets |
| Withdrawals | GET/POST | /api/line-admin/withdrawals |
| Shop staff | GET/POST/DELETE | /api/line-admin/shops/<id>/staff |

## Dashboard Metrics
- Total members, sellers (by status), products (by status)
- Pending seller applications count
- Pending product reviews count
- Pending withdrawal requests count
- Revenue and commission totals

## Anti-Patterns

| Don't | Do Instead |
|-------|-----------|
| Auto-approve without review | Always require manual admin action |
| Skip rejection reason | Require reason text for seller/product reject |
| Show raw error to admin | Friendly Thai error messages with action hints |
| Allow approve from list view only | Require detail view for informed decisions |

## Cross-References
- [api-design](../api-design/SKILL.md) — API conventions and admin auth
- [mobile-ux](../mobile-ux/SKILL.md) — Admin-specific mobile patterns
- [buyer-app](../buyer-app/SKILL.md) — Shared component patterns
