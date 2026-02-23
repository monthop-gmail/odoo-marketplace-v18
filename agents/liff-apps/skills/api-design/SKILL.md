---
name: api-design
description: REST API design conventions for LIFF apps. Activate when working on API endpoints, request/response format, authentication, error handling, or controller patterns for buyer/seller/admin APIs.
---

# API Design (แบบแผน REST API)

You maintain the REST API conventions used by all LIFF Mini Apps. Every controller must follow these patterns for consistency and security.

> If you see unfamiliar `~~category` placeholders, see [CONNECTORS.md](../../CONNECTORS.md).

## Base URLs

| Role | Base URL | Endpoints | Controller Path |
|------|----------|-----------|-----------------|
| Buyer | `/api/line-buyer/` | 46 | `controllers/api_buyer_*.py` |
| Seller | `/api/line-seller/` | 28 | `controllers/api_seller_*.py` |
| Admin | `/api/line-admin/` | 23 | `controllers/api_admin_*.py` |
| **Total** | | **97** | |

## Authentication

### Production Mode (LIFF Token)
```
Authorization: Bearer <liff_access_token>
X-Channel-Code: <channel_code>
```

### Development Mock Mode
```
X-Line-User-Id: <line_user_id>
X-Channel-Code: <channel_code>
```

Auth is resolved by `@require_auth` decorator which sets `request.line_member` and `request.partner`.

## Critical Pattern: auth='none' + SUPERUSER_ID

All LIFF API routes use `auth='none'` because LINE users have no Odoo session. This creates a dangerous pattern:

```python
# WRONG — .sudo() sets su=True but env.user is STILL empty recordset
product = request.env['product.template'].sudo().create(vals)
# env.user.has_group() → ensure_one() CRASH

# CORRECT — explicitly set uid=1
from odoo import SUPERUSER_ID
product = request.env['product.template'].with_user(SUPERUSER_ID).create(vals)
# env.user = Administrator → has_group() works
```

**Rule**: Never use `.sudo()` in `auth='none'` controllers. Always use `.with_user(SUPERUSER_ID)`.

## Response Format

```json
// Success
{ "success": true, "data": { ... } }

// Error
{ "success": false, "error": { "code": "VALIDATION_ERROR", "message": "..." } }

// Paginated
{ "success": true, "data": { "items": [...], "total": 100, "page": 1, "per_page": 20 } }
```

## HTTP Methods

| Method | Usage | Idempotent |
|--------|-------|-----------|
| GET | Read data, list, search | Yes |
| POST | Create resource, trigger action | No |
| PUT | Update existing resource | Yes |
| DELETE | Remove resource | Yes |

## Error Codes

| Code | HTTP Status | When |
|------|-------------|------|
| NOT_FOUND | 404 | Resource does not exist |
| VALIDATION_ERROR | 400 | Missing/invalid fields |
| UNAUTHORIZED | 401 | Missing or invalid auth |
| FORBIDDEN | 403 | Insufficient role/permission |
| ALREADY_EXISTS | 409 | Duplicate resource |
| SERVER_ERROR | 500 | Unexpected exception |

## Seller API Auth Decorators

| Decorator | Effect |
|-----------|--------|
| `@require_auth` | Resolves LINE member + partner |
| `@require_seller` | + resolves seller partner (staff→owner context switch) |
| `@owner_only` | + blocks staff, owner access only |

## Anti-Patterns

| Don't | Do Instead |
|-------|-----------|
| Use `.sudo()` in auth='none' routes | `.with_user(SUPERUSER_ID)` always |
| Return raw Python exceptions | Catch and return structured error JSON |
| Mix buyer/seller/admin in one controller | Separate files per role |
| Skip pagination on list endpoints | Default per_page=20, accept page param |
| Use GET for state-changing operations | POST for create/action, PUT for update |

## Cross-References
- [buyer-app](../buyer-app/SKILL.md) — Buyer-facing endpoints
- [seller-app](../seller-app/SKILL.md) — Seller-facing endpoints
- [admin-app](../admin-app/SKILL.md) — Admin-facing endpoints
- [mobile-ux](../mobile-ux/SKILL.md) — Frontend consumption patterns
