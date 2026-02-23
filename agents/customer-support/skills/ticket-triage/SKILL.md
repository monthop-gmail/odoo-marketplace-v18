---
name: ticket-triage
description: Support ticket classification and triage. Activate when working on ticket priority assignment, category taxonomy, routing rules, SLA management, or initial ticket assessment.
---

# Ticket Triage (คัดกรองตั๋วสนับสนุน)

You handle the initial classification and routing of customer support tickets to ensure fast, accurate resolution.

> If you see unfamiliar `~~category` placeholders, see [CONNECTORS.md](../../CONNECTORS.md).

## Priority Levels

| Priority | Label | SLA Response | SLA Resolution | Criteria |
|----------|-------|-------------|----------------|----------|
| P1 | Critical | 15 min | 2 hours | Payment failed, order stuck, security issue |
| P2 | High | 1 hour | 8 hours | Wrong item, delivery problem, refund request |
| P3 | Medium | 4 hours | 24 hours | Product question, account update, general complaint |
| P4 | Low | 24 hours | 72 hours | Feature request, feedback, how-to question |

## Category Taxonomy

| Category | Sub-categories |
|----------|---------------|
| Order Issues | สินค้าไม่ตรง, ไม่ได้รับสินค้า, ยกเลิกคำสั่งซื้อ, เปลี่ยนสินค้า |
| Payment | ชำระเงินไม่สำเร็จ, ขอคืนเงิน, ยอดไม่ถูกต้อง, โปรโมชั่นไม่ลด |
| Seller | สมัครผู้ขาย, ร้านค้ามีปัญหา, สินค้าไม่เหมาะสม, รายงานผู้ขาย |
| Account | เปลี่ยนข้อมูล, ลบบัญชี, เข้าสู่ระบบไม่ได้, LINE เชื่อมไม่ได้ |
| Wallet | ถอนเงินไม่สำเร็จ, ยอดไม่ตรง, ค่าคอมมิชชั่น |
| Technical | แอปค้าง, หน้าจอขาว, ไม่โหลด, LIFF error |

## Routing Rules

| Condition | Route To |
|-----------|----------|
| P1 (Critical) | Senior agent + auto-escalate to T2 |
| Payment/Refund | Finance-trained agent |
| Seller application | Admin team (officer+) |
| Wallet/Commission | Finance + Admin |
| Technical/LIFF bug | Developer escalation (T3) |
| General inquiry | Any available agent |

## Triage Decision Table

| Thai Keyword | Category | Priority | Action |
|-------------|----------|----------|--------|
| "เงินหาย", "ชำระไม่ได้" | Payment | P1 | Immediate finance review |
| "ไม่ได้รับ", "สินค้าไม่มา" | Order | P2 | Check delivery tracking |
| "ผิด", "ไม่ตรง", "สินค้าผิด" | Order | P2 | Request photo evidence |
| "คืนเงิน", "ขอเงินคืน" | Payment | P2 | Refund process |
| "สมัครขาย", "เป็นผู้ขาย" | Seller | P3 | Route to admin |
| "ถอนเงิน", "คอมมิชชั่น" | Wallet | P2 | Check wallet records |
| "ค้าง", "ไม่โหลด", "error" | Technical | P3 | Collect device + screenshot |
| "ยังไง", "ทำอย่างไร" | General | P4 | Route to FAQ/knowledge base |
| "แจ้งร้าน", "ร้านหลอก" | Seller | P2 | Flag seller for review |

## Ticket Data to Collect

| Field | Required | Source |
|-------|----------|--------|
| LINE User ID | Yes | Auto from ~~identity |
| Message text | Yes | Customer input |
| Category | Yes | Auto-classified + confirmed |
| Priority | Yes | Auto from decision table |
| Order number | If applicable | Customer provides or lookup |
| Screenshots | If technical | Customer attachment |
| Device/OS | If technical | LIFF SDK `liff.getOS()` |

## Anti-Patterns

| Don't | Do Instead |
|-------|-----------|
| Default everything to P3 | Use keyword matching for initial priority |
| Ask customer for category | Auto-classify from message content |
| Route P1 to queue | Immediate alert to available senior agent |
| Ignore repeat contacts | Check ticket history before creating new |

## Cross-References
- [response-drafting](../response-drafting/SKILL.md) — Thai response templates
- [escalation](../escalation/SKILL.md) — When to escalate
- [buyer-research](../buyer-research/SKILL.md) — Customer context lookup
- [knowledge-base](../knowledge-base/SKILL.md) — Self-service before ticket
