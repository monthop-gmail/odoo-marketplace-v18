# สภา shop - Urgent Priorities

## 🎯 Phase 3.1 MVP - Core Requirements

### 1. Revenue Share Model (สำคัญที่สุด)
**Purpose:** สร้างแรงจูงใจทางเศรษฐกิจให้ Gurus

**Requirements:**
- กำหนด Commission % สำหรับ Brand Ambassadors
  - Default: 5-10% จากยอดขายสินค้าที่รับรอง
  - Tiered: Bronze (5%), Silver (7%), Gold (10%)
- Payout System ใน Odoo
  - เชื่อมกับ Seller Wallet
  - Withdrawal Request สำหรับ Gurus
  - Monthly payout cycle
- Tracking System
  - Track ทุก order ที่มาจาก Endorsement
  - Attribute sale ให้ถูกต้อง (affiliate tracking)

**Models Needed:**
- `brand_ambassador.py` - profile, tier, commission_rate
- `endorsement_commission.py` - track commissions
- `endorsement_payout.py` - payout requests

---

### 2. Guru Verification Process
**Purpose:** ตรวจสอบความน่าเชื่อถือของ Ambassadors

**Requirements:**
- Application Form
  - ชื่อ-นามสกุล, credentials, expertise area
  - Upload: ID card, certificates, portfolio
  - Social media links (YouTube, Facebook, TikTok)
- Approval Workflow
  - Admin review & approve
  - Background check (optional)
- Guru Profile Page
  - Public profile ใน LIFF
  - แสดง specialties, followers, endorsement history
  - Verification badge

**Models Needed:**
- `brand_ambassador_application.py` - application form
- `brand_ambassador.py` - approved ambassadors
- `guru_specialty.py` - หมวดหมู่ความเชี่ยวชาญ

**Status Flow:**
```
draft → submitted → under_review → approved/rejected
```

---

### 3. Endorsement Badge System
**Purpose:** ทำให้เห็นชัดเจนว่าสินค้าไหนได้รับการรับรอง

**Requirements:**
- Endorsement Request (จาก Seller → Guru)
  - Seller เลือกสินค้าที่ต้องการให้รับรอง
  - ส่ง request พร้อมข้อความ
  - Guru approve/reject
- Endorsement Badge
  - แสดง badge บนสินค้าใน LIFF
  - Badge แสดงชื่อ/รูป Guru
  - Click ดูรายละเอียด Endorsement
- Filter & Search
  - Filter สินค้าที่ endorse แล้ว
  - Search ตาม Guru
- Endorsement Details
  - Video review จาก Guru
  - Comment/review text
  - Endorsement date & expiry

**Models Needed:**
- `product_endorsement.py` - endorsement records
- `endorsement_request.py` - request workflow
- `endorsement_badge.py` - badge configuration

---

### 4. Basic Analytics Dashboard
**Purpose:** วัดผล Endorsement ROI

**Requirements:**
- For Gurus:
  - จำนวนสินค้าที่รับรอง
  - ยอดขายรวมจากสินค้าที่รับรอง
  - Commission ที่ได้รับ
  - Engagement (views, clicks, shares)
- For Sellers:
  - ยอดขายก่อน/หลัง Endorsement
  - Traffic จาก content
  - Conversion rate
- For Admin:
  - Top performing Gurus
  - Top endorsed products
  - Total commission payouts

**Tracking:**
- UTM parameters จาก content
- Click tracking บน Endorsement badge
- Attribution window (30 days?)

**Views Needed:**
- Guru Dashboard (LIFF Seller)
- Seller Dashboard (ดูผล endorsement)
- Admin Report (platform-wide)

---

### 5. LINE OA Integration
**Purpose:** ใช้ LINE เป็นช่องทางหลักสำหรับ Endorsement

**Requirements:**
- Rich Menu สำหรับ Endorsement
  - ปุ่ม "สินค้าที่อาจารย์รับรอง"
  - ปุ่ม "ขอ Endorsement"
  - ปุ่ม "ดู Dashboard"
- LINE Broadcast จาก Gurus
  - แจ้งสินค้าใหม่ที่รับรอง
  - โปรโมชันพิเศษ
  - Live shopping announcement
- LINE Notifications
  - Notify Seller เมื่อ Guru approve endorsement
  - Notify Guru เมื่อมี request ใหม่
  - Notify เมื่อมี commission เข้า
- LINE Official Account per Guru (optional)
  - แต่ละ Guru มี OA ของตัวเอง
  - Fans สามารถ follow ได้
- LINE Chatbot Consultation
  - ถามคำถามเกี่ยวกับสินค้า
  - นัดหมายถ่ายทำ content

**Technical:**
- เชื่อมกับ `core_line_integration` module
- ใช้ LINE Messaging API
- LINE LIFF สำหรับ Dashboard

---

## 📋 Implementation Checklist

### Sprint 1: Foundation
- [ ] Create `council_shop` module structure
- [ ] Model: brand_ambassador, brand_ambassador_application
- [ ] Model: product_endorsement, endorsement_request
- [ ] Approval workflows
- [ ] Basic views (backend)

### Sprint 2: Commerce Integration
- [ ] Commission calculation logic
- [ ] Payout system (integrate with seller_wallet)
- [ ] Endorsement badge UI (LIFF)
- [ ] Filter endorsed products

### Sprint 3: LINE Integration
- [ ] Rich menu configuration
- [ ] LINE broadcast integration
- [ ] Notification triggers
- [ ] LIFF Dashboard for Gurus

### Sprint 4: Analytics & Launch
- [ ] Tracking system (UTM, clicks, attribution)
- [ ] Analytics dashboard
- [ ] Reports
- [ ] Testing & bug fixes
- [ ] Documentation

---

## 🚀 Success Metrics (KPIs)

| Metric | Target | Timeline |
|--------|--------|----------|
| Active Brand Ambassadors | 10 Gurus | Month 1 |
| Endorsed Products | 50 products | Month 1 |
| Sales Lift (endorsed vs non-endorsed) | +30% | Month 2 |
| Guru Retention Rate | 80% | Month 3 |
| Average Commission per Guru | ฿5,000/month | Month 3 |

---

## ⏸️ Deferred Features (Phase 3.2+)

- Gamification (Points, Leaderboard, Tiers)
- AI Content Generation (script, auto-post)
- Live Shopping (LINE Live)
- Community Features (Fan Clubs, UGC)
- Advanced Analytics (A/B testing, sentiment analysis)
- Content Production Management (booking, scheduling)
- Annual Awards Program

---

## 📝 Notes

- **Priority:** ทำ Sprint 1-2 ก่อน (Core system)
- **Integration:** ใช้ existing modules (core_marketplace, core_line_integration, seller_wallet)
- **Timeline:** MVP พร้อมใน 4-6 สัปดาห์
- **Budget:** เน้น Revenue Share เป็นหลัก (ไม่ต้องจ่ายล่วงหน้า)
