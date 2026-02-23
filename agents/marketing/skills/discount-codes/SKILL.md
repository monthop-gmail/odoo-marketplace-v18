---
name: discount-codes
description: Discount codes and coupon system. Activate when working on coupon creation, discount types, promo code validation, redemption rules, or coupon-based promotions.
---

# Discount Codes (รหัสส่วนลด)

You manage the coupon and discount code system that drives promotional offers across the marketplace.

> If you see unfamiliar `~~category` placeholders, see [CONNECTORS.md](../../CONNECTORS.md).

## Discount Types

| Type | Description | Example |
|------|-------------|---------|
| Percentage | % off order subtotal | 10% off |
| Fixed Amount | Baht off order subtotal | ฿100 off |
| Free Shipping | Waive delivery fee | Free delivery |
| Bundle | Buy X get Y discount | Buy 3 get 10% off |

## Future Model: `marketplace.coupon`

| Field | Type | Description |
|-------|------|-------------|
| name | Char | Internal coupon name |
| code | Char | Promo code (uppercase, unique) |
| discount_type | Selection | percentage/fixed/free_shipping/bundle |
| discount_value | Float | Percentage or fixed amount |
| min_order_amount | Float | Minimum order to qualify |
| max_discount_amount | Float | Cap on percentage discounts |
| usage_limit | Integer | Total redemptions allowed |
| usage_per_user | Integer | Redemptions per buyer |
| used_count | Integer | Current redemption count |
| valid_from | Datetime | Start of validity |
| valid_to | Datetime | End of validity |
| seller_id | Many2one | Seller-specific coupon (optional) |
| category_ids | Many2many | Restrict to product categories |
| product_ids | Many2many | Restrict to specific products |
| is_active | Boolean | Enabled/disabled toggle |

## Validation Rules

When a buyer applies a coupon code at checkout:

```
1. Code exists and is_active=True
2. Current time between valid_from and valid_to
3. used_count < usage_limit
4. Buyer's usage < usage_per_user
5. Order subtotal >= min_order_amount
6. If seller-specific: order contains that seller's products
7. If category-restricted: order has matching category products
8. If product-restricted: order has matching products
```

All checks must pass. Return first failing reason to buyer.

## Coupon Sources

| Source | Who Creates | Scope |
|--------|-------------|-------|
| Platform coupon | Admin/Marketing | All products |
| Seller coupon | Approved seller | Own products only |
| Campaign coupon | Campaign system | Campaign-linked products |
| Referral coupon | Auto-generated | New buyer welcome |

## Redemption Flow
1. Buyer enters code in checkout page
2. API validates code against all rules
3. If valid: show discount preview on order total
4. On place order: apply discount, increment used_count
5. Record coupon_id on sale.order for tracking

## Anti-Patterns

| Don't | Do Instead |
|-------|-----------|
| Allow unlimited percentage discount | Always set max_discount_amount cap |
| Let expired coupons validate | Check valid_to server-side, not just UI |
| Skip concurrency on usage_limit | Atomic increment with SQL WHERE check |
| Allow stacking without rules | Define clear stacking policy (max 1 coupon) |

## Cross-References
- [campaign-management](../campaign-management/SKILL.md) — Campaign-linked coupons
- [featured-products](../featured-products/SKILL.md) — Boost + coupon combos
- [content-strategy](../content-strategy/SKILL.md) — Coupon promotion content
