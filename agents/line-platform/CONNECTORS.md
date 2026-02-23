# Connectors — LINE Platform

Maps `~~category` placeholders used in this plugin's skills and commands.

| Category | Concrete Tool | Location | Description |
|----------|--------------|----------|-------------|
| `~~messaging` | LINE Messaging API | `services/line_api.py` | Push, reply, broadcast, flex messages |
| `~~identity` | LINE Login + LIFF SDK | `controllers/api_auth.py` | LIFF token auth, LINE profile |
| `~~webhook` | LINE Webhook | `controllers/webhook.py` | Event handling: follow, unfollow, message, postback |
| `~~rich-menu` | LINE Rich Menu API | `models/line_rich_menu.py` | Role-based menus |
| `~~notification` | LINE Push + Email | `services/line_messaging.py` + `edi/` | Event notifications |
| `~~crm` | Odoo res.partner | `models/res_partner.py` | LINE-Odoo identity mapping |

## Key Files
- `core_line_integration/models/line_channel.py` — Channel configuration
- `core_line_integration/models/line_channel_member.py` — Member mapping
- `core_line_integration/models/line_liff.py` — LIFF app registration
- `core_line_integration/models/line_rich_menu.py` — Rich menu records
- `core_line_integration/services/line_api.py` — LINE API service
- `core_line_integration/services/line_messaging.py` — Message builder
- `core_line_integration/controllers/webhook.py` — Webhook handler
