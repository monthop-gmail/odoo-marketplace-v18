# /draft-response

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).

Draft a Thai support response following the brand voice and Acknowledge-Empathize-Solve-Follow-up structure.

## Usage

```
/draft-response <context>
/draft-response "ลูกค้าถามเรื่องสถานะคำสั่งซื้อ SO-1234"
/draft-response --template refund
/draft-response --tone formal
```

## How It Works

```
┌─────────────────────────────────────────────────────┐
│                 DRAFT RESPONSE                       │
├─────────────────────────────────────────────────────┤
│  STANDALONE (always works)                           │
│  ✓ Generate Thai response from context description   │
│  ✓ Follow AESF structure                             │
│  ✓ Match brand voice (friendly, professional)        │
│  ✓ Suggest template selection                        │
├─────────────────────────────────────────────────────┤
│  SUPERCHARGED (when ~~crm + ~~api connected)         │
│  + Pull real customer and order data                 │
│  + Personalize with customer name and order details  │
│  + Include actual tracking/status information        │
│  + Auto-send via ~~messaging (LINE push)             │
└─────────────────────────────────────────────────────┘
```

## Response Structure (AESF)

| Step | Thai Label | Purpose |
|------|-----------|---------|
| **Acknowledge** | รับทราบ | ขอบคุณที่แจ้ง / ได้รับข้อความแล้ว |
| **Empathize** | เข้าใจ | เข้าใจความไม่สะดวก / ขออภัย |
| **Solve** | แก้ไข | อธิบายสิ่งที่ทำ/จะทำ ให้ชัดเจน |
| **Follow-up** | ติดตาม | แจ้งขั้นตอนถัดไป / ช่องทางติดต่อ |

## Brand Voice Guidelines

| Do | Don't |
|----|-------|
| ใช้ครับ/ค่ะ ท้ายประโยค | ใช้ภาษาทางการเกินไป |
| เรียกชื่อลูกค้า | ใช้คำว่า "ท่าน" ซ้ำ |
| ให้ข้อมูลชัดเจน ตรงประเด็น | ตอบยาวเกินไป |
| แสดงความใส่ใจ | ใช้ข้อความ copy-paste ชัดเจน |

## Common Templates

| Template | Use Case |
|----------|----------|
| `order-status` | สอบถามสถานะคำสั่งซื้อ |
| `refund` | ขอคืนเงิน/คืนสินค้า |
| `shipping-delay` | จัดส่งล่าช้า |
| `wrong-item` | ได้รับสินค้าผิด |
| `payment-failed` | ชำระเงินไม่สำเร็จ |
| `seller-complaint` | ร้องเรียนผู้ขาย |

## Output

```markdown
## Draft Response

**Customer:** [name]
**Issue:** [category]
**Tone:** [friendly/formal/apologetic]

### Message (Thai)
---
สวัสดีค่ะ คุณ[ชื่อ]

[Acknowledge] ได้รับข้อความเรื่อง [issue] เรียบร้อยแล้วค่ะ

[Empathize] เข้าใจความไม่สะดวก [empathy statement]

[Solve] ดิฉันได้ดำเนินการ [action] เรียบร้อยแล้วค่ะ [details]

[Follow-up] หากมีข้อสงสัยเพิ่มเติม สามารถแจ้งผ่าน LINE ได้เลยค่ะ

ขอบคุณค่ะ
---
```

## Next Steps

- Want me to send this via LINE push message?
- Should I adjust the tone or add more details?
- Want to save this as a new template?

## Related Skills

- Uses [customer-support](../skills/) for response templates and brand voice
- Triggers [line-integration](../../line-platform/skills/) for message delivery
