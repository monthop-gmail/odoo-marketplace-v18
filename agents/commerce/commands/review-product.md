# /review-product

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).

Review and approve or reject a marketplace product listing.

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
│  + Pull product from Odoo (product.template)         │
│  + Execute approval status change in DB              │
│  + Publish product to website                        │
│  + Send ~~messaging notification to seller           │
└─────────────────────────────────────────────────────┘
```

## Workflow

1. **Fetch Product** -- Pull from ~~marketplace-engine (product.template)
2. **Review** -- Check images, description, price, category
3. **Compliance Check** -- Against listing guidelines below
4. **Recommend** -- Approve or reject with reason
5. **Execute** -- On approval: set status, publish to storefront
6. **Notify** -- Send ~~messaging to seller with result

## Listing Guidelines

| Rule | Check | Severity |
|------|-------|----------|
| Has main image | At least 1 product image (square, min 500px) | Required |
| Has description | Non-empty, informative product description | Required |
| Valid price | Price > 0, reasonable for category | Required |
| Category assigned | Must belong to a product category | Required |
| Appropriate content | No prohibited/counterfeit items | Required |
| Clear title | Descriptive, not misleading, no keyword spam | Required |
| Gallery images | Additional angles/detail photos | Recommended |
| Stock set | Initial stock quantity configured | Recommended |

## Output

```markdown
## Product Review

**Product:** [name] (template_id: [id])
**Seller:** [seller_name] (partner_id: [id])
**Shop:** [shop_name]
**Price:** ฿[price]
**Category:** [category]
**Images:** [count] (main + [gallery_count] gallery)
**Created:** [date]

### Compliance Checklist
- [x/✗] Main image present and quality acceptable
- [x/✗] Description filled and informative
- [x/✗] Valid price (฿[price])
- [x/✗] Category assigned ([category])
- [x/✗] Content appropriate (no prohibited items)
- [x/✗] Clear, descriptive title

### Recommendation
[APPROVE/REJECT] -- [reason]

### Notes
[Any additional observations or required seller actions]
```

## Next Steps

- Want me to approve this product?
- Should I reject with a specific reason for the seller?
- Want to see more pending products?

## Related Skills

- Uses [product-catalog](../skills/product-catalog/SKILL.md) for product lifecycle
- Uses [inventory](../skills/inventory/SKILL.md) for stock verification
- Triggers [line-integration](../../line-platform/CONNECTORS.md) for seller notification
