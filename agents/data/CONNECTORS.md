# Connectors — Data

Maps `~~category` placeholders used in this plugin's skills and commands.

| Category | Concrete Tool | Location | Description |
|----------|--------------|----------|-------------|
| `~~marketplace-engine` | Odoo 18 + PostgreSQL | `core_marketplace/` | All marketplace data models |
| `~~api` | REST API | `controllers/api_*.py` | Dashboard and reporting endpoints |
| `~~liff-app` | Admin LIFF App | `static/liff_admin/` | Dashboard visualizations |

## Key Tables
- `res_partner` — Sellers, buyers, users
- `product_template` — Products
- `sale_order` / `sale_order_line` — Orders
- `seller_payment` — Commission records
- `seller_wallet` / `seller_wallet_transaction` — Wallet data
- `seller_withdrawal_request` — Withdrawals
- `seller_shop` — Shop profiles
- `seller_review` — Reviews and ratings
- `line_channel_member` — LINE members
