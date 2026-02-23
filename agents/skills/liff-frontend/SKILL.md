---
name: liff-frontend
description: LIFF Mini App frontend and REST API management. Activate when working on
  LIFF HTML/JS/CSS, API controllers, buyer/seller/admin app UI, product browsing,
  cart, checkout, mobile-first design, or any frontend user experience task.
---

# S5: LIFF Frontend (หน้าบ้าน LIFF Mini App)

You are an expert at building mobile-first LIFF Mini Apps for LINE. You manage 5 LIFF apps, all REST API controllers, and the HTML5/Vanilla JS frontend — delivering a fast, native-feeling shopping and selling experience inside LINE.

> If you see unfamiliar `~~category` placeholders, see [CONNECTORS.md](../../CONNECTORS.md).

## LIFF Apps

| App | Path | Users | Status |
|-----|------|-------|--------|
| **Buyer** | `static/liff/` | All users | ✅ 100% |
| **Seller** | `static/liff_seller/` | Approved sellers + staff | ✅ 100% |
| **Admin** | `static/liff_admin/` | Officers + Managers | ✅ 100% |
| **Promotion** | `static/liff_promotion/` | Marketing | ❌ 5% stub |
| **Support** | `static/liff_support/` | Customer service | ❌ 5% stub |

## Tech Stack

```
HTML5 + Vanilla JS (no framework)
├── index.html          → App entry point (SPA router)
├── js/
│   ├── config.js       → API base URL, LIFF ID
│   ├── api.js          → Fetch wrapper with auth headers
│   └── app.js          → Application logic + page routing
├── css/
│   └── style.css       → Mobile-first responsive styling
└── js/thai-address-data.js → Cascading province/district/subdistrict (404KB)
```

## API Endpoints (97 total)

### Buyer API (46 endpoints) — `/api/line-buyer/`

| Group | Endpoints | Key Operations |
|-------|-----------|---------------|
| Products | GET /products, /products/<id>, /categories | Browse, search, filter, detail with images[] |
| Cart | GET/POST/PUT/DELETE /cart | Add, update qty, remove items |
| Checkout | POST /checkout/place-order | Create order from cart |
| Orders | GET /orders, /orders/<id> | History, detail, tracking |
| Profile | GET/PUT /profile | View/edit name, phone, email |
| Addresses | CRUD /addresses + GET /provinces | Thai address with cascading dropdown |
| Wishlist | GET/POST/DELETE /wishlist | Favorite products |
| Compare | GET/POST/DELETE /compare | Product comparison |

### Seller API (28 endpoints) — `/api/line-seller/`

| Group | Endpoints | Key Operations |
|-------|-----------|---------------|
| Products | CRUD /products + /images | Create, edit, gallery upload |
| Orders | GET /orders, /orders/<id>/ship | View, process, ship |
| Dashboard | GET /dashboard | Sales stats, metrics |
| Wallet | GET /wallet, /transactions, POST /withdraw | Balance, history, withdrawal |
| Shop | GET/PUT /shop | Shop profile management |
| Staff | CRUD /staff | Owner manages staff members |

### Admin API (23 endpoints) — `/api/line-admin/`

| Group | Endpoints | Key Operations |
|-------|-----------|---------------|
| Members | GET /members | LINE member management |
| Sellers | GET/POST /sellers, /approve, /reject | Seller moderation |
| Products | GET/POST /products, /approve, /reject | Product moderation |
| Wallets | GET /wallets, /withdrawals | Wallet oversight |
| Dashboard | GET /dashboard | Platform analytics |

## LIFF Deep Link Pattern

LIFF SDK double-loads: first with `liff.state=?page%3Dprofile`, second reload with empty params.

```javascript
// Fix: save target page to sessionStorage before liff.init()
const params = new URLSearchParams(window.location.search);
if (params.get('page')) sessionStorage.setItem('targetPage', params.get('page'));

liff.init({ liffId }).then(() => {
    const page = sessionStorage.getItem('targetPage') || 'home';
    sessionStorage.removeItem('targetPage');
    navigateTo(page);
});
```

## Cascading Thai Address

```
จังหวัด (province) → อำเภอ (district) → ตำบล (subdistrict) → auto-fill zip
```

- Data: 77 provinces / 928 districts / 7,475 sub-districts
- Source: `static/liff/js/thai-address-data.js`
- Save mapping: district→city, subdistrict→street2

## Product Image Handling

- **Square crop**: `fileToBase64()` center-crops to square + resize max 1024px + JPEG 85%
- **Gallery**: grid UI in product form, add/remove images, batch upload on save
- **Category auto-create**: dropdown with `+ สร้างหมวดหมู่ใหม่` → API accepts `categ_name`

## Standalone / Supercharged

```
┌─────────────────────────────────────────────────┐
│              LIFF FRONTEND                       │
├─────────────────────────────────────────────────┤
│  STANDALONE (always works)                       │
│  ✓ Full HTML/CSS/JS app with mock auth           │
│  ✓ All pages render with sample data             │
│  ✓ API calls work with X-Line-User-Id header     │
├─────────────────────────────────────────────────┤
│  SUPERCHARGED (in LINE app)                      │
│  + Real LIFF SDK authentication                  │
│  + Native LINE profile integration               │
│  + ~~rich-menu deep links                        │
│  + Share to LINE chat                            │
│  + ~~messaging push notifications                │
└─────────────────────────────────────────────────┘
```

## Response Format Standard

```json
// Success
{ "success": true, "data": { ... } }

// Error
{ "success": false, "error": { "code": "VALIDATION_ERROR", "message": "..." } }

// Paginated
{ "success": true, "data": { "items": [...], "total": 100, "page": 1, "per_page": 20 } }
```

## Interfaces

| Direction | Agent | What |
|-----------|-------|------|
| ← | [seller-engine](../seller-engine/SKILL.md) | Seller profile data for display |
| ← | [commerce](../commerce/SKILL.md) | Product, cart, order data |
| ← | [commission-wallet](../commission-wallet/SKILL.md) | Wallet balance for seller dashboard |
| ↔ | [line-integration](../line-integration/SKILL.md) | Auth tokens, channel context, user identity |

## Anti-Patterns

| Don't | Do Instead |
|-------|-----------|
| Access database directly from JS | Always go through ~~api controllers |
| Store sensitive data in localStorage | Use sessionStorage for temporary page state only |
| Skip LIFF token on API calls | Always send `Authorization: Bearer <token>` |
| Use frameworks (React/Vue) | Keep vanilla JS — LIFF loads must be fast |
| Forget cache busting on deploy | Append `?v=N` to CSS/JS imports |
| Browse `product.product` with template ID | Browse `product.template` → `.product_variant_id` |
| Dump all form fields at once | Conversational UX — show essentials first |

## Related Commands

- [/quick-post](../../commands/quick-post.md) — Mobile-first product posting flow
