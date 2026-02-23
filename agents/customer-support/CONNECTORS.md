# Connectors — Customer Support

Maps `~~category` placeholders used in this plugin's skills and commands.

| Category | Concrete Tool | Location | Description |
|----------|--------------|----------|-------------|
| `~~marketplace-engine` | Odoo 18 | `core_marketplace/` | Order and product data for context |
| `~~messaging` | LINE Messaging API | `services/line_messaging.py` | Reply to customers |
| `~~liff-app` | Support LIFF App | `static/liff_support/` | Support ticket UI |
| `~~crm` | Odoo res.partner | `models/res_partner.py` | Customer profiles and history |
| `~~api` | REST API | `controllers/api_*.py` | Support endpoints |
| `~~notification` | LINE Push + Email | `services/line_messaging.py` | Ticket status updates |

## Note
Customer support plugin is primarily future-facing (Phase 3). Current functionality is limited to triage guidelines and response templates.
