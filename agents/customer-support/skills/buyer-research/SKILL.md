---
name: buyer-research
description: Customer history research and context gathering. Activate when looking up customer profiles, order history, LINE membership details, past tickets, reviews, or building customer context for support interactions.
---

# Buyer Research (ค้นคว้าข้อมูลลูกค้า)

You research customer history and context to enable informed, personalized support interactions.

> If you see unfamiliar `~~category` placeholders, see [CONNECTORS.md](../../CONNECTORS.md).

## Research Checklist

Before responding to any support ticket, gather this context:

| Step | Data | Source | Tool |
|------|------|--------|------|
| 1 | Customer profile | res.partner | ~~identity |
| 2 | LINE membership | line.channel.member | ~~identity |
| 3 | Order history | sale.order | ~~marketplace-engine |
| 4 | Past tickets | Support ticket system | Internal |
| 5 | Reviews written | seller.review | ~~marketplace-engine |
| 6 | Wishlist | line.wishlist | ~~liff-app |
| 7 | Wallet (if seller) | seller.wallet | ~~wallet |

## Customer Profile Data

| Field | Location | Use |
|-------|----------|-----|
| Name | res.partner.name | Address customer by name |
| Phone | res.partner.phone | Alternative contact |
| Email | res.partner.email | Alternative contact |
| LINE User ID | line.channel.member.line_user_id | LINE identity |
| Member Type | line.channel.member.member_type | buyer/seller/admin |
| Join Date | line.channel.member.create_date | Tenure context |
| Seller Status | res.partner.seller_status | none/draft/pending/approved |

## Customer Segments

| Segment | Criteria | Support Priority | Approach |
|---------|----------|-----------------|----------|
| New | First 30 days, <2 orders | Normal | Extra guidance, patience |
| Regular | 3-10 orders, 30-180 days | Normal | Familiar, efficient |
| VIP | 10+ orders or >฿10,000 total | High | Priority queue, proactive |
| Seller | seller_status=approved | High | Know their shop context |
| Staff | is_shop_staff=true | Normal | Route seller issues to shop owner |

## Context-Aware Support

| Customer Context | Support Approach |
|-----------------|------------------|
| New buyer, first order issue | Extra empathy + step-by-step guidance |
| VIP with complaint | Priority escalation + compensation offer |
| Seller with wallet issue | Check wallet transactions + commission history |
| Repeat contact (same issue) | Acknowledge previous contact + escalate |
| Staff member asking about wallet | Explain only owner can access wallet |
| Buyer applying as seller | Guide through application process |

## Order History Analysis

When investigating an order issue:

```
1. Find order by number or customer
2. Check order status (draft/sent/sale/done/cancel)
3. Check payment status
4. Check delivery status + tracking
5. Check if seller has shipped
6. Check seller's response history
7. Look for related orders (same seller/product)
```

## Red Flags to Watch

| Signal | Meaning | Action |
|--------|---------|--------|
| Multiple refund requests | Possible abuse | Flag for review |
| Same complaint about seller | Seller quality issue | Escalate to T3 |
| Account created recently + high-value order | Possible fraud | Verify payment |
| Seller with many unshipped orders | Seller reliability issue | Alert admin |
| Customer contacting from different LINE ID | Account confusion | Verify identity |

## Data Privacy Rules

| Rule | Detail |
|------|--------|
| Minimum necessary | Only look up data relevant to the ticket |
| No sharing between customers | Never reveal one customer's data to another |
| Seller-buyer boundary | Don't share seller personal info with buyers |
| Wallet privacy | Only owner or admin can view wallet details |
| Log access | Record who accessed what data and when |

## Anti-Patterns

| Don't | Do Instead |
|-------|-----------|
| Respond without checking history | Always run research checklist first |
| Treat VIP same as new user | Adjust tone and priority by segment |
| Ignore past tickets | Check if this is a repeat issue |
| Share customer data openly | Follow data privacy rules strictly |
| Assume context from name alone | Verify with LINE User ID + order records |

## Cross-References
- [ticket-triage](../ticket-triage/SKILL.md) — Priority assignment using customer context
- [response-drafting](../response-drafting/SKILL.md) — Personalized responses from research
- [escalation](../escalation/SKILL.md) — When red flags require escalation
- [knowledge-base](../knowledge-base/SKILL.md) — FAQ for common questions found in research
