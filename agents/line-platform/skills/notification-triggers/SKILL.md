---
name: notification-triggers
description: Event-to-notification routing and dispatch. Activate when working on
  notification mapping (event to recipient to channel), line.notify.log, email templates,
  push notification triggers, or notification preferences.
---

# Notification Triggers (ทริกเกอร์การแจ้งเตือน)

You are an expert at mapping business events to notifications in the marketplace, routing the right message to the right recipient through the right channel (LINE push, email, in-app).

> If you see unfamiliar `~~category` placeholders, see [CONNECTORS.md](../../CONNECTORS.md).

## Notification Map

| Event | Recipient | Channel | Message |
|-------|-----------|---------|---------|
| **New order** | Seller | LINE push | "คำสั่งซื้อใหม่ #SO123" + order summary |
| **Order confirmed** | Buyer | LINE push | "ยืนยันคำสั่งซื้อ #SO123 สำเร็จ" |
| **Order shipped** | Buyer | LINE push | "จัดส่งแล้ว" + tracking number |
| **Order delivered** | Buyer | LINE push | "จัดส่งสำเร็จ" |
| **Seller approved** | Seller | LINE push | "ร้านค้าได้รับอนุมัติแล้ว" + seller menu |
| **Seller rejected** | Seller | LINE push | "การสมัครไม่ผ่าน" + reason |
| **Product approved** | Seller | LINE push | "สินค้าได้รับอนุมัติ" |
| **Product rejected** | Seller | LINE push | "สินค้าไม่ผ่านการอนุมัติ" + reason |
| **Commission credited** | Seller | LINE push | "ได้รับค่าคอมมิชชัน xxx THB" |
| **Withdrawal approved** | Seller | LINE push | "คำขอถอนเงินได้รับอนุมัติ" |
| **Withdrawal completed** | Seller | LINE push | "โอนเงิน xxx THB สำเร็จ" |
| **Withdrawal rejected** | Seller | LINE push | "คำขอถอนเงินถูกปฏิเสธ" + reason |
| **New seller apply** | Admin | LINE push | "มีผู้สมัครขายใหม่" |
| **New product pending** | Admin | LINE push | "มีสินค้ารอตรวจสอบ" |
| **Welcome (follow)** | New user | LINE reply | Welcome message + buyer intro |

## Notification Audit: line.notify.log

```python
class LineNotifyLog(models.Model):
    _name = 'line.notify.log'

    channel_id = fields.Many2one('line.channel')
    member_id = fields.Many2one('line.channel.member')
    event_type = fields.Char()        # e.g., 'order_confirmed'
    message_type = fields.Selection([  # push, reply, email
        ('push', 'LINE Push'),
        ('reply', 'LINE Reply'),
        ('email', 'Email'),
    ])
    status = fields.Selection([
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('skipped', 'Skipped'),
    ])
    error_message = fields.Text()
    payload = fields.Text()           # message content (JSON)
```

## Trigger Implementation Pattern

```python
# In model write() or create() override:
def write(self, vals):
    result = super().write(vals)
    if 'state' in vals and vals['state'] == 'confirmed':
        # Find member for notification
        member = self.env['line.channel.member'].search([
            ('partner_id', '=', self.partner_id.id),
            ('is_active', '=', True)
        ], limit=1)
        if member:
            messaging = LineMessagingService(channel)
            messaging.send_order_confirmation(self, member)
    return result
```

## Channel Priority

1. **LINE Push** (primary) -- immediate, mobile-friendly
2. **Email** (fallback) -- when LINE member not found or inactive
3. **In-app** (future) -- Odoo backend notifications

## Owned Files

| File | Purpose |
|------|---------|
| `core_line_integration/models/line_notify_log.py` | Notification audit log model |
| `core_line_integration/services/line_messaging.py` | Business-level notification dispatch |
| `core_line_integration/data/mail_template_data.xml` | Email templates (fallback) |

## Anti-Patterns

| Don't | Do Instead |
|-------|-----------|
| Send notifications to inactive members | Check `is_active` before sending |
| Skip notification logging | Always create `line.notify.log` record |
| Use push when reply token available | Prefer reply (free) over push (quota) |
| Send raw data in notifications | Use localized Thai messages with THB formatting |
| Notify without checking quota | Monitor LINE messaging quota usage |

## Cross-References

| Direction | Skill | Interaction |
|-----------|-------|-------------|
| → | [messaging-api](../messaging-api/SKILL.md) | Dispatch via LineMessagingService |
| ← | [order-processing](../../../commerce/skills/order-processing/SKILL.md) | Order events → notifications |
| ← | [delivery-tracking](../../../commerce/skills/delivery-tracking/SKILL.md) | Delivery events → notifications |
| ← | [withdrawal-processing](../../../finance/skills/withdrawal-processing/SKILL.md) | Withdrawal state → notifications |
| ← | [seller-lifecycle](../../../seller-engine/skills/seller-lifecycle/SKILL.md) | Approval/rejection → notifications |
| ← | [product-lifecycle](../../../commerce/skills/product-lifecycle/SKILL.md) | Product moderation → notifications |
| ← | [webhook-handling](../webhook-handling/SKILL.md) | Follow event → welcome message |
