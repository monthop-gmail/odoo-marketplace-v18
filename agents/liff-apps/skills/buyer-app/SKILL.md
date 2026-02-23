---
name: buyer-app
description: Buyer LIFF Mini App frontend. Activate when working on buyer shopping experience, product browsing, cart, checkout, order history, wishlist, compare, or buyer profile UI.
---

# Buyer App (แอปผู้ซื้อ)

You manage the buyer LIFF Mini App — the primary shopping experience inside LINE.

> If you see unfamiliar `~~category` placeholders, see [CONNECTORS.md](../../CONNECTORS.md).

## App Location
`core_line_integration/static/liff/` — Status: ✅ 100%

## Tech Stack
HTML5 + Vanilla JS (no framework): index.html, js/config.js, js/api.js, js/app.js, css/style.css, js/thai-address-data.js (404KB)

## Pages

| Page | Route | Features |
|------|-------|----------|
| Home | home | Product grid, search, categories |
| Product Detail | product/<id> | Gallery with thumbnails, description, add to cart |
| Cart | cart | Items, qty adjust, totals, checkout button |
| Checkout | checkout | Address selection, place order |
| Orders | orders | Order history list |
| Order Detail | order/<id> | Line items, status, tracking |
| Profile | profile | Name, phone, email editing |
| Addresses | addresses | Thai cascading address CRUD |
| Wishlist | wishlist | Saved products |
| Compare | compare | Side-by-side product comparison |
| Seller Apply | seller-apply | Seller application form with file upload |

## Product Card Features
- Product image, name, price
- "รายละเอียด" button opens detail modal (gallery, seller name, category, description)
- "หยิบใส่ตะกร้า" button calls `quickAddToCart(productId)` for 1-tap add

## Key API Endpoints (via ~~api)

| Action | Method | Endpoint |
|--------|--------|----------|
| Browse products | GET | /api/line-buyer/products |
| Product detail | GET | /api/line-buyer/products/<id> |
| Categories | GET | /api/line-buyer/categories |
| Cart operations | GET/POST/PUT/DELETE | /api/line-buyer/cart |
| Place order | POST | /api/line-buyer/checkout/place-order |
| Order history | GET | /api/line-buyer/orders |
| Profile | GET/PUT | /api/line-buyer/profile |
| Addresses | CRUD | /api/line-buyer/addresses |
| Wishlist | GET/POST/DELETE | /api/line-buyer/wishlist |

## CSS Classes

| Class | Purpose |
|-------|---------|
| `.product-card-actions` | Button container below product info |
| `.btn-card-detail` | "รายละเอียด" button style |
| `.btn-card-cart` | "หยิบใส่ตะกร้า" button style |
| `.pd-*` | Product detail modal elements |

## Cart Bug Fix (Important)
Products API returns `product.template.id`. Cart API must browse `product.template` first, then get `.product_variant_id`. Never browse `product.product` with a template ID.

## Anti-Patterns

| Don't | Do Instead |
|-------|-----------|
| Use React/Vue | Keep vanilla JS for fast LIFF loads |
| Store data in localStorage | sessionStorage for temp state only |
| Skip cache busting | Append `?v=N` on CSS/JS imports |
| Show all form fields at once | Progressive disclosure — essentials first |
| Hardcode Thai text in JS | Keep labels in HTML where possible |

## Cross-References
- [api-design](../api-design/SKILL.md) — API conventions and auth patterns
- [mobile-ux](../mobile-ux/SKILL.md) — Mobile-first design principles
- [thai-localization](../thai-localization/SKILL.md) — Thai address and label conventions
