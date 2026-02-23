# /search

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).

Cross-marketplace search across products, sellers, orders, and customers.

## Usage

```
/search <query>
/search "กระเป๋า"                   # Search everything
/search --seller "ร้านใหม่"         # Search sellers only
/search --order SO-1234             # Search orders only
/search --product "เสื้อ"           # Search products only
/search --all "keyword"             # Explicit all-entity search
```

## How It Works

```
┌─────────────────────────────────────────────────────┐
│                    SEARCH                             │
├─────────────────────────────────────────────────────┤
│  STANDALONE (always works)                           │
│  ✓ Parse search query and detect entity type         │
│  ✓ Build search plan across relevant models          │
│  ✓ Format results in structured tables               │
├─────────────────────────────────────────────────────┤
│  SUPERCHARGED (when ~~marketplace-engine connected)  │
│  + Query product.template with name/description ILIKE│
│  + Query res.partner (sellers) with name ILIKE       │
│  + Query sale.order with name or partner match       │
│  + Aggregate results with counts per entity          │
│  + Rank by relevance (exact > starts_with > contains)│
└─────────────────────────────────────────────────────┘
```

## Search Entities

| Entity | Model | Searchable Fields |
|--------|-------|-------------------|
| Products | product.template | name, description, categ_id.name |
| Sellers | res.partner (seller) | name, email, shop.name |
| Orders | sale.order | name, partner_id.name, state |
| Customers | res.partner (buyer) | name, email, phone |
| Shops | seller.shop | name, url_handler |

## Smart Detection

| Query Pattern | Detected Type | Example |
|---------------|--------------|---------|
| `SO-[digits]` | Order | SO-1234 |
| `shop-[digits]` | Shop | shop-46 |
| `@` in query | Customer (email) | user@example.com |
| `0[0-9]{8,9}` | Customer (phone) | 0812345678 |
| `partner_id:[digits]` | Partner | partner_id:46 |
| Anything else | All entities | กระเป๋า |

## Output

```markdown
## Search Results: "[query]"

**Found:** [n] products, [n] sellers, [n] orders

### Products ([count])
| ID | Name | Price | Seller | Category |
|----|------|-------|--------|----------|
| [id] | [name] | ฿[price] | [seller] | [category] |

### Sellers ([count])
| ID | Name | Shop | Products | Rating | Status |
|----|------|------|----------|--------|--------|
| [id] | [name] | [shop] | [count] | [rating] | [status] |

### Orders ([count])
| Order | Customer | Date | Total | Status |
|-------|----------|------|-------|--------|
| [name] | [customer] | [date] | ฿[amount] | [status] |
```

## Next Steps

- Want to see details for a specific result?
- Should I narrow the search with filters?
- Want to export these results?

## Related Skills

- Uses [enterprise-search](../skills/) for search logic and ranking
- Cross-references [commerce](../../commerce/skills/) for product models
- Cross-references [seller-engine](../../seller-engine/skills/) for seller models
