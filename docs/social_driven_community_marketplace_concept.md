# Social-Driven Community Marketplace Platform

## Powered by LINE OA + LIFF + Odoo Marketplace

---

# 1. Core Concept

> Use Social Media to create demand\
> Use LINE as the Customer Hub\
> Use Odoo as the Business Engine

This platform is not just an online store.\
It is a **LINE-Centric Commerce Ecosystem** driven by community sellers and social traffic.

---

# 2. Overall Architecture

```
Social Media (YouTube / Facebook / TikTok / X)
    ↓ Value-Based Content & Entertainment (80% content, 20% selling)
    ↓ Brand Ambassadors / Gurus endorse products
    ↓ AI Content Distribution (Multi-platform)
LINE OA (Customer Entry Point)
    ↓ Identity, CRM, Broadcast, Notifications
LIFF Mini App (Marketplace UI)
    ↓ 5 apps: buyer, admin, seller, promotion, support
Odoo + Webkul Marketplace (Core Engine)
    ↓ Order / Stock / Commission / Accounting / Endorsements
```

---

# 3. Platform Roles

## Default Role: Buyer

All users start as:
- Buyer
- seller_status = none

## Seller Application Flow

```
none → draft → pending → approved
```

Once approved:
- Buyer + Seller roles
- Access to Seller Dashboard
- Product Management
- Sales Report

Dynamic menu is rendered based on role and seller status.

## Brand Ambassador / Guru Role

- นักวิชาการ / นักพูด / Content Creator
- รับรองสินค้าเฉพาะทาง (Endorsement)
- ถ่ายทำ Content ที่แหล่งผลิต
- สร้างความน่าเชื่อถือให้สินค้า

---

# 4. Social Media Strategy

## Purpose of Social Platforms

- Build trust
- Educate audience
- Demonstrate products
- Generate traffic
- Entertainment + Education (Edutainment)

## Content Strategy: "สภา shop" Model

Inspired by "สภาโจ๊ก" - รายการล้อเลียนรัฐบาลที่มีมุขเด็ดๆ คนติดตามมาก

### Brand Ambassador Program
- อ.สมภาค → กูรูผ้าไหม (คนเหนือ ชอบแต่งตัว)
- รับรองสินค้าว่า "ของดี ไม่เอาเปรียบผู้บริโภค"
- หลายคน หลายหมวดสินค้า

### Content Production
- ถ่ายทำที่แหล่งผลิต (โรงงาน, ชุมชน, ฟาร์ม)
- บรรยากาศสนุกสนาน คลายเครียด
- Storytelling สร้างเรื่องราวให้สินค้า

### AI Content Distribution
- แปลง Video → Multi-format (blog, social caption, article)
- Auto-post: Facebook, X, Instagram, TikTok, LINE
- SEO Optimization สำหรับ Google
- บทความลงเว็บไซต์/เว็บบอร์ด

## Funnel Strategy

```
Content (Entertainment + Education)
    ↓
Brand Ambassador Endorsement
    ↓
Multi-Platform Distribution (AI-powered)
    ↓
Traffic → LINE OA → LIFF → Marketplace
    ↓
Trust Purchase → Repeat Orders
```

---

# 5. LINE OA as Customer Hub

LINE handles:
- Identity (LINE User ID)
- CRM
- Broadcast
- Notifications
- Entry to LIFF Marketplace

All users are synced to Odoo via:
```
line_user_id → res.partner
```

---

# 6. LIFF Mini App Functions

## Buyer Features:
- Browse products
- Search
- Order history
- Open shop (Apply Seller)
- View Endorsed Products (by Gurus)

## Seller Features (after approval):
- Add products
- Manage products
- View sales dashboard
- Commission tracking
- Wallet (future phase)
- Request Endorsement from Gurus

## Brand Ambassador Features:
- Manage endorsements
- Content library
- Production schedule
- Analytics (engagement, conversion)

---

# 7. Odoo Marketplace Engine

Core modules:
- Website Sale
- Stock
- Accounting
- Webkul Marketplace

Extended with:
- Seller Status Engine
- Commission Logic
- Wallet System
- Dynamic Menu Config
- **Brand Endorsement System** (NEW)
- **Content Production Management** (NEW)
- **Multi-Platform Distribution** (NEW)

---

# 8. Revenue Model

1. Commission per order
2. Premium Seller subscription
3. Boost product placement
4. Affiliate system
5. Featured store promotion
6. **Brand Endorsement Fees** (NEW)
7. **Content Production Services** (NEW)

---

# 9. Competitive Positioning

Unlike Shopee or TikTok Shop:

- You own customer data
- You control commission
- You control branding
- You control ecosystem growth
- **Trust-based commerce via Guru endorsements**

Positioning:
> A Community Marketplace powered by Social Traffic, LINE Infrastructure, and Trusted Brand Ambassadors

---

# 10. Future Expansion Phases

## Phase 1: Buyer + Seller basic marketplace ✅

## Phase 2: Wallet, Withdrawal, Advanced commission

## Phase 3: 
- Affiliate network
- AI content moderation
- Seller ranking algorithm
- Boost marketplace ads
- **Brand Ambassador Program** (สภา shop)
- **Content Production Studio**
- **AI Multi-Platform Distribution**

---

# 11. Strategic Summary

This platform integrates:
- Social Media (Traffic Engine)
- LINE (Customer Hub)
- LIFF (Commerce Interface)
- Odoo (ERP Core System)
- **Brand Ambassadors (Trust Engine)**
- **AI Content Distribution (Amplification Engine)**

It creates a scalable, controllable, community-driven marketplace ecosystem where:
- Content creates demand
- Gurus build trust
- AI amplifies reach
- LINE captures customers
- Odoo manages business

---

# 12. "สภา shop" Implementation Plan

## New Module: `council_shop`

### Models Needed:
1. `brand_ambassador.py` - กูรู/นักวิชาการรับรองสินค้า
2. `product_endorsement.py` - การรับรองสินค้า
3. `content_production.py` - Production plan & schedule
4. `content_distribution.py` - Multi-platform posting
5. `affiliate_tracking.py` - ติดตาม traffic/sales จาก content

### Features:
- Endorsement badge บนสินค้า
- Ambassador profile page
- Content library (video, article, social posts)
- Auto-publishing pipeline
- Analytics: content → traffic → conversion

### AI/Bot Integration:
- Video → Text summary (blog, social caption)
- Auto-generate SEO content
- Schedule & publish across platforms
- Monitor engagement & sentiment
