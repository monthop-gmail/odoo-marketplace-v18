# Connectors — Finance

Maps `~~category` placeholders used in this plugin's skills and commands.

| Category | Concrete Tool | Location | Description |
|----------|--------------|----------|-------------|
| `~~marketplace-engine` | Odoo 18 (core_marketplace) | `core_marketplace/models/` | Commission, wallet, payment models |
| `~~payment` | Odoo Accounting | `models/account_move.py` | Journal entries, invoices |
| `~~wallet` | Seller Wallet | `models/seller_wallet.py` | Balance, transactions |
| `~~api` | REST API | `controllers/api_*.py` | Wallet, withdrawal endpoints |
| `~~notification` | LINE Push | `services/line_messaging.py` | Payment/withdrawal notifications |

## Key Files
- `core_marketplace/models/seller_payment.py` — Commission tracking
- `core_marketplace/models/seller_wallet.py` — Wallet balance
- `core_marketplace/models/seller_wallet_transaction.py` — Transaction log
- `core_marketplace/models/seller_withdrawal_request.py` — Withdrawals
- `core_marketplace/models/account_move.py` — Accounting integration
- `core_marketplace/models/res_config.py` — Commission settings
- `core_line_integration/controllers/api_seller_wallet.py` — Seller wallet API
- `core_line_integration/controllers/api_admin_wallets.py` — Admin wallet API
