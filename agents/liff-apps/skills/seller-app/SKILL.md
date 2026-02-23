---
name: seller-app
description: Seller LIFF Mini App frontend. Activate when working on seller dashboard, Quick Post, product management, order processing, wallet, shop settings, staff management, or seller app UI.
---

# Seller App (แอปผู้ขาย)

You manage the seller LIFF Mini App — the mobile selling cockpit for approved sellers and their staff inside LINE.

> If you see unfamiliar `~~category` placeholders, see [CONNECTORS.md](../../CONNECTORS.md).

## App Location
`core_line_integration/static/liff_seller/` — Status: ✅ 100%

## Tech Stack
HTML5 + Vanilla JS: index.html, js/config.js, js/api.js, js/app.js, css/style.css

## Pages

| Page | Route | Access | Features |
|------|-------|--------|----------|
| Dashboard | dashboard | Owner + Staff | Sales stats, recent orders, metrics |
| Quick Post | quick-post | Owner + Staff | Camera → price → post (core feature) |
| Products | products | Owner + Staff | Product list with status filters |
| Product Form | product-form | Owner + Staff | Full edit with category + gallery |
| Orders | orders | Owner only | Order list, process, ship |
| Wallet | wallet | Owner only | Balance, transactions, withdrawal |
| Shop Settings | shop-settings | Owner only | Shop name, description, logo |
| Staff | staff | Owner only | Invite/remove staff members |

## Quick Post (Core Feature)

The heart of seller experience. Design principle: **เจอสินค้า → เปิด LINE → ถ่ายรูป → กรอกราคา → Post ทันที**

```
1. Tap "โพสต์สินค้า" (rich menu or dashboard)
2. Camera opens → take/select photo
3. Square crop + resize (1024px, JPEG 85%)
4. Enter: name, price, category (required)
5. Tap "โพสต์" → product created
```

Minimum fields: image, name, price, category. Everything else optional for speed.

## Image Processing
- `fileToBase64()` center-crops to square aspect ratio
- Resizes to max 1024x1024px
- Compresses to JPEG quality 85%
- Gallery supports batch upload on save

## Category Handling
- Dropdown with existing categories
- `+ สร้างหมวดหมู่ใหม่` option at bottom
- API accepts `categ_name` string to auto-create (dedup by name)

## Staff-Specific UI
When `is_shop_staff=true` (from GET /staff/my-status):
- Staff banner shown at top of app
- Wallet nav button **hidden**
- Shop settings button **hidden**
- Orders page **hidden**
- Only product management accessible

## Owner vs Staff Access

| Feature | Owner | Staff |
|---------|-------|-------|
| Quick Post | Yes | Yes |
| Edit products | Yes | Yes |
| View orders | Yes | No |
| Process orders | Yes | No |
| Wallet/withdraw | Yes | No |
| Shop settings | Yes | No |
| Manage staff | Yes | No |

## Key API Endpoints (via ~~api)

| Action | Method | Endpoint |
|--------|--------|----------|
| Dashboard | GET | /api/line-seller/dashboard |
| Products CRUD | GET/POST/PUT | /api/line-seller/products |
| Product images | GET/POST/PUT/DELETE | /api/line-seller/products/<id>/images |
| Orders | GET | /api/line-seller/orders |
| Ship order | POST | /api/line-seller/orders/<id>/ship |
| Wallet | GET | /api/line-seller/wallet |
| Withdraw | POST | /api/line-seller/withdraw |
| Staff | GET/POST/DELETE | /api/line-seller/staff |

## Anti-Patterns

| Don't | Do Instead |
|-------|-----------|
| Require all fields for Quick Post | Only image + name + price + category |
| Show wallet to staff | Check `is_shop_owner` before rendering |
| Upload raw camera photos | Always square-crop + compress first |
| Let staff access owner routes | `@owner_only` decorator blocks server-side |

## Cross-References
- [buyer-app](../buyer-app/SKILL.md) — Shared UI patterns and CSS
- [api-design](../api-design/SKILL.md) — API auth and response format
- [mobile-ux](../mobile-ux/SKILL.md) — Camera and touch UX patterns
