---
name: product-search
description: Activate when searching for products in the marketplace catalog. Covers
  search fields, filtering, sorting, API endpoints with parameters, and search
  optimization for the product.template model.
---

# Product Search (Catalog Search Specialist)

You are a product search specialist who builds efficient queries against the marketplace product catalog, supporting full-text search, category filtering, price ranges, and seller-specific views.

> If you see unfamiliar `~~category` placeholders, see [CONNECTORS.md](../../../CONNECTORS.md).

## Search Fields

| Field | DB Column | Type | Searchable By |
|-------|-----------|------|--------------|
| Product Name | `product_template.name` | Text (ILIKE) | All roles |
| Category | `product_template.categ_id` | Many2one | All roles |
| Seller | `product_template.marketplace_seller_id` | Many2one | All roles |
| Price | `product_template.list_price` | Float range | All roles |
| Status | `product_template.status_cust` | Selection | Admin, Seller |
| Published | `product_template.website_published` | Boolean | Admin |
| Created Date | `product_template.create_date` | Date range | Admin |
| Stock Qty | `stock_quant.quantity` | Float | Seller (own), Admin |

## API Endpoints

| Endpoint | Method | Role | Parameters |
|----------|--------|------|-----------|
| `/api/line-buyer/products` | GET | Buyer | `search`, `category_id`, `min_price`, `max_price`, `seller_id`, `sort`, `page`, `limit` |
| `/api/line-buyer/products/<id>` | GET | Buyer | -- |
| `/api/line-seller/products` | GET | Seller | `search`, `status`, `category_id`, `sort`, `page`, `limit` |
| `/api/line-seller/products/<id>` | GET | Seller | -- |
| `/api/line-admin/products` | GET | Admin | `search`, `seller_id`, `status`, `category_id`, `published`, `page`, `limit` |

## Sort Options

| Sort Value | SQL Order | Default For |
|-----------|-----------|-------------|
| `newest` | `create_date DESC` | Buyer browse |
| `price_asc` | `list_price ASC` | Price filter |
| `price_desc` | `list_price DESC` | Price filter |
| `popular` | `sales_count DESC` | Buyer home |
| `name` | `name ASC` | Admin list |
| `rating` | `seller_avg_rating DESC` | Future |

## Search Query Pattern

```python
domain = [('website_published', '=', True), ('status_cust', '=', 'approved')]
if search:
    domain += [('name', 'ilike', search)]
if category_id:
    domain += [('categ_id', '=', int(category_id))]
if min_price:
    domain += [('list_price', '>=', float(min_price))]
if max_price:
    domain += [('list_price', '<=', float(max_price))]
if seller_id:
    domain += [('marketplace_seller_id', '=', int(seller_id))]

products = env['product.template'].with_user(SUPERUSER_ID).search(
    domain, limit=limit, offset=offset, order=sort_order
)
```

## Search Optimization

| Technique | When | Benefit |
|-----------|------|---------|
| Database index on `name` | High product count (>1000) | Faster ILIKE |
| Category tree caching | Deep category hierarchy | Avoid recursive queries |
| Price range bucketing | Filter UI | Pre-computed ranges |
| Limit + offset pagination | All list endpoints | Bounded response size |
| `fields` parameter | API response | Reduce payload size |

## Response Format

```json
{
  "success": true,
  "data": {
    "products": [
      {"id": 1, "name": "...", "price": 299, "image_url": "...", "seller_name": "...", "category": "..."}
    ],
    "total": 150,
    "page": 1,
    "limit": 20
  }
}
```

## Cross-References

- [seller-search](../seller-search/SKILL.md) for finding sellers
- [order-search](../order-search/SKILL.md) for order lookup
- [cross-model-search](../cross-model-search/SKILL.md) for multi-model queries
- ~~marketplace-engine for product model details
- ~~api for endpoint conventions
