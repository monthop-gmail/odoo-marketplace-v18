---
name: seller-search
description: Activate when searching for sellers in the marketplace directory. Covers
  search fields, status filtering, shop lookup, rating queries, and role-specific
  API endpoints.
---

# Seller Search (Directory Specialist)

You are a seller search specialist who queries the marketplace seller directory by name, status, shop, rating, and activity level, with role-appropriate access controls.

> If you see unfamiliar `~~category` placeholders, see [CONNECTORS.md](../../../CONNECTORS.md).

## Search Fields

| Field | DB Column | Type | Searchable By |
|-------|-----------|------|--------------|
| Seller Name | `res_partner.name` | Text (ILIKE) | All roles |
| Status | `res_partner.seller_status` | Selection | Admin |
| Shop Name | `seller_shop.shop_name` | Text (ILIKE) | All roles |
| Shop URL | `seller_shop.url_handler` | Exact match | System |
| Rating | `seller_review` AVG(rating) | Float range | Buyer, Admin |
| Province | `res_partner.state_id` | Many2one | Buyer |
| Joined Date | `res_partner.create_date` | Date range | Admin |
| Product Count | Computed from `product_template` | Integer | Admin |
| LINE User ID | `line_channel_member.line_user_id` | Exact match | System |

## API Endpoints

| Endpoint | Method | Role | Parameters |
|----------|--------|------|-----------|
| `/api/line-buyer/sellers` | GET | Buyer | `search`, `category_id`, `sort`, `page`, `limit` |
| `/api/line-buyer/sellers/<id>` | GET | Buyer | -- |
| `/api/line-buyer/shops/<url>` | GET | Buyer | -- |
| `/api/line-admin/sellers` | GET | Admin | `search`, `status`, `sort`, `page`, `limit` |
| `/api/line-admin/sellers/<id>` | GET | Admin | -- |
| `/api/line-admin/sellers/<id>/approve` | POST | Admin | -- |
| `/api/line-admin/sellers/<id>/deny` | POST | Admin | `reason` |

## Status Values

| Status | Meaning | Visible to Buyer |
|--------|---------|-----------------|
| `none` | Not a seller | No |
| `draft` | Started application | No |
| `pending` | Awaiting approval | No |
| `approved` | Active seller | Yes |
| `denied` | Application rejected | No |

## Search Domain Pattern

```python
# Buyer: only see approved sellers with published shops
domain = [('seller_status', '=', 'approved')]
if search:
    domain = ['|',
        ('name', 'ilike', search),
        ('seller_shop_ids.shop_name', 'ilike', search)
    ] + domain

# Admin: see all sellers, filter by status
domain = []
if status:
    domain += [('seller_status', '=', status)]
if search:
    domain += ['|', ('name', 'ilike', search), ('email', 'ilike', search)]
```

## Sort Options

| Sort Value | Order | Default For |
|-----------|-------|-------------|
| `name` | `name ASC` | Admin list |
| `newest` | `create_date DESC` | Admin pending |
| `rating` | Computed, DESC | Buyer browse |
| `products` | Computed, DESC | Buyer popular |
| `revenue` | Computed, DESC | Admin analytics |

## Response Format

```json
{
  "success": true,
  "data": {
    "sellers": [
      {"id": 46, "name": "Jacks Sparrow", "shop_name": "shop name",
       "rating": 4.5, "product_count": 12, "image_url": "..."}
    ],
    "total": 25,
    "page": 1
  }
}
```

## Cross-References

- [product-search](../product-search/SKILL.md) for product catalog queries
- [order-search](../order-search/SKILL.md) for seller order lookup
- [cross-model-search](../cross-model-search/SKILL.md) for multi-model queries
- ~~marketplace-engine for seller model details
- ~~identity for LINE user mapping
