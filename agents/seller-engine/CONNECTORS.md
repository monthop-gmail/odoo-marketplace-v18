# Connectors — Seller Engine

Maps `~~category` placeholders used in this plugin's skills and commands.

| Category | Concrete Tool | Location | Description |
|----------|--------------|----------|-------------|
| `~~marketplace-engine` | Odoo 18 (core_marketplace) | `core_marketplace/models/` | Seller models: res.partner, seller.shop, seller.review |
| `~~identity` | LINE Login + LIFF SDK | `controllers/api_auth.py` | Seller authentication |
| `~~notification` | LINE Push + Email | `services/line_messaging.py` + `edi/` | Seller status notifications |
| `~~wallet` | Seller Wallet | `models/seller_wallet.py` | Auto-create wallet on approval |
| `~~rich-menu` | LINE Rich Menu API | `models/line_rich_menu.py` | Switch to seller menu on approval |
| `~~crm` | Odoo res.partner | `models/res_partner.py` | Seller profiles, status management |
| `~~api` | REST API | `controllers/api_seller_*.py` | Seller API endpoints |

## Key Files
- `core_marketplace/models/res_partner.py` — Seller status, approval logic
- `core_marketplace/models/seller_shop.py` — Shop model
- `core_marketplace/models/seller_review.py` — Review model
- `core_marketplace/models/seller_shop_staff.py` — Staff model
- `core_line_integration/controllers/api_seller_apply.py` — Apply API
- `core_line_integration/controllers/api_seller_shop.py` — Shop API
- `core_line_integration/controllers/api_seller_staff.py` — Staff API
