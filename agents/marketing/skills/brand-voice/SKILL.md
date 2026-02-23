---
name: brand-voice
description: Thai copywriting and brand voice guidelines. Activate when working on Thai text for notifications, product descriptions, error messages, promotional copy, welcome messages, or any user-facing Thai content.
---

# Brand Voice (น้ำเสียงแบรนด์)

You maintain the Thai copywriting and brand voice guidelines for all user-facing text across the marketplace platform.

> If you see unfamiliar `~~category` placeholders, see [CONNECTORS.md](../../CONNECTORS.md).

## Core Brand Personality
- **Friendly** (เป็นกันเอง) — like a helpful friend, not a corporation
- **Trustworthy** (น่าเชื่อถือ) — clear, honest, no exaggeration
- **Encouraging** (ให้กำลังใจ) — supportive of sellers and buyers
- **Modern** (ทันสมัย) — current language, not overly formal

## Tone Guidelines by Context

| Context | Tone | Polite Particle | Example |
|---------|------|-----------------|---------|
| Welcome | Warm, inviting | ค่ะ/ครับ | "ยินดีต้อนรับสู่ร้านค้าของเรานะคะ" |
| Product | Informative, honest | Optional | "กระเป๋าหนังแท้ ทนทาน ใช้ได้นาน" |
| Error | Calm, solution-focused | ค่ะ/ครับ | "ขออภัยค่ะ ไม่สามารถดำเนินการได้ กรุณาลองใหม่อีกครั้ง" |
| Promo | Exciting but not pushy | Optional | "โปรพิเศษ! ลด 20% เฉพาะวันนี้" |
| Support | Empathetic, professional | ค่ะ/ครับ | "เข้าใจค่ะ เราจะช่วยแก้ไขให้เร็วที่สุด" |
| Success | Celebratory, brief | ค่ะ/ครับ | "สั่งซื้อสำเร็จแล้วค่ะ ขอบคุณที่ไว้วางใจ" |
| Notification | Concise, actionable | ค่ะ/ครับ | "คำสั่งซื้อ #1234 จัดส่งแล้วค่ะ" |

## Writing Rules

### Do
- Use natural spoken Thai, not textbook formal
- Keep sentences short (max 2 clauses)
- Lead with the most important information
- Use numerals for numbers (not Thai numerals unless decorative)
- End messages with polite particles (ค่ะ/ครับ) for notifications and support
- Use emoji sparingly and only in casual contexts (LINE messages, not error dialogs)

### Don't
- Use English words when Thai equivalents exist (ยกเลิก not Cancel)
- Use aggressive sales language ("ด่วน! ซื้อเดี๋ยวนี้เลย!!!")
- Use ราชาศัพท์ (royal language) — too formal
- Mix formal and informal registers in one message
- Use negative framing ("คุณจะพลาด!" → "โอกาสดีรออยู่")

## Template Patterns

### Order Notification
```
[Status Icon] คำสั่งซื้อ #{order_number}
{status_message}
{detail_if_applicable}
```

### Seller Application
```
Welcome: "ยินดีต้อนรับผู้ขายใหม่ค่ะ กรุณากรอกข้อมูลเพื่อสมัครเป็นผู้ขาย"
Approved: "ยินดีด้วยค่ะ! ร้านค้าของคุณได้รับการอนุมัติแล้ว เริ่มโพสต์สินค้าได้เลย"
Rejected: "ขออภัยค่ะ ใบสมัครยังไม่ผ่านการอนุมัติ เหตุผล: {reason}"
```

### Error Messages
```
Generic: "เกิดข้อผิดพลาดค่ะ กรุณาลองใหม่อีกครั้ง"
Not Found: "ไม่พบข้อมูลที่ต้องการค่ะ"
Validation: "กรุณากรอก{field_name}ค่ะ"
Network: "ไม่สามารถเชื่อมต่อได้ค่ะ กรุณาตรวจสอบสัญญาณ"
```

## Do / Don't Table

| Don't | Do Instead |
|-------|-----------|
| "ERROR: Invalid input" | "กรุณากรอกข้อมูลให้ถูกต้องค่ะ" |
| "Your order has been placed" | "สั่งซื้อสำเร็จแล้วค่ะ" |
| "ด่วนมาก!! ซื้อเลย!!!" | "โปรพิเศษวันนี้ ลดราคา 20%" |
| "ระบบไม่สามารถประมวลผลคำร้องขอของท่านได้" | "ขออภัยค่ะ ไม่สามารถดำเนินการได้" |
| Mixed: "Order ของคุณ complete แล้ว" | Pure Thai: "คำสั่งซื้อเสร็จสมบูรณ์แล้วค่ะ" |

## Cross-References
- [content-strategy](../content-strategy/SKILL.md) — Content planning and 80/20 rule
- [social-media](../social-media/SKILL.md) — Platform-specific copywriting
- [campaign-management](../campaign-management/SKILL.md) — Campaign messaging
