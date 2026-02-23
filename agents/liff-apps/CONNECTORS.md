# Connectors — LIFF Apps

Maps `~~category` placeholders used in this plugin's skills and commands.

| Category | Concrete Tool | Location | Description |
|----------|--------------|----------|-------------|
| `~~liff-app` | LIFF Mini Apps (5 apps) | `static/liff*/` | Buyer, Seller, Admin, Promotion, Support |
| `~~api` | REST API Controllers | `controllers/api_*.py` | 97 endpoints: 46 buyer + 28 seller + 23 admin |
| `~~identity` | LIFF SDK Auth | `controllers/api_auth.py` | Token validation, mock auth |
| `~~messaging` | LINE Messaging | `services/line_messaging.py` | In-app notifications |

## Key Files
- `core_line_integration/static/liff/` — Buyer LIFF app
- `core_line_integration/static/liff_seller/` — Seller LIFF app
- `core_line_integration/static/liff_admin/` — Admin LIFF app
- `core_line_integration/static/liff_promotion/` — Promotion app (stub)
- `core_line_integration/static/liff_support/` — Support app (stub)
- `core_line_integration/controllers/api_auth.py` — Auth middleware
- `core_line_integration/controllers/liff.py` — LIFF page endpoints

## Auth Modes
| Mode | Header | When |
|------|--------|------|
| Production | `Authorization: Bearer <liff_token>` + `X-Channel-Code` | LIFF in LINE |
| Dev Mock | `X-Line-User-Id` + `X-Channel-Code` | Local testing |
