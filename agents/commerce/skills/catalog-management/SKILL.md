---
name: catalog-management
description: Product categories and image gallery management. Activate when working on
  category creation/dedup, product.image gallery, image upload/reorder, square
  crop processing, or category hierarchy.
---

# Catalog Management (การจัดการแคตาล็อก)

You are an expert at managing the product catalog structure including categories, product image galleries, and media processing in the marketplace.

> If you see unfamiliar `~~category` placeholders, see [CONNECTORS.md](../../CONNECTORS.md).

## Category System

### Auto-Create with Dedup
Sellers can create categories inline during product creation:

```python
# In api_seller_products.py
if categ_name:
    existing = env['product.public.category'].search([
        ('name', '=ilike', categ_name)  # case-insensitive dedup
    ], limit=1)
    if existing:
        categ_id = existing.id
    else:
        categ_id = env['product.public.category'].create({
            'name': categ_name
        }).id
```

- Category is **required** for both Quick Post and full product form
- Dropdown includes `+ สร้างหมวดหมู่ใหม่` option in LIFF UI
- Model: `product.public.category` (Odoo standard from `website_sale`)

## Product Image Gallery

Uses existing `product.image` model from `website_sale` module:

```python
class ProductImage(models.Model):
    _name = 'product.image'
    product_tmpl_id = fields.Many2one('product.template')
    name = fields.Char()
    image_1920 = fields.Image()
    sequence = fields.Integer()  # display order
```

### Square Crop Pipeline

All uploaded images are processed client-side before upload:

```
Camera/file → Read as Image → Center-crop to square
    → Resize max 1024×1024 → JPEG quality 85% → Base64 → API
```

### Gallery API (via ~~api)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/line-seller/products/<id>/images` | GET | List gallery images |
| `/api/line-seller/products/<id>/images` | POST | Upload new image |
| `/api/line-seller/products/<id>/images/<img_id>` | PUT | Update/reorder image |
| `/api/line-seller/products/<id>/images/<img_id>` | DELETE | Remove image |

### Buyer Product Detail
- Detail API returns `images[]` array with all gallery images
- LIFF buyer modal shows main image + thumbnail gallery

## Owned Files

| File | Purpose |
|------|---------|
| `core_marketplace/models/marketplace_product.py` | Product category assignment |
| `core_line_integration/controllers/api_seller_products.py` | Gallery CRUD + categ_name support |
| `core_line_integration/static/liff_seller/js/app.js` | Square crop, gallery UI, batch upload |
| `core_line_integration/static/liff/js/app.js` | Buyer product detail with gallery display |

## Anti-Patterns

| Don't | Do Instead |
|-------|-----------|
| Create duplicate categories | Always dedup by name (case-insensitive) before creating |
| Upload raw unprocessed images | Center-crop to square + resize 1024px + JPEG 85% |
| Skip sequence on gallery images | Always set sequence for consistent ordering |
| Allow gallery for non-owned products | Validate `marketplace_seller_id` matches current seller |

## Cross-References

| Direction | Skill | Interaction |
|-----------|-------|-------------|
| ← | [product-lifecycle](../product-lifecycle/SKILL.md) | Category required on product creation |
| ← | [order-processing](../order-processing/SKILL.md) | Product images shown in cart/order |
| ← | [staff-management](../../../seller-engine/skills/staff-management/SKILL.md) | Staff can manage gallery for shop owner |
