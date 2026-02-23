---
name: seller-onboarding
description: Seller registration and welcome flow. Activate when working on the seller application form, required documents, welcome messages, or first-time seller guidance.
---

# Seller Onboarding (การสมัครผู้ขาย)

You manage the seller onboarding experience — from the application form through document verification to the welcome flow after approval.

> If you see unfamiliar `~~category` placeholders, see [CONNECTORS.md](../../CONNECTORS.md).

## Application Requirements

| Field | Required | Validation |
|-------|----------|-----------|
| Full name | Yes | Non-empty |
| Phone number | Yes | Thai format |
| Email | Yes | Valid email |
| ID document | Yes | File uploaded |
| Bank account | Recommended | For withdrawals |
| Shop name | Yes | Non-empty |

## Onboarding Steps

1. **Apply** — Buyer fills application form in LIFF
2. **Submit Documents** — Upload required verification docs
3. **Wait for Review** — Status: pending
4. **Approval** — Officer approves → full side-effect chain
5. **Welcome** — Push notification + guide to first product post

## Welcome Flow (post-approval)

1. LINE push: "ยินดีต้อนรับสู่การเป็นผู้ขาย!"
2. Rich menu switches to seller menu
3. LIFF shows seller dashboard
4. Prompt to post first product (Quick Post)

## API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/line-buyer/seller/apply` | POST | Submit application |
| `/api/line-buyer/seller/apply/status` | GET | Check application status |

## Owned Files

| File | Purpose |
|------|---------|
| `core_line_integration/controllers/api_seller_apply.py` | Application API |
| `core_marketplace/edi/seller_creation_mail_*.xml` | Email templates |

## Critical Pattern

Application API uses `auth='none'` routes — always use `.with_user(SUPERUSER_ID)` not `.sudo()`.

## Cross-References

- → [seller-lifecycle](../seller-lifecycle/SKILL.md) — Status transitions
- → [liff-apps/buyer-app](../../liff-apps/skills/buyer-app/SKILL.md) — Application form UI
- → [line-platform/notification-triggers](../../line-platform/skills/notification-triggers/SKILL.md) — Welcome notifications
