---
name: knowledge-base
description: Customer support FAQ and knowledge base. Activate when working on FAQ content, self-service flows, help articles, common question answers, or knowledge base structure.
---

# Knowledge Base (ฐานความรู้)

You maintain the self-service knowledge base that helps buyers and sellers find answers without contacting support.

> If you see unfamiliar `~~category` placeholders, see [CONNECTORS.md](../../CONNECTORS.md).

## Article Categories

| Category | Audience | Topics |
|----------|----------|--------|
| การซื้อสินค้า (Buying) | Buyers | Browse, cart, checkout, payment |
| การขายสินค้า (Selling) | Sellers | Apply, post products, manage orders |
| การชำระเงิน (Payment) | All | Payment methods, refunds, invoices |
| บัญชีผู้ใช้ (Account) | All | Profile, LINE connection, settings |
| เทคนิค (Technical) | All | App issues, device compatibility |
| กระเป๋าเงิน (Wallet) | Sellers | Balance, withdrawal, commission |

## Article Structure

Every knowledge base article follows this format:

```markdown
# {Question Title in Thai}

## คำตอบสั้น
{1-2 sentence answer}

## วิธีทำ (Step-by-step)
1. {Step 1 with screenshot reference}
2. {Step 2}
3. {Step 3}

## หมายเหตุ
- {Important note or exception}

## ยังมีคำถาม?
แจ้งเราผ่าน LINE OA ได้เลยค่ะ
```

## Top FAQs (Thai)

### การซื้อสินค้า
| Question | Short Answer |
|----------|-------------|
| สั่งซื้อสินค้าอย่างไร? | เลือกสินค้า → หยิบใส่ตะกร้า → สั่งซื้อ |
| ยกเลิกคำสั่งซื้อได้ไหม? | ยกเลิกได้ก่อนจัดส่ง แจ้งผ่าน LINE |
| ติดตามพัสดุอย่างไร? | ดูที่หน้าคำสั่งซื้อ → เลขพัสดุ |
| คืนสินค้าอย่างไร? | แจ้งภายใน 7 วัน พร้อมรูปถ่าย |

### การขายสินค้า
| Question | Short Answer |
|----------|-------------|
| สมัครเป็นผู้ขายอย่างไร? | โปรไฟล์ → สมัครผู้ขาย → กรอกข้อมูล → รออนุมัติ |
| โพสต์สินค้าอย่างไร? | เมนูผู้ขาย → โพสต์สินค้า → ถ่ายรูป → กรอกราคา |
| ให้คนอื่นช่วยโพสต์ได้ไหม? | ได้ค่ะ เพิ่มผู้ช่วย (Staff) ในการตั้งค่าร้าน |
| ค่าคอมมิชชั่นเท่าไหร่? | ตามอัตราที่ตั้งไว้ ดูได้ที่แดชบอร์ด |

### การชำระเงิน
| Question | Short Answer |
|----------|-------------|
| ชำระเงินช่องทางไหนได้บ้าง? | โอนเงิน, บัตรเครดิต (ตามที่เปิดให้) |
| ขอคืนเงินใช้เวลากี่วัน? | 3-7 วันทำการหลังอนุมัติ |
| ถอนเงินขั้นต่ำเท่าไหร่? | ตามที่กำหนดในระบบ (ดูที่กระเป๋าเงิน) |

### บัญชีผู้ใช้
| Question | Short Answer |
|----------|-------------|
| แก้ไขโปรไฟล์อย่างไร? | เมนูโปรไฟล์ → แก้ไข → บันทึก |
| เชื่อม LINE ไม่ได้? | ปิด LINE แล้วเปิดใหม่ → เข้าแอปอีกครั้ง |

## Self-Service Flows

Before creating a ticket, guide users through self-service:

```
User sends message
    ↓
Keyword match to FAQ?
    ├─ Yes → Send FAQ answer + "ช่วยตอบคำถามได้ไหมคะ?"
    │         ├─ "ได้" → Close (resolved)
    │         └─ "ไม่ได้" → Create ticket
    └─ No → Create ticket
```

## Knowledge Base Maintenance

| Task | Frequency | Owner |
|------|-----------|-------|
| Review article accuracy | Monthly | Support lead |
| Add new FAQs from tickets | Weekly | Support agents |
| Update screenshots | On UI changes | Dev + Support |
| Analyze search queries | Monthly | Support lead |
| Archive outdated articles | Quarterly | Support lead |

## Anti-Patterns

| Don't | Do Instead |
|-------|-----------|
| Write articles in English | Thai only for customer-facing content |
| Use technical jargon | Plain Thai anyone can understand |
| Skip step-by-step instructions | Always include numbered steps |
| Let articles go stale | Review monthly, update on changes |
| Force users to read long articles | Short answer first, details below |

## Cross-References
- [ticket-triage](../ticket-triage/SKILL.md) — Deflect to FAQ before ticket creation
- [response-drafting](../response-drafting/SKILL.md) — Link FAQ in response messages
- [buyer-research](../buyer-research/SKILL.md) — Understand what customers ask about
