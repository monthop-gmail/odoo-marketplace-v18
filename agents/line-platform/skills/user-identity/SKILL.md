---
name: user-identity
description: LINE-Odoo user identity mapping and authentication. Activate when working
  on line.channel.member, user registration, role synchronization, auth modes
  (LIFF token/dev mock), or the critical auth='none'+SUPERUSER_ID pattern.
---

# User Identity (ระบบตัวตนผู้ใช้)

You are an expert at managing user identity mapping between LINE and Odoo in the marketplace, handling member registration, role synchronization, authentication flows, and the critical SUPERUSER_ID pattern.

> If you see unfamiliar `~~category` placeholders, see [CONNECTORS.md](../../CONNECTORS.md).

## Identity Architecture

```
LINE User (userId)
    ↕ linked via
line.channel.member
    ↕ linked via
res.partner (Odoo contact)
    ↕ linked via
res.users (Odoo user, optional)
```

## Key Model: line.channel.member

```python
class LineChannelMember(models.Model):
    _name = 'line.channel.member'

    channel_id = fields.Many2one('line.channel')
    line_user_id = fields.Char(index=True)     # LINE userId
    partner_id = fields.Many2one('res.partner') # linked Odoo contact
    display_name = fields.Char()
    picture_url = fields.Char()
    member_type = fields.Selection([
        ('buyer', 'Buyer'),
        ('seller', 'Seller'),
        ('admin', 'Admin'),
    ], default='buyer')
    is_active = fields.Boolean(default=True)
```

## Registration Flow

```
LINE Follow → webhook → fetch profile → create line.channel.member
    ↓
Create res.partner (if not exists)
    ↓
Link member.partner_id = partner
    ↓
member_type = 'buyer' (default)
    ↓
Assign buyer rich menu
```

## Role Sync: sync_member_type_from_partner()

When `res.partner` seller status changes:

```python
def sync_member_type_from_partner(self):
    partner = self.partner_id
    if partner.is_marketplace_officer or partner.is_marketplace_manager:
        self.member_type = 'admin'
    elif partner.seller_status == 'approved':
        self.member_type = 'seller'
    else:
        self.member_type = 'buyer'
    # Then reassign rich menu
    self.assign_role_rich_menu()
```

## Authentication Modes

| Mode | Header | Resolution | Use Case |
|------|--------|------------|----------|
| **LIFF Token** | `Authorization: Bearer <token>` | Validate with LINE API → userId | Production |
| **Dev Mock** | `X-Line-User-Id: <userId>` | Direct lookup | Development/testing |
| **Channel Code** | `X-Channel-Code: <code>` | Resolve line.channel | Both modes |

## Critical Pattern: auth='none' + SUPERUSER_ID

When using `auth='none'` routes (all LIFF API endpoints):

```python
# PROBLEM: request.env.user is EMPTY recordset
# .sudo() sets su=True but does NOT set uid -> env.user still empty -> ensure_one() fails

# WRONG:
env = request.env['model'].sudo()  # uid still empty!

# RIGHT:
from odoo import SUPERUSER_ID
env = request.env['model'].with_user(SUPERUSER_ID)  # uid=1, safe
```

This affects all inherited `write()` methods that call `self.env.user.has_group()`.
Guard pattern: `if self.env.su or not self.env.user:` to bypass group checks.

## @require_auth Decorator

```python
def require_auth(func):
    """Resolves LINE userId -> member -> partner, sets request attributes"""
    # Sets: request.line_member, request.partner, request.seller_partner
    # For staff: seller_partner = shop owner's partner (context switch)
```

## Owned Files

| File | Purpose |
|------|---------|
| `core_line_integration/models/line_channel_member.py` | Member model + sync + role assignment |
| `core_line_integration/controllers/api_auth.py` | Auth helpers, @require_auth decorator |
| `core_line_integration/services/line_api.py` | get_profile() for registration |
| `core_marketplace/models/res_partner.py` | Partner write() → trigger member sync |

## Anti-Patterns

| Don't | Do Instead |
|-------|-----------|
| Use `.sudo()` in auth='none' routes | Use `.with_user(SUPERUSER_ID)` |
| Call `env.user.has_group()` without guard | Check `self.env.su or not self.env.user` first |
| Create duplicate members for same userId | Search existing, reactivate if needed |
| Store LINE tokens in database | Tokens are transient, validate per-request |
| Skip member deactivation on unfollow | Set `is_active=False` to stop messaging |

## Cross-References

| Direction | Skill | Interaction |
|-----------|-------|-------------|
| ← | [webhook-handling](../webhook-handling/SKILL.md) | Follow event → member registration |
| → | [rich-menu-system](../rich-menu-system/SKILL.md) | Role change → menu reassignment |
| ← | [channel-management](../channel-management/SKILL.md) | Channel provides context |
| ← | [seller-lifecycle](../../../seller-engine/skills/seller-lifecycle/SKILL.md) | Seller approved → sync to member |
| ← | [staff-management](../../../seller-engine/skills/staff-management/SKILL.md) | Staff → seller_partner context switch |
