# Social-Driven Community Marketplace Platform

## Project Overview
ระบบ Multi-Vendor Marketplace ที่ขับเคลื่อนด้วย Social Media + LINE OA + LIFF + Odoo 18

### Architecture Flow
```
Social Media (YouTube/Facebook/TikTok)
    ↓ Value-Based Content (80% content, 20% selling)
LINE OA (Customer Hub)
    ↓ Identity, CRM, Broadcast, Notifications
LIFF Mini App (Marketplace UI)
    ↓ 5 apps: buyer, admin, seller, promotion, support
Odoo 18 + Marketplace Engine
    ↓ Order / Stock / Commission / Accounting
```

## Core Modules

### 1. core_marketplace (Odoo Module)
- **Path:** `core_marketplace/`
- **Depends:** website_sale, stock_account, delivery
- **Purpose:** Multi-vendor marketplace engine (based on Webkul)
- **Key Models:** res.partner (seller), marketplace.product, seller.shop, seller.payment, seller.review, marketplace.dashboard, marketplace.stock
- **Security Groups:**
  - `marketplace_manager_group` → Manager (full access)
  - `marketplace_officer_group` → Officer/Admin
  - `marketplace_seller_group` → Approved Seller
  - `marketplace_draft_seller_group` → Pending Seller

### 2. core_line_integration (Odoo Module)
- **Path:** `core_line_integration/`
- **Depends:** base, sale, website_sale, core_marketplace
- **Purpose:** LINE OA integration with full REST API for LIFF apps
- **Key Models:** line.channel, line.liff, line.channel.member, line.rich.menu, line.wishlist, line.compare, line.notify.log
- **API Base:** `/api/line-buyer/`
- **Auth:** LIFF token (production) / X-Line-User-Id (dev mock)
- **LIFF Apps:** liff/ (buyer), liff_admin/, liff_seller/, liff_promotion/, liff_support/

## Business Roles
| Role | Status | Access |
|------|--------|--------|
| Buyer | Default (all users) | Browse, Order, Wishlist, Compare |
| Draft Seller | seller_status=draft | Application form |
| Pending Seller | seller_status=pending | Waiting approval |
| Approved Seller | seller_status=approved | Product Mgmt, Dashboard, Commission |
| Platform Officer | Security group | Seller approval, Product moderation |
| Platform Manager | Security group | Full system access |

### Seller Flow
```
none → draft → pending → approved
```

## Revenue Model
1. Commission per order
2. Premium Seller subscription
3. Boost product placement
4. Featured store promotion
5. Affiliate system (future)

## Development Conventions

### Odoo 18 Standards
- Python: PEP 8, use `_` prefix for private methods
- Models: inherit existing models via `_inherit`, new models use dotted names (e.g., `seller.shop`)
- Views: XML with `<odoo>` root, use `noupdate="1"` for security data
- Security: always define ir.model.access.csv + record rules
- Assets: use `web.assets_backend` / `web.assets_frontend` in manifest

### Module Structure
```
module_name/
├── __init__.py
├── __manifest__.py
├── models/
├── controllers/
├── services/          (business logic services)
├── views/
├── security/
├── data/
├── static/
├── wizard/
├── tests/
├── docs/
└── report/
```

### API Convention (core_line_integration)
- Base URL: `/api/line-buyer/`
- Auth header: `Authorization: Bearer <liff_token>` + `X-Channel-Code: <code>`
- Response format: JSON with `success`, `data`, `error` fields
- HTTP methods: GET (read), POST (create/action), PUT (update), DELETE (remove)

## Agent Architecture (Plugin Pattern)

Structure follows [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins) pattern:

```
agents/
├── plugin.json                          # Manifest
├── CONNECTORS.md                        # ~~category → concrete tool mapping
├── skills/                              # Auto-activated domain knowledge
│   ├── product-admin/SKILL.md           # Master agent (architecture, security, coordination)
│   ├── seller-engine/SKILL.md           # Seller lifecycle, shops, reviews
│   ├── commerce/SKILL.md               # Products, orders, stock, pricing
│   ├── commission-wallet/SKILL.md       # Commission, payments, wallet
│   ├── line-integration/SKILL.md        # LINE OA, webhook, messaging
│   └── liff-frontend/SKILL.md           # LIFF apps, REST API, UI/UX
└── commands/                            # Explicit slash commands
    ├── approve-seller.md                # /approve-seller
    ├── review-product.md                # /review-product
    ├── check-commission.md              # /check-commission
    ├── deploy-richmenu.md               # /deploy-richmenu
    ├── system-status.md                 # /system-status
    └── quick-post.md                    # /quick-post
```

- **Skills**: YAML frontmatter with trigger description, auto-activated when relevant
- **Commands**: Explicit workflows with standalone/supercharged duality
- **Connectors**: Abstract `~~category` placeholders (e.g., `~~marketplace-engine`, `~~messaging`)

## Phase Roadmap
- **Phase 1:** Buyer + Seller basic marketplace (current)
- **Phase 2:** Wallet, Withdrawal, Advanced commission
- **Phase 3:** Affiliate network, AI content moderation, Seller ranking, Boost ads
