---
name: product-lifecycle
description: Product creation, approval, and publishing workflow. Activate when working
  on Quick Post, product moderation, seller product submission, image processing,
  product status transitions, or admin approval/rejection.
---

# Product Lifecycle (วงจรชีวิตสินค้า)

You are an expert at managing product creation, review, and publishing in a multi-vendor marketplace. You handle the Quick Post mobile-first flow, image processing, category management, and Officer/Manager moderation workflows.

> If you see unfamiliar `~~category` placeholders, see [CONNECTORS.md](../../CONNECTORS.md).

## Product Status Flow

```
Draft ──→ Pending ──→ Approved ──→ Published
                  └──→ Rejected ──→ (Seller edits) ──→ Pending
```

| Status | Who Acts | Transitions | Notes |
|--------|----------|-------------|-------|
| Draft | Seller | → Pending (submit) | Initial creation via Quick Post or full form |
| Pending | Officer/Manager | → Approved, → Rejected | Moderation queue |
| Approved | Officer/Manager | → Published | Ready for storefront |
| Published | Officer/Manager | → Unpublished | Live on marketplace |
| Rejected | Seller (edit & resubmit) | → Pending | Reason shown to seller |

## Quick Post Concept

Core design principle: **ความสะดวกในการ post สินค้า คือสิ่งสำคัญที่สุด**

```
เจอสินค้าข้างนอก → เปิด LINE OA → ถ่ายรูป → กรอกราคา → Post ทันที
```

- Mobile-first: camera → name + price + category → submit in under 30 seconds
- Staff (ผู้ช่วย) can Quick Post on behalf of shop owner
- Category required: dropdown includes `+ สร้างหมวดหมู่ใหม่` for inline creation

## Image Processing

All product images are **center-cropped to square** before upload:

```javascript
// fileToBase64() in liff_seller/js/app.js
1. Read file → canvas
2. Center-crop to square (min dimension)
3. Resize to max 1024×1024
4. Export JPEG 85% quality
5. Return base64 string
```

## API Endpoints (via ~~api)

| Endpoint | Method | Role | Description |
|----------|--------|------|-------------|
| `/api/line-seller/products` | GET | Seller | List own products |
| `/api/line-seller/products` | POST | Seller | Create product (supports `categ_name`) |
| `/api/line-seller/products/<id>` | PUT | Seller | Update product |
| `/api/line-seller/products/<id>/images` | GET/POST/PUT/DELETE | Seller | Gallery CRUD |
| `/api/line-admin/products` | GET | Admin | All products (filterable by status) |
| `/api/line-admin/products/<id>/approve` | POST | Admin | Approve product |
| `/api/line-admin/products/<id>/reject` | POST | Admin | Reject with reason |

## Owned Files

| File | Purpose |
|------|---------|
| `core_marketplace/models/marketplace_product.py` | product.template extension with status, seller_id |
| `core_line_integration/controllers/api_seller_products.py` | Seller product API + categ_name |
| `core_line_integration/controllers/api_admin_products.py` | Admin moderation API |
| `core_line_integration/static/liff_seller/js/app.js` | Quick Post UI, image crop |
| `core_marketplace/views/mp_product_view.xml` | Backend product moderation views |

## Anti-Patterns

| Don't | Do Instead |
|-------|-----------|
| Skip moderation step | Always require Officer/Manager approval |
| Upload raw images without crop | Center-crop to square + resize 1024px + JPEG 85% |
| Create duplicate categories | Dedup by name before creating (case-insensitive) |
| Let staff access publish toggle | Only Officer/Manager can publish |
| Use `product.product` ID from template API | Browse `product.template` → `.product_variant_id` |

## Cross-References

| Direction | Skill | Interaction |
|-----------|-------|-------------|
| ← | [seller-lifecycle](../../../seller-engine/skills/seller-lifecycle/SKILL.md) | Only approved sellers can create products |
| ← | [staff-management](../../../seller-engine/skills/staff-management/SKILL.md) | Staff can Quick Post for shop owner |
| → | [catalog-management](../catalog-management/SKILL.md) | Category and gallery management |
| → | [commission-engine](../../../finance/skills/commission-engine/SKILL.md) | Product sale triggers commission |
| ← | [messaging-api](../../../line-platform/skills/messaging-api/SKILL.md) | Approval/rejection → LINE notify seller |
