# /catalog-update

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).

Update catalog structure -- categories, featured products, and catalog organization.

## Usage

```
/catalog-update categories            # List all categories with product counts
/catalog-update --add-category <name> # Add a new product category
/catalog-update --featured            # Manage featured products
/catalog-update --reorganize          # Suggest category reorganization
```

## How It Works

```
┌─────────────────────────────────────────────────────┐
│                 CATALOG UPDATE                       │
├─────────────────────────────────────────────────────┤
│  STANDALONE (always works)                           │
│  ✓ Review category structure and naming              │
│  ✓ Suggest organization improvements                 │
│  ✓ Plan featured product rotation                    │
├─────────────────────────────────────────────────────┤
│  SUPERCHARGED (when ~~marketplace-engine connected)  │
│  + Pull category tree from Odoo (product.category)   │
│  + Create/rename/merge categories                    │
│  + Set featured products on storefront               │
│  + Update category images and descriptions           │
│  + Recount products per category                     │
└─────────────────────────────────────────────────────┘
```

## Category Management

- **Model**: `product.category` (Odoo standard, hierarchical)
- **Seller-created**: Sellers can create categories via Quick Post (`categ_name` param)
- **Dedup**: Auto-deduplication by name on creation
- **API**: `GET /api/line-buyer/categories` returns flat list

## Workflow

1. **List Categories** -- Pull category tree from ~~marketplace-engine
2. **Analyze** -- Count products, identify empty/duplicate categories
3. **Plan Changes** -- Propose additions, merges, renames
4. **Execute** -- Apply changes to Odoo
5. **Update Frontend** -- Category list auto-refreshes in ~~liff-app

## Output

```markdown
## Catalog Structure

**Total Categories:** [n]
**Total Products:** [n]

### Category Tree
| Category | Parent | Products | Active | Status |
|----------|--------|----------|--------|--------|
| [name] | [parent] | [count] | Yes/No | OK/Empty/Duplicate |

### Featured Products
| Product | Seller | Price | Category | Featured Since |
|---------|--------|-------|----------|---------------|
| [name] | [seller] | ฿[price] | [category] | [date] |

### Recommendations
- **Merge**: [cat_a] + [cat_b] → [merged_name] (similar products)
- **Rename**: [old_name] → [new_name] (clarity)
- **Archive**: [cat_name] (0 products, inactive)
- **Add**: [new_cat] (gap in product coverage)

### Changes Applied
| Action | Category | Result |
|--------|----------|--------|
| [Created/Merged/Renamed/Archived] | [name] | [status] |
```

## Next Steps

- Want me to create a new category?
- Should I merge duplicate categories?
- Want to update the featured product list?

## Related Skills

- Uses [product-catalog](../skills/product-catalog/SKILL.md) for product data
- Uses [buyer-app](../../liff-apps/skills/buyer-app/SKILL.md) for storefront display
