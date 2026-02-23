# /research-buyer

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).

Research a customer's full history — profile, orders, LINE activity, and segment classification.

## Usage

```
/research-buyer <name_or_id>
/research-buyer "Jacks Sparrow"
/research-buyer --partner 46
/research-buyer --line Ud6c41147b7c7d919baf065ca5c7f5d95
```

## How It Works

```
┌─────────────────────────────────────────────────────┐
│                 RESEARCH BUYER                       │
├─────────────────────────────────────────────────────┤
│  STANDALONE (always works)                           │
│  ✓ Define research scope and data points needed      │
│  ✓ Classify segment from provided data               │
│  ✓ Generate customer summary template                │
├─────────────────────────────────────────────────────┤
│  SUPERCHARGED (when ~~crm + ~~marketplace-engine)    │
│  + Pull res.partner profile from Odoo                │
│  + Query sale.order history via ~~api                │
│  + Look up line.channel.member for LINE activity     │
│  + Check line.wishlist and line.compare items        │
│  + Calculate lifetime value and segment              │
└─────────────────────────────────────────────────────┘
```

## Customer Segments

| Segment | Criteria | Lifetime Value |
|---------|----------|---------------|
| **New** | 0 orders, registered < 30 days | ฿0 |
| **Regular** | 1-5 orders, active last 90 days | ฿1 — ฿4,999 |
| **VIP** | 6+ orders or LTV > ฿5,000 | ฿5,000+ |
| **At-Risk** | No order in 60+ days, was Regular/VIP | Declining |
| **Churned** | No activity in 120+ days | Inactive |

## Data Points

| Source | Model | Fields |
|--------|-------|--------|
| Profile | `res.partner` | name, email, phone, address, seller_status |
| Orders | `sale.order` | order count, total spend, last order date |
| LINE | `line.channel.member` | line_user_id, member_type, follow date |
| Wishlist | `line.wishlist` | saved products count |
| Compare | `line.compare` | compared products count |

## Output

```markdown
## Customer Research

**Name:** [name]
**Partner ID:** [id]
**Segment:** [New/Regular/VIP/At-Risk/Churned]

### Profile
| Field | Value |
|-------|-------|
| Email | [email] |
| Phone | [phone] |
| Address | [address] |
| Registered | [date] |
| Seller Status | [none/draft/pending/approved] |

### Order History
| Order | Date | Items | Total | Status |
|-------|------|-------|-------|--------|
| SO-[id] | [date] | [count] | ฿[amount] | [status] |

**Total Orders:** [n] | **Lifetime Value:** ฿[amount]

### LINE Activity
| Field | Value |
|-------|-------|
| LINE User ID | [id] |
| Member Type | [buyer/seller/admin] |
| Rich Menu | [assigned menu] |
| Wishlist Items | [count] |
| Compare Items | [count] |
```

## Next Steps

- Want me to check this customer's open support tickets?
- Should I send a personalized message to this customer?
- Want to see their full order details?

## Related Skills

- Uses [customer-support](../skills/) for segment classification
- Cross-references [commerce](../../commerce/skills/) for order data
- Cross-references [line-integration](../../line-platform/skills/) for LINE profile
