# Social-Driven Community Marketplace Platform

> Multi-Vendor Marketplace ขับเคลื่อนด้วย **Social Media + LINE OA + LIFF + Odoo 18**

[![Odoo Version](https://img.shields.io/badge/Odoo-18.0-blueviolet)](#) [![Python](https://img.shields.io/badge/Python-3.10+-blue)](#) [![License](https://img.shields.io/badge/License-LGPL--3-green)](#) [![LINE](https://img.shields.io/badge/LINE-OA%20%2B%20LIFF-00C300)](#)

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Modules](#modules)
  - [core\_marketplace](#1-core_marketplace)
  - [core\_line\_integration](#2-core_line_integration)
  - [core\_ambassador](#3-core_ambassador)
  - [agents](#4-agents)
- [Business Roles](#business-roles)
- [API Reference](#api-reference)
- [Revenue Model](#revenue-model)
- [Development Conventions](#development-conventions)
- [Project Structure](#project-structure)
- [Roadmap](#roadmap)
- [Getting Started](#getting-started)

---

## Overview

แพลตฟอร์มนี้ไม่ใช่แค่ร้านค้าออนไลน์ แต่เป็น **LINE-Centric Commerce Ecosystem** ที่ขับเคลื่อนด้วย Community Sellers และ Social Traffic

**Core Concept:**
> ใช้ Social Media สร้าง Demand → ใช้ LINE เป็น Customer Hub → ใช้ Odoo เป็น Business Engine

**จุดเด่นเทียบกับ Shopee / TikTok Shop:**
- เป็นเจ้าของ Customer Data เอง
- ควบคุม Commission เอง
- ควบคุม Branding เอง
- ควบคุม Ecosystem Growth เอง

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│         Social Media (Traffic Engine)            │
│      YouTube / Facebook / TikTok / Instagram     │
│        80% Value Content — 20% Selling           │
└──────────────────────┬──────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────┐
│            LINE OA (Customer Hub)                │
│     Identity · CRM · Broadcast · Notification    │
│         Rich Menu (role-based switching)          │
└──────────────────────┬──────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────┐
│          LIFF Mini Apps (Commerce UI)            │
│  ┌─────────┐ ┌───────┐ ┌────────┐ ┌──────────┐ │
│  │  Buyer  │ │Seller │ │ Admin  │ │Promotion │ │
│  └─────────┘ └───────┘ └────────┘ └──────────┘ │
│                  ┌──────────┐                    │
│                  │ Support  │                    │
│                  └──────────┘                    │
└──────────────────────┬──────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────┐
│       Odoo 18 + Marketplace Engine (ERP)         │
│   Order · Stock · Commission · Wallet · Acct.    │
└─────────────────────────────────────────────────┘
```

---

## Modules

### 1. `core_marketplace`

> Multi-vendor marketplace engine (based on Webkul) — `v18.0.1.0.0`

**Depends:** `website_sale`, `stock_account`, `delivery`

**Models (25 files):**

| Model | Description |
|-------|-------------|
| `res_partner.py` | Seller profile extension (seller_status, commission, shop) |
| `marketplace_product.py` | Marketplace product with approval workflow |
| `seller_shop.py` | Seller shop configuration & branding |
| `seller_shop_staff.py` | Shop staff management |
| `seller_payment.py` | Seller payment settlement |
| `seller_payment_method.py` | Payment method configuration |
| `seller_review.py` | Buyer reviews & ratings for sellers |
| `seller_wallet.py` | Seller wallet balance |
| `seller_wallet_transaction.py` | Wallet transaction history |
| `seller_withdrawal_request.py` | Withdrawal request workflow |
| `marketplace_dashboard.py` | Seller & admin dashboard data |
| `mp_pricelist_item.py` | Marketplace pricelist logic |
| `sale.py` | Sale order extension (commission split) |
| `stock.py` | Stock picking per seller |
| `account_move.py` | Invoice/journal entries |
| `res_config.py` | Marketplace configuration settings |
| `website.py` | Website integration |

**Security Groups:**

| Group | Access Level |
|-------|-------------|
| `marketplace_manager_group` | Full system access |
| `marketplace_officer_group` | Seller approval, product moderation |
| `marketplace_seller_group` | Approved seller features |
| `marketplace_draft_seller_group` | Pending seller (limited) |

**Frontend Assets:** CSS (marketplace, snippets, star-rating, review chatter) + JS (marketplace, snippets, star-rating, review chatter, circle chart, timeago)

---

### 2. `core_line_integration`

> LINE OA integration + REST API for LIFF apps — `v18.0.1.0.0`

**Depends:** `base`, `sale`, `website_sale`, `core_marketplace`

**Models (12 files):**

| Model | Description |
|-------|-------------|
| `line_channel.py` | LINE OA channel configuration |
| `line_liff.py` | LIFF app registration |
| `line_channel_member.py` | LINE user ↔ Odoo partner mapping |
| `line_rich_menu.py` | Role-based rich menu management |
| `line_wishlist.py` | Buyer wishlist via LINE |
| `line_compare.py` | Product comparison |
| `line_notify_log.py` | Notification logging |
| `admin_team_member.py` | Admin team assignment |
| `res_partner.py` | Partner extension for LINE |
| `res_config_settings.py` | LINE config settings |
| `sale_order.py` | Sale order LINE notifications |

**Controllers / API (26 files, ~97 endpoints):**

| Controller | Endpoints | Description |
|-----------|-----------|-------------|
| `api_auth.py` | Auth | LIFF token validation, dev mock |
| `api_products.py` | Buyer | Product browsing, search, detail |
| `api_cart.py` | Buyer | Cart management |
| `api_checkout.py` | Buyer | Checkout flow |
| `api_wishlist.py` | Buyer | Wishlist CRUD |
| `api_compare.py` | Buyer | Product comparison |
| `api_profile.py` | Buyer | Profile management |
| `api_address.py` | Buyer | Address management |
| `api_seller_apply.py` | Seller | Seller application flow |
| `api_seller_products.py` | Seller | Product management |
| `api_seller_orders.py` | Seller | Order management |
| `api_seller_dashboard.py` | Seller | Sales dashboard |
| `api_seller_profile.py` | Seller | Seller profile |
| `api_seller_staff.py` | Seller | Staff management |
| `api_seller_wallet.py` | Seller | Wallet & withdrawals |
| `api_admin_dashboard.py` | Admin | Platform dashboard |
| `api_admin_orders.py` | Admin | Order management |
| `api_admin_members.py` | Admin | Member management |
| `api_admin_team.py` | Admin | Team management |
| `api_admin_wallet.py` | Admin | Wallet oversight |
| `webhook.py` | LINE | Event handling (follow, unfollow, message, postback) |
| `liff.py` | LIFF | LIFF app page routes |

**Services:**

| Service | Description |
|---------|-------------|
| `line_api.py` | LINE Messaging API client (push, reply, broadcast) |
| `line_messaging.py` | Flex message templates & notification helpers |

**Tests (10 files):** Unit tests + API tests + UAT flow documentation

---

### 3. `core_ambassador`

> Brand Ambassador / Guru endorsement system (สภา shop) — `v18.0.1.0.0`

**Depends:** `core_marketplace`, `core_line_integration`

**Models (5 files):**

| Model | Description |
|-------|-------------|
| `brand_ambassador.py` | res.partner extension (is_ambassador, ambassador_state, tier, specialties) |
| `ambassador_specialty.py` | Expertise categories (EV, Tech, Food, Health, Fashion, Home) |
| `ambassador_application.py` | Application workflow: draft → submitted → under_review → approved/rejected |
| `product_endorsement.py` | Endorsement record (ambassador + product link, review, video, rating) |
| `endorsement_request.py` | Request workflow: seller requests → ambassador approves/rejects |

**Security Groups:**

| Group | Access Level |
|-------|-------------|
| `marketplace_ambassador_group` | Approved ambassador (independent from seller hierarchy) |

**Controllers / API (6 files, ~30 endpoints):**

| Controller | Endpoints | Description |
|-----------|-----------|-------------|
| `api_ambassador_apply.py` | Buyer | Ambassador application, specialties |
| `api_ambassador_endorsements.py` | Ambassador | Manage endorsements, approve/reject requests, dashboard |
| `api_seller_endorsements.py` | Seller | Request endorsement, browse ambassadors |
| `api_admin_ambassadors.py` | Admin | Manage ambassadors, applications, endorsements |
| `api_buyer_endorsements.py` | Buyer | Browse endorsed products, ambassador profiles |

**Ambassador Tier & Commission:**

| Tier | Commission Rate | Source |
|------|----------------|--------|
| Bronze | 5% | Platform share |
| Silver | 7% | Platform share |
| Gold | 10% | Platform share |

---

### 4. `agents`

> Claude Code Agent Architecture — Plugin Pattern

ตาม [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins) pattern

**Skills (auto-activated domain knowledge):**

| Skill | Domain |
|-------|--------|
| `product-admin/` | Master agent — architecture, security, coordination |
| `seller-engine/` | Seller lifecycle, shops, reviews |
| `commerce/` | Products, orders, stock, pricing |
| `commission-wallet/` | Commission, payments, wallet |
| `line-integration/` | LINE OA, webhook, messaging |
| `liff-frontend/` | LIFF apps, REST API, UI/UX |

**Commands (slash commands):**

| Command | Description |
|---------|-------------|
| `/approve-seller` | Approve seller application |
| `/review-product` | Review product submission |
| `/check-commission` | Check commission status |
| `/deploy-richmenu` | Deploy LINE rich menu |
| `/system-status` | System health check |
| `/quick-post` | Quick social media post |

**Connectors (`~~category` mapping):**

| Category | Tool | Description |
|----------|------|-------------|
| `~~marketplace-engine` | Odoo 18 (core_marketplace) | Multi-vendor backend |
| `~~messaging` | LINE Messaging API | Push/reply/broadcast |
| `~~identity` | LINE Login + LIFF SDK | Authentication |
| `~~liff-app` | LIFF Mini Apps | 5 frontend apps |
| `~~notification` | LINE Push + Odoo Email | Notifications |
| `~~payment` | Odoo Accounting | Payment settlement |
| `~~wallet` | Seller Wallet System | Wallet & withdrawals |
| `~~rich-menu` | LINE Rich Menu API | Role-based menus |
| `~~webhook` | LINE Webhook | Event handling |
| `~~crm` | Odoo res.partner | Customer/seller profiles |
| `~~stock` | Odoo Stock | Inventory & delivery |
| `~~api` | REST Controllers | 97 endpoints total |

---

## Business Roles

```
┌───────────────────────────────────────────────┐
│              Seller Status Flow                │
│                                                │
│   none ──→ draft ──→ pending ──→ approved      │
│    │                     │           │         │
│  Buyer              Waiting       Full Seller  │
│  (default)          Approval      + Dashboard  │
└───────────────────────────────────────────────┘
```

| Role | Status | Access |
|------|--------|--------|
| **Buyer** | Default (ทุกคน) | Browse, Search, Order, Wishlist, Compare |
| **Draft Seller** | `seller_status=draft` | กรอกใบสมัคร Seller |
| **Pending Seller** | `seller_status=pending` | รออนุมัติจาก Admin |
| **Approved Seller** | `seller_status=approved` | จัดการสินค้า, Dashboard, Commission, Wallet |
| **Ambassador** | `ambassador_state=approved` | รับรองสินค้า, Endorsement Dashboard, Commission |
| **Platform Officer** | Security group | อนุมัติ Seller/Ambassador, Moderate สินค้า |
| **Platform Manager** | Security group | Full system access |

---

## API Reference

### Authentication

| Mode | Header | Use Case |
|------|--------|----------|
| **Production** | `Authorization: Bearer <liff_token>` + `X-Channel-Code` | LIFF app in LINE |
| **Dev Mock** | `X-Line-User-Id` + `X-Channel-Code` | Local development/testing |
| **Odoo Backend** | Session cookie | Odoo admin panel |

### Base URLs

| API Group | Base URL | Endpoints | Auth Required |
|-----------|----------|-----------|---------------|
| **Buyer** | `/api/line-buyer/` | 49 endpoints | LIFF token / mock |
| **Seller** | `/api/line-seller/` | 34 endpoints | LIFF token + seller role |
| **Ambassador** | `/api/line-ambassador/` | 8 endpoints | LIFF token + ambassador role |
| **Admin** | `/api/line-admin/` | 31 endpoints | LIFF token + officer/manager |
| **Webhook** | `/api/line-buyer/webhook/<channel_code>` | 1 endpoint | LINE signature |

### Response Format

```json
{
  "success": true,
  "data": { ... },
  "error": null
}
```

### HTTP Methods

| Method | Usage |
|--------|-------|
| `GET` | Read / List |
| `POST` | Create / Action |
| `PUT` | Update |
| `DELETE` | Remove |

---

## Revenue Model

| # | Revenue Stream | Phase |
|---|---------------|-------|
| 1 | Commission per order | Phase 1 |
| 2 | Premium Seller subscription | Phase 2 |
| 3 | Boost product placement | Phase 3 |
| 4 | Featured store promotion | Phase 3 |
| 5 | Affiliate system | Phase 4 |
| 6 | Brand Endorsement fees (Ambassador commission) | Phase 3 |

---

## Development Conventions

### Odoo 18 Standards
- **Python:** PEP 8, `_` prefix for private methods
- **Models:** inherit via `_inherit`, new models use dotted names (e.g., `seller.shop`)
- **Views:** XML with `<odoo>` root, `noupdate="1"` for security data
- **Security:** always define `ir.model.access.csv` + record rules
- **Assets:** `web.assets_backend` / `web.assets_frontend` in manifest

### API Convention
- Base URL: `/api/line-buyer/`, `/api/line-seller/`, `/api/line-admin/`
- Auth: `Authorization: Bearer <liff_token>` + `X-Channel-Code: <code>`
- Response: JSON with `success`, `data`, `error` fields
- Methods: `GET` (read), `POST` (create/action), `PUT` (update), `DELETE` (remove)

---

## Project Structure

```
odoo-marketplace-v18/
├── CLAUDE.md                              # Project conventions for Claude Code
├── social_driven_community_marketplace_concept.md
│
├── core_marketplace/                      # Odoo Module — Marketplace Engine
│   ├── __manifest__.py                    #   v18.0.1.0.0, depends: website_sale, stock_account, delivery
│   ├── models/                            #   25 models (seller, product, shop, wallet, dashboard...)
│   ├── controllers/                       #   Web controllers
│   ├── views/                             #   Backend + Website templates + Snippets
│   ├── security/                          #   Groups + ACL (ir.model.access.csv)
│   ├── data/                              #   Demo data, config, sequences
│   ├── edi/                               #   Email templates (seller/product status change)
│   ├── wizard/                            #   Wizards (seller status, payment, registration)
│   ├── static/                            #   CSS + JS (frontend & backend)
│   └── i18n/                              #   Translations
│
├── core_line_integration/                 # Odoo Module — LINE + API
│   ├── __manifest__.py                    #   v18.0.1.0.0, depends: base, sale, website_sale, core_marketplace
│   ├── models/                            #   12 models (channel, member, LIFF, rich menu, wishlist...)
│   ├── controllers/                       #   26 API controllers (~97 endpoints)
│   ├── services/                          #   LINE API client + messaging helpers
│   ├── views/                             #   Backend views (channel, LIFF, member, rich menu)
│   ├── security/                          #   Groups + ACL
│   ├── data/                              #   Channel data, cron, Thai provinces
│   ├── tests/                             #   10 test files + UAT docs
│   ├── wizard/                            #   Shipping label, LINE message wizard
│   ├── report/                            #   Shipping label report
│   ├── scripts/                           #   Utility scripts
│   ├── docs/                              #   API documentation
│   └── static/                            #   LIFF apps (buyer, seller, admin, promotion, support)
│
├── core_ambassador/                       # Odoo Module — Brand Ambassador (สภา shop)
│   ├── __manifest__.py                    #   v18.0.1.0.0, depends: core_marketplace, core_line_integration
│   ├── models/                            #   5 models (ambassador, specialty, application, endorsement, request)
│   ├── controllers/                       #   6 API controllers (~30 endpoints)
│   ├── views/                             #   6 backend view files + menu
│   ├── security/                          #   Groups + ACL + record rules
│   └── data/                              #   Sequences, specialties, config
│
├── docs/                                  # Project documentation
│   ├── social_driven_community_marketplace_concept.md
│   └── council_shop_priorities.md         #   สภา shop MVP priorities
│
└── agents/                                # Claude Code Agent Plugin
    ├── plugin.json                        #   Manifest (marketplace-platform v1.0.0)
    ├── CONNECTORS.md                      #   ~~category → tool mapping (12 connectors)
    ├── skills/                            #   6 auto-activated domain skills
    │   ├── product-admin/                 #     Master agent
    │   ├── seller-engine/                 #     Seller lifecycle
    │   ├── commerce/                      #     Products, orders, stock
    │   ├── commission-wallet/             #     Commission, wallet
    │   ├── line-integration/              #     LINE OA, webhook
    │   └── liff-frontend/                 #     LIFF apps, REST API
    └── commands/                          #   6 slash commands
        ├── approve-seller.md
        ├── review-product.md
        ├── check-commission.md
        ├── deploy-richmenu.md
        ├── system-status.md
        └── quick-post.md
```

---

## Roadmap

### Phase 1 — Foundation (Complete)
- [x] Multi-vendor marketplace engine
- [x] Seller registration & approval flow
- [x] Product management with approval workflow
- [x] LINE OA integration (channel, member sync)
- [x] LIFF buyer app (browse, cart, checkout, order history)
- [x] LIFF seller app (products, orders, dashboard)
- [x] LIFF admin app (members, orders, dashboard)
- [x] REST API (97 endpoints: buyer + seller + admin)
- [x] Webhook handling (follow, unfollow, message, postback)
- [x] Rich menu (role-based switching)
- [x] Review & rating system

### Phase 2 — Commerce (Complete)
- [x] Wallet system
- [x] Withdrawal request workflow
- [x] Stock management & validation
- [x] Shop staff system

### Phase 3 — Brand Ambassador / สภา shop
- [x] Sprint 1: Models, Security, Views, API (~30 endpoints)
- [ ] Sprint 2: Ambassador Wallet, Commission tracking
- [ ] Sprint 3: LINE Integration, Rich Menu for ambassadors
- [ ] Sprint 4: Analytics Dashboard, UTM tracking

### Phase 4 — Growth
- [ ] Affiliate network
- [ ] AI content moderation
- [ ] Seller ranking algorithm
- [ ] Boost marketplace ads
- [ ] Featured store promotion

---

## Getting Started

### Prerequisites

- **Odoo 18** Community or Enterprise
- **Python 3.10+**
- **PostgreSQL 14+**
- **LINE Developers Account** (Messaging API channel)

### Installation

```bash
# 1. Clone repository
git clone https://github.com/monthop-gmail/odoo-marketplace-v18.git

# 2. Copy modules to Odoo addons path
cp -r core_marketplace /path/to/odoo/addons/
cp -r core_line_integration /path/to/odoo/addons/

# 3. Update Odoo module list
./odoo-bin -d <database> -u base --stop-after-init

# 4. Install modules via Odoo UI
#    Apps → Search "Core Marketplace" → Install
#    Apps → Search "Core LINE Integration" → Install
```

### LINE OA Configuration

1. สร้าง LINE Messaging API Channel ที่ [LINE Developers Console](https://developers.line.biz/)
2. ตั้งค่า Webhook URL: `https://<your-domain>/api/line-buyer/webhook/<channel_code>`
3. สร้าง LIFF App สำหรับแต่ละ role (buyer, seller, admin, promotion, support)
4. ใน Odoo Backend → LINE Integration → Channels → สร้าง Channel ใหม่
5. กำหนด LIFF ID ใน Odoo Backend → LINE Integration → LIFF Apps

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **ERP** | Odoo 18 (Python, PostgreSQL, XML) |
| **API** | Odoo HTTP Controllers (REST JSON) |
| **Messaging** | LINE Messaging API |
| **Frontend** | LIFF SDK + HTML/CSS/JS |
| **Auth** | LIFF Token / LINE Login |
| **AI Agent** | Claude Code (Plugin Pattern) |

---

## Author

**SiamCivilize** — Social-Driven Community Marketplace Platform

---

> *Built with LINE OA + LIFF + Odoo 18 — Community-powered, Social-driven*
