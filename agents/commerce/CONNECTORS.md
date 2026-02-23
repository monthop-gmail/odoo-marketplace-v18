# Connectors — Commerce

Maps `~~category` placeholders used in this plugin's skills and commands.

| Category | Concrete Tool | Location | Description |
|----------|--------------|----------|-------------|
| `~~marketplace-engine` | Odoo 18 (core_marketplace) | `core_marketplace/models/` | Product, order, stock models |
| `~~stock` | Odoo Stock | `models/stock.py` | Inventory, stock picking, delivery |
| `~~payment` | Odoo Accounting | `models/account_move.py` | Invoice generation |
| `~~api` | REST API | `controllers/api_*.py` | Product, cart, order endpoints |
| `~~liff-app` | LIFF Mini Apps | `static/liff*/` | Product browsing, cart, checkout UI |
| `~~notification` | LINE Push | `services/line_messaging.py` | Order status notifications |

## Key Files
- `core_marketplace/models/marketplace_product.py` — Product extensions
- `core_marketplace/models/sale.py` — Order extensions
- `core_marketplace/models/stock.py` — Stock extensions
- `core_marketplace/models/mp_pricelist_item.py` — Seller pricing
- `core_line_integration/controllers/api_buyer_products.py` — Product API
- `core_line_integration/controllers/api_buyer_cart.py` — Cart API
- `core_line_integration/controllers/api_buyer_orders.py` — Order API
- `core_line_integration/controllers/api_seller_products.py` — Seller products API
