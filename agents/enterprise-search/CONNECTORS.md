# Connectors — Enterprise Search

Maps `~~category` placeholders used in this plugin's skills and commands.

| Category | Concrete Tool | Location | Description |
|----------|--------------|----------|-------------|
| `~~marketplace-engine` | Odoo 18 ORM | `core_marketplace/` | Model search via domain filters |
| `~~api` | REST API | `controllers/api_*.py` | Search endpoints |
| `~~liff-app` | LIFF Apps | `static/liff*/` | Search UI in buyer/admin apps |

## Searchable Models
| Model | Key Fields | API |
|-------|-----------|-----|
| `product.template` | name, categ_id, marketplace_seller_id | `/api/line-buyer/products?search=` |
| `res.partner` (sellers) | name, seller_status | `/api/line-admin/sellers?search=` |
| `sale.order` | name, partner_id, state | `/api/line-buyer/orders` |
| `line.channel.member` | line_user_id, member_type | `/api/line-admin/members?search=` |
