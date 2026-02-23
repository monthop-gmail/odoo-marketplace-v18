---
name: channel-management
description: LINE channel configuration and multi-role architecture. Activate when
  working on line.channel model, LINE OA setup, channel credentials, single LINE OA
  with multiple roles, or LIFF app registration.
---

# Channel Management (การจัดการช่องทาง LINE)

You are an expert at managing LINE Official Account channels and their integration with the Odoo marketplace, including the single-channel multi-role architecture.

> If you see unfamiliar `~~category` placeholders, see [CONNECTORS.md](../../CONNECTORS.md).

## Single LINE OA, Multiple Roles

Core architecture: **One LINE OA serves all roles** (buyer/seller/admin) with dynamic experience switching.

```
LINE Official Account
    ├── Buyer experience (default)
    │     └── LIFF: liff/ (buyer app)
    ├── Seller experience (approved sellers)
    │     └── LIFF: liff_seller/ (seller app)
    └── Admin experience (officers/managers)
          └── LIFF: liff_admin/ (admin app)
```

Role determined by `line.channel.member.member_type` + corresponding rich menu.

## Key Model: line.channel

```python
class LineChannel(models.Model):
    _name = 'line.channel'

    name = fields.Char()
    channel_code = fields.Char(unique=True)   # used in API URLs
    channel_id = fields.Char()                # LINE channel ID
    channel_secret = fields.Char()            # LINE channel secret
    channel_access_token = fields.Char()      # LINE long-lived token
    liff_ids = fields.One2many('line.liff')   # registered LIFF apps
    webhook_url = fields.Char(compute=True)   # /api/line-buyer/webhook/<code>
    is_active = fields.Boolean(default=True)
```

## LIFF App Registration: line.liff

```python
class LineLiff(models.Model):
    _name = 'line.liff'

    channel_id = fields.Many2one('line.channel')
    liff_id = fields.Char()          # LINE LIFF ID
    liff_type = fields.Selection([
        ('general', 'General'),
        ('buyer', 'Buyer'),
        ('seller', 'Seller'),
        ('admin', 'Admin'),
        ('promotion', 'Promotion'),
        ('support', 'Support'),
    ])
    liff_url = fields.Char()         # LIFF app URL
```

## Channel Setup Checklist

1. Create `line.channel` record with credentials
2. Register LIFF apps (buyer, seller, admin) in LINE Developers Console
3. Map LIFF IDs to `line.liff` records with correct `liff_type`
4. Configure webhook URL in LINE Developers Console
5. Create rich menus (buyer/seller/admin) with LIFF URLs

## Owned Files

| File | Purpose |
|------|---------|
| `core_line_integration/models/line_channel.py` | Channel model |
| `core_line_integration/models/line_liff.py` | LIFF registration model |
| `core_line_integration/views/line_channel_view.xml` | Channel management views |
| `core_line_integration/views/line_liff_view.xml` | LIFF app configuration views |

## Anti-Patterns

| Don't | Do Instead |
|-------|-----------|
| Store channel secret in plain text logs | Keep credentials in database only |
| Create multiple channels for different roles | Single channel, role-based experience |
| Hard-code channel credentials | Use `line.channel` model records |
| Skip webhook URL configuration | Always set webhook after channel creation |

## Cross-References

| Direction | Skill | Interaction |
|-----------|-------|-------------|
| → | [webhook-handling](../webhook-handling/SKILL.md) | Channel receives webhook events |
| → | [rich-menu-system](../rich-menu-system/SKILL.md) | Channel-level rich menu assignment |
| → | [user-identity](../user-identity/SKILL.md) | Channel members (line.channel.member) |
| → | [messaging-api](../messaging-api/SKILL.md) | Channel token used for API calls |
