---
name: line-integration
description: LINE OA platform integration. Activate when working on LINE channels,
  webhook events, messaging API, rich menus, LIFF configuration, user identity mapping,
  push/reply/broadcast messages, or LINE-related notifications.
---

# S4: LINE Integration (เชื่อมต่อ LINE Platform)

You are an expert at integrating LINE OA with Odoo 18. You manage LINE channels, webhook event handling, the Messaging API (push/reply/broadcast), rich menu management, LIFF app configuration, and user identity mapping between LINE and Odoo.

> If you see unfamiliar `~~category` placeholders, see [CONNECTORS.md](../../CONNECTORS.md).

## Architecture: Single LINE OA, Multiple Roles

```
One LINE OA → all roles (buyer/seller/admin)
├── Dynamic ~~rich-menu switching based on role
├── Dynamic LIFF app routing based on liff_type
└── Auto-sync on role change via sync_member_type_from_partner()
```

| liff_type | Target | Rich Menu |
|-----------|--------|-----------|
| buyer | All users (default) | Green — ร้านค้า, ตะกร้า, คำสั่งซื้อ, โปรไฟล์ |
| seller | Approved sellers + staff | Orange — แดชบอร์ด, โพสต์สินค้า, สินค้า, กระเป๋าเงิน |
| admin | Officers + Managers | Dark blue — (pending redesign) |
| promotion | Marketing | Stub |
| support | Customer service | Stub |

## Webhook Events

| Event | Handler | Side Effect |
|-------|---------|-------------|
| `follow` | Register/link LINE user → ~~crm | Auto-create res.partner, assign buyer rich menu |
| `unfollow` | Mark user as unfollowed | Update member status |
| `message` | Route to handler | Text/image/sticker processing |
| `postback` | Handle button callbacks | Action dispatching |

## Owned Files

### Models (core_line_integration)
| File | Model | Purpose |
|------|-------|---------|
| `models/line_channel.py` | line.channel | LINE OA channel config |
| `models/line_channel_member.py` | line.channel.member | LINE user ↔ Odoo partner |
| `models/line_liff.py` | line.liff | LIFF app registration |
| `models/line_rich_menu.py` | line.rich.menu | Rich Menu management |
| `models/line_notify_log.py` | line.notify.log | Notification logging |
| `models/res_partner.py` | res.partner (ext) | LINE user ID field |
| `models/sale_order.py` | sale.order (ext) | LINE channel on orders |

### Services
| File | Class | Purpose |
|------|-------|---------|
| `services/line_api.py` | LineApiService | LINE Messaging API calls |
| `services/line_messaging.py` | LineMessagingService | Message builder & notification triggers |

### Controllers
| File | Purpose |
|------|---------|
| `controllers/webhook.py` | LINE webhook event handler |
| `controllers/api_auth.py` | LIFF token / mock authentication |
| `controllers/liff.py` | LIFF app page endpoints |

## Key Data Models

### line.channel
```python
channel_code = fields.Char()  # unique identifier
channel_id = fields.Char()     # LINE Channel ID
channel_secret = fields.Char()
channel_access_token = fields.Char()
webhook_url = fields.Char(compute)  # /api/line-buyer/webhook/<code>
liff_ids = fields.One2many('line.liff')
member_ids = fields.One2many('line.channel.member')
```

### line.channel.member
```python
channel_id = fields.Many2one('line.channel')
partner_id = fields.Many2one('res.partner')
line_user_id = fields.Char()
member_type = fields.Selection()  # buyer, seller, admin
status = fields.Selection()  # following, blocked
```

## Authentication Modes

| Mode | Headers | When to Use |
|------|---------|-------------|
| **Production** | `Authorization: Bearer <liff_token>` + `X-Channel-Code` | LIFF in LINE app |
| **Dev Mock** | `X-Line-User-Id` + `X-Channel-Code` | Local testing |

### Critical Pattern: auth='none' + SUPERUSER_ID
```python
# WRONG — env.user is empty on auth='none' routes
records = request.env['model'].sudo()  # su=True but uid empty → ensure_one() fails

# RIGHT — explicitly set uid=1
records = request.env['model'].with_user(SUPERUSER_ID)
```

## Rich Menu System

| Menu | Style | Buttons |
|------|-------|---------|
| Buyer (v19) | Green, 2500x843px | ร้านค้า, ตะกร้า, คำสั่งซื้อ, โปรไฟล์ |
| Seller (v4) | Orange, 2500x843px | แดชบอร์ด, โพสต์สินค้า, สินค้า, กระเป๋าเงิน |
| Admin | Dark blue | Pending redesign |

Auto-assign on role change: `assign_role_rich_menu()` → `LineApiService.set_user_rich_menu()`

## Notification Triggers

| Event | Recipient | Channel |
|-------|-----------|---------|
| Seller approved | Seller | ~~messaging push + email |
| Seller rejected | Seller | ~~messaging push + email |
| New order | Seller | ~~messaging push |
| Order status change | Buyer | ~~messaging push |
| Payment settled | Seller | ~~messaging push |
| Withdrawal status | Seller | ~~messaging push |

## Interfaces

| Direction | Agent | What |
|-----------|-------|------|
| ← | [seller-engine](../seller-engine/SKILL.md) | Status change → push notification |
| ← | [commerce](../commerce/SKILL.md) | New order → seller notification |
| ← | [commission-wallet](../commission-wallet/SKILL.md) | Payment/withdrawal → notification |
| ↔ | [liff-frontend](../liff-frontend/SKILL.md) | Auth, channel context, user identity |

## Anti-Patterns

| Don't | Do Instead |
|-------|-----------|
| Skip webhook signature validation | Always verify `X-Line-Signature` |
| Store `channel_secret` in logs | Use Odoo config parameters |
| Send push without `line_messaging` service | Always use `LineMessagingService` |
| Use `.sudo()` on `auth='none'` routes | Use `.with_user(SUPERUSER_ID)` |
| Forget `self.env.su` guard on `has_group()` | Add `self.env.su or not self.env.user` check |
| Exceed LINE rate limits | Push 500/min, reply within 30 sec |

## Related Commands

- [/deploy-richmenu](../../commands/deploy-richmenu.md) — Rich menu deployment
