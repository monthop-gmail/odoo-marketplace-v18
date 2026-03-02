# สภา shop - Development Progress

**Last Updated:** 2026-03-02

---

## ✅ Completed (Sprint 1 - Foundation)

### Module: core_ambassador
**Status:** ✅ Complete

**Files Created (28 files, +2,944 lines):**

#### Models
- ✅ `models/brand_ambassador.py` — res.partner extension (is_ambassador, tier, commission_rate)
- ✅ `models/ambassador_application.py` — Application workflow (draft → submitted → under_review → approved/rejected)
- ✅ `models/ambassador_specialty.py` — Expertise categories
- ✅ `models/product_endorsement.py` — Endorsement records
- ✅ `models/endorsement_request.py` — Request workflow

#### Controllers (APIs)
- ✅ `controllers/api_ambassador_apply.py` — Apply as ambassador
- ✅ `controllers/api_admin_ambassadors.py` — Admin management
- ✅ `controllers/api_ambassador_endorsements.py` — Ambassador manage endorsements
- ✅ `controllers/api_seller_endorsements.py` — Seller request endorsements
- ✅ `controllers/api_buyer_endorsements.py` — Buyer view endorsed products

#### Security
- ✅ `security/ambassador_security.xml` — Groups + record rules
- ✅ `security/ir.model.access.csv` — Access rights

#### Views (Backend)
- ✅ `views/ambassador_views.xml`
- ✅ `views/ambassador_application_views.xml`
- ✅ `views/product_endorsement_views.xml`
- ✅ `views/endorsement_request_views.xml`
- ✅ `views/ambassador_specialty_views.xml`
- ✅ `views/ambassador_menu_views.xml`

#### Data
- ✅ `data/ambassador_sequence_data.xml`
- ✅ `data/ambassador_specialty_data.xml`
- ✅ `data/ir_config_parameter_data.xml`

#### Configuration
- ✅ `__manifest__.py` — Depends: core_marketplace, core_line_integration
- ✅ Updated `CLAUDE.md` — Added core_ambassador section

---

## ⏸️ Pending (Sprint 2-4)

### Sprint 2: Commerce Integration
- [ ] Commission calculation logic
- [ ] Payout system (integrate with seller_wallet)
  - [ ] `models/endorsement_commission.py`
  - [ ] `models/endorsement_payout.py`
- [ ] Endorsement badge UI (LIFF)
- [ ] Filter endorsed products API

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

---

## 📋 Next Steps (เมื่อทำต่อ)

1. **ทดสอบ Module** — Install core_ambassador ใน Odoo
2. **สร้าง Test Data** — สมัคร Ambassador, ขอ Endorsement
3. **ทำ Sprint 2** — Commission & Payout
4. **ทำ Sprint 3** — LINE Integration
5. **ทำ Sprint 4** — Analytics & Testing

---

## 📝 Notes

- Module name: `core_ambassador` (ไม่ใช่ council_shop)
- Tier system: Bronze (5%), Silver (7%), Gold (10%)
- Status flow: `none → draft → pending → approved → (suspended)`
- APIs ใช้ prefix: `/api/line-buyer/ambassador/`, `/api/line-admin/ambassadors/`
