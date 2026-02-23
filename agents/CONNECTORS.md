# Connectors — Tool Category Mapping

This file maps abstract `~~category` placeholders used in skills and commands to the concrete tools in this marketplace platform.

## Connector Categories

| Category | Concrete Tool | Module | Description |
|----------|--------------|--------|-------------|
| `~~marketplace-engine` | Odoo 18 (core_marketplace) | `core_marketplace/` | Multi-vendor backend: sellers, products, orders, stock, commission |
| `~~messaging` | LINE Messaging API | `services/line_api.py` | Push/reply/broadcast messages, flex messages, templates |
| `~~identity` | LINE Login + LIFF SDK | `controllers/api_auth.py` | User authentication via LIFF token or dev mock header |
| `~~liff-app` | LIFF Mini Apps (5 apps) | `static/liff*/` | Buyer, Seller, Admin, Promotion, Support frontends |
| `~~notification` | LINE Push + Odoo Email | `services/line_messaging.py` + `edi/` | LINE push notifications + email templates |
| `~~payment` | Odoo Accounting | `models/account_move.py` | Journal entries, invoices, seller payment settlement |
| `~~wallet` | Seller Wallet System | `models/seller_wallet.py` | Wallet balance, transactions, withdrawal requests |
| `~~rich-menu` | LINE Rich Menu API | `models/line_rich_menu.py` | Role-based rich menus (buyer/seller/admin) |
| `~~webhook` | LINE Webhook | `controllers/webhook.py` | Event handling: follow, unfollow, message, postback |
| `~~crm` | Odoo res.partner | `models/res_partner.py` | Customer/seller profiles, LINE member mapping |
| `~~stock` | Odoo Stock | `models/stock.py` | Inventory, stock picking, delivery tracking |
| `~~api` | REST API Controllers | `controllers/api_*.py` | 97 endpoints: 46 buyer + 28 seller + 23 admin |

## Authentication Modes

| Mode | Header | When |
|------|--------|------|
| **Production** | `Authorization: Bearer <liff_token>` + `X-Channel-Code` | LIFF app in LINE |
| **Dev Mock** | `X-Line-User-Id` + `X-Channel-Code` | Local development/testing |
| **Odoo Backend** | Session cookie | Odoo admin panel |

## Base URLs

| API Group | Base URL | Auth |
|-----------|----------|------|
| Buyer API | `/api/line-buyer/` | LIFF token / mock |
| Seller API | `/api/line-seller/` | LIFF token / mock (requires seller role) |
| Admin API | `/api/line-admin/` | LIFF token / mock (requires officer/manager) |
| Webhook | `/api/line-buyer/webhook/<channel_code>` | LINE signature |
