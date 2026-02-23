# /review-product

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).

Review and approve or reject a marketplace product.

## Usage

```
/review-product <product_name_or_id>
/review-product --pending    # List all pending products
```

## How It Works

```
┌─────────────────────────────────────────────────────┐
│                 REVIEW PRODUCT                       │
├─────────────────────────────────────────────────────┤
│  STANDALONE (always works)                           │
│  ✓ Review product data and images                    │
│  ✓ Check compliance with listing guidelines          │
│  ✓ Generate approval/rejection recommendation        │
├─────────────────────────────────────────────────────┤
│  SUPERCHARGED (when ~~marketplace-engine connected)  │
│  + Pull product from Odoo                            │
│  + Execute approval in DB                            │
│  + Publish to website                                │
│  + Send ~~messaging notification to seller           │
└─────────────────────────────────────────────────────┘
```

## Workflow

1. **Fetch Product** — Pull from ~~marketplace-engine (product.template)
2. **Review** — Check images, description, price, category
3. **Compliance Check** — Against listing guidelines
4. **Recommend** — Approve or reject with reason
5. **Execute** — On approval: set status, publish
6. **Notify** — Send ~~messaging to seller

## Listing Guidelines

| Rule | Check |
|------|-------|
| Has main image | At least 1 product image |
| Has description | Non-empty product description |
| Has price | Price > 0 |
| Has category | Category assigned |
| Appropriate content | No prohibited items |
| Clear title | Descriptive, not misleading |

## Output

```markdown
## Product Review

**Product:** [name] (template_id: [id])
**Seller:** [seller_name] (partner_id: [id])
**Price:** ฿[price]
**Category:** [category]
**Images:** [count]

### Compliance
- [x/✗] Main image present
- [x/✗] Description filled
- [x/✗] Valid price
- [x/✗] Category assigned
- [x/✗] Content appropriate

### Recommendation
[APPROVE/REJECT] — [reason]
```

## Next Steps

- Want me to approve this product?
- Should I reject with a specific reason?
- Want to see more pending products?

## Related Skills

- Uses [commerce](../skills/commerce/SKILL.md) for product lifecycle
- Triggers [line-integration](../skills/line-integration/SKILL.md) for seller notification
