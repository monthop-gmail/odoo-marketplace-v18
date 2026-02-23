---
name: cross-model-search
description: Activate when a search query spans multiple models (products, sellers,
  orders) simultaneously. Covers search strategy, result aggregation, priority
  ranking by context, and unified response format.
---

# Cross-Model Search (Unified Search Specialist)

You are a cross-model search specialist who executes queries across products, sellers, and orders simultaneously, aggregates results, and ranks them by relevance to the user's context.

> If you see unfamiliar `~~category` placeholders, see [CONNECTORS.md](../../../CONNECTORS.md).

## Search Strategy

```
User Query
  Product Search (name, description ILIKE)
  Seller Search (name, shop_name ILIKE)
  Order Search (order name exact, product name ILIKE)
       |
  Aggregate Results
       |
  Rank by Context Priority
       |
  Return Unified Response
```

## Model Search Mapping

| Model | Search Fields | Weight | Result Type |
|-------|-------------|--------|-------------|
| product.template | name, description_sale | High | Product card |
| res.partner (seller) | name, seller_shop.shop_name | Medium | Seller card |
| sale.order | name (exact), partner_id.name | Medium | Order card |
| product.public.category | name | Low | Category link |
| line.channel.member | display_name, line_user_id | Low (admin only) | Member card |

## Priority by Context

| User Context | Primary Results | Secondary | Tertiary |
|-------------|----------------|-----------|----------|
| Buyer browsing | Products | Sellers | Categories |
| Buyer with order | Orders | Products | -- |
| Seller dashboard | Own products | Own orders | -- |
| Admin investigating | Orders | Sellers | Products |
| Admin user lookup | Members | Sellers | Orders |

## Result Aggregation Format

```json
{
  "success": true,
  "data": {
    "query": "search term",
    "results": {
      "products": {
        "items": [{"id": 1, "name": "...", "price": 299, "type": "product"}],
        "total": 15
      },
      "sellers": {
        "items": [{"id": 46, "name": "...", "shop_name": "...", "type": "seller"}],
        "total": 3
      },
      "orders": {
        "items": [{"id": 1, "name": "S00001", "amount": 1299, "type": "order"}],
        "total": 1
      }
    },
    "total_results": 19
  }
}
```

## Implementation Pattern

```python
def cross_model_search(env, query, role, limit=5):
    results = {}

    # Products (always search)
    products = env['product.template'].with_user(SUPERUSER_ID).search(
        [('name', 'ilike', query), ('website_published', '=', True)],
        limit=limit
    )
    results['products'] = format_products(products)

    # Sellers (buyer + admin)
    if role in ('buyer', 'admin'):
        sellers = env['res.partner'].with_user(SUPERUSER_ID).search(
            [('seller_status', '=', 'approved'),
             '|', ('name', 'ilike', query),
             ('seller_shop_ids.shop_name', 'ilike', query)],
            limit=limit
        )
        results['sellers'] = format_sellers(sellers)

    # Orders (admin only for cross-search)
    if role == 'admin':
        orders = env['sale.order'].with_user(SUPERUSER_ID).search(
            ['|', ('name', 'ilike', query),
             ('partner_id.name', 'ilike', query)],
            limit=limit
        )
        results['orders'] = format_orders(orders)

    return results
```

## Performance Considerations

| Concern | Mitigation |
|---------|-----------|
| Multiple model queries | Run in parallel or limit per model |
| Large result sets | Cap at `limit` per model (default 5) |
| Slow ILIKE on large tables | Database indexes on name fields |
| Unnecessary queries | Skip models not relevant to role |

## Cross-References

- [product-search](../product-search/SKILL.md) for product-specific queries
- [seller-search](../seller-search/SKILL.md) for seller-specific queries
- [order-search](../order-search/SKILL.md) for order-specific queries
- ~~marketplace-engine for model relationships
- ~~api for response format standards
