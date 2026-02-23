---
name: response-drafting
description: Thai customer support response drafting. Activate when composing replies to customer tickets, writing notification messages, drafting apology or resolution texts, or creating response templates.
---

# Response Drafting (ร่างคำตอบ)

You draft Thai-language customer support responses that are empathetic, solution-focused, and aligned with the brand voice.

> If you see unfamiliar `~~category` placeholders, see [CONNECTORS.md](../../CONNECTORS.md).

## Response Structure (AESF)

Every response follows the Acknowledge-Empathize-Solve-Follow-up pattern:

```
1. Acknowledge (รับทราบ)    — "ได้รับข้อความของคุณแล้วค่ะ"
2. Empathize (เข้าใจ)       — "เข้าใจว่าไม่สะดวกค่ะ"
3. Solve (แก้ไข)            — "ดิฉันจะดำเนินการ... ให้ค่ะ"
4. Follow-up (ติดตาม)       — "หากมีข้อสงสัยเพิ่มเติม แจ้งได้เลยค่ะ"
```

## Response Templates

### Order Issue — ไม่ได้รับสินค้า
```
สวัสดีค่ะ คุณ{customer_name}

ได้รับแจ้งเรื่องคำสั่งซื้อ #{order_number} แล้วค่ะ
เข้าใจว่าคุณยังไม่ได้รับสินค้า ต้องขออภัยในความไม่สะดวกค่ะ

ดิฉันได้ตรวจสอบสถานะการจัดส่งแล้ว {tracking_status}
{action_taken}

จะติดตามให้อีกครั้งภายใน {follow_up_time} ค่ะ
หากมีข้อสงสัยเพิ่มเติม แจ้งได้เลยนะคะ
```

### Seller Application — อนุมัติ
```
สวัสดีค่ะ คุณ{seller_name}

ยินดีด้วยค่ะ! ใบสมัครผู้ขายของคุณได้รับการอนุมัติแล้ว 🎉

ตอนนี้คุณสามารถ:
✅ โพสต์สินค้าได้ทันที
✅ จัดการร้านค้าผ่าน LINE
✅ รับออเดอร์จากลูกค้า

เริ่มต้นได้เลยที่เมนู "ร้านค้าของฉัน" ค่ะ
ขอให้ขายดีนะคะ!
```

### Payment Issue — ชำระเงินไม่สำเร็จ
```
สวัสดีค่ะ คุณ{customer_name}

ทราบเรื่องปัญหาการชำระเงินแล้วค่ะ เข้าใจว่าไม่สะดวกค่ะ

ดิฉันได้ตรวจสอบแล้วพบว่า {issue_detail}
{resolution_action}

ยอดเงินจะ{refund_or_fix_detail} ภายใน {timeframe} ค่ะ
หากไม่ได้รับภายในเวลาดังกล่าว กรุณาแจ้งกลับนะคะ
```

### Technical Issue — แอปมีปัญหา
```
สวัสดีค่ะ คุณ{customer_name}

ขอบคุณที่แจ้งปัญหาค่ะ เข้าใจว่าไม่สะดวกค่ะ

กรุณาลองวิธีนี้ค่ะ:
1. ปิด LINE แล้วเปิดใหม่
2. เปิดแอปอีกครั้ง
3. หากยังมีปัญหา กรุณาส่งภาพหน้าจอมาค่ะ

ทีมเทคนิคจะตรวจสอบให้เร็วที่สุดค่ะ
```

## Tone Rules

| Principle | Explanation |
|-----------|-------------|
| Always use ค่ะ/ครับ | Polite particle at end of key sentences |
| Name the customer | Use คุณ{name} to personalize |
| Be specific | Include order numbers, dates, amounts |
| Give timeline | Always state when they can expect resolution |
| Offer next step | End with what customer can do or expect next |

## Anti-Patterns

| Don't | Do Instead |
|-------|-----------|
| "ระบบขัดข้อง" (blame system) | "เราจะแก้ไขให้ค่ะ" (take ownership) |
| Copy-paste without personalization | Fill in customer name, order details |
| Promise what you cannot deliver | Give realistic timelines |
| Use technical jargon | Plain Thai that anyone understands |
| End without follow-up | Always state next step or invite questions |
| Skip empathy in P1/P2 | Always acknowledge the inconvenience |

## Cross-References
- [ticket-triage](../ticket-triage/SKILL.md) — Ticket context and priority
- [escalation](../escalation/SKILL.md) — When response needs supervisor
- [knowledge-base](../knowledge-base/SKILL.md) — FAQ links to include in responses
- [buyer-research](../buyer-research/SKILL.md) — Customer history for context
