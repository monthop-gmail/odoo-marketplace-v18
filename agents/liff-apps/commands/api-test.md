# /api-test

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).

Test REST API endpoints for buyer, seller, or admin APIs.

## Usage

```
/api-test buyer                  # Test all buyer API endpoints
/api-test seller                 # Test all seller API endpoints
/api-test admin                  # Test all admin API endpoints
/api-test <url>                  # Test specific endpoint URL
/api-test --auth <line_user_id>  # Test with specific user context
```

## How It Works

```
┌─────────────────────────────────────────────────────┐
│                   API TEST                           │
├─────────────────────────────────────────────────────┤
│  STANDALONE (always works)                           │
│  ✓ List available endpoints by API group             │
│  ✓ Show expected request/response formats            │
│  ✓ Generate curl examples for testing                │
├─────────────────────────────────────────────────────┤
│  SUPERCHARGED (when ~~api accessible)                │
│  + Execute actual API calls against Odoo             │
│  + Validate response format and data                 │
│  + Test auth flow (LIFF token / dev mock)            │
│  + Report endpoint health status                     │
│  + Identify broken or misconfigured endpoints        │
└─────────────────────────────────────────────────────┘
```

## API Groups

| Group | Base URL | Endpoints | Auth |
|-------|----------|-----------|------|
| Buyer | `/api/line-buyer/` | 46 endpoints | LIFF token / mock |
| Seller | `/api/line-seller/` | 28 endpoints | LIFF token / mock (seller role) |
| Admin | `/api/line-admin/` | 23 endpoints | LIFF token / mock (officer/manager) |

## Dev Mock Authentication

```bash
# Dev mock headers (local testing only)
curl -X GET "http://localhost:8069/api/line-buyer/products" \
  -H "X-Line-User-Id: Ud6c41147b7c7d919baf065ca5c7f5d95" \
  -H "X-Channel-Code: YOUR_CHANNEL_CODE" \
  -H "Content-Type: application/json"
```

## Production Authentication

```bash
# LIFF token authentication
curl -X GET "https://your-domain.com/api/line-buyer/products" \
  -H "Authorization: Bearer <liff_access_token>" \
  -H "X-Channel-Code: YOUR_CHANNEL_CODE" \
  -H "Content-Type: application/json"
```

## Expected Response Format

```json
{
    "success": true,
    "data": { ... },
    "error": null
}
```

## Common Test Scenarios

| Scenario | Endpoint | Method | Expected |
|----------|----------|--------|----------|
| List products | `/api/line-buyer/products` | GET | 200, product list |
| Get cart | `/api/line-buyer/cart` | GET | 200, cart items |
| Add to cart | `/api/line-buyer/cart/add` | POST | 200, updated cart |
| Seller dashboard | `/api/line-seller/dashboard` | GET | 200, stats |
| Create product | `/api/line-seller/products` | POST | 200, product created |
| Pending sellers | `/api/line-admin/sellers/pending` | GET | 200, seller list |

## Output

```markdown
## API Test Results

**Target:** [buyer/seller/admin or specific URL]
**Auth:** [mock user: line_user_id]
**Date:** [timestamp]

### Endpoint Health
| Endpoint | Method | Status | Time | Response |
|----------|--------|--------|------|----------|
| /api/line-buyer/products | GET | 200 OK | [ms] | [n] products |
| /api/line-buyer/cart | GET | 200 OK | [ms] | [n] items |
| /api/line-seller/dashboard | GET | 200 OK | [ms] | Valid |

### Summary
| Status | Count |
|--------|-------|
| Passing | [n] |
| Failing | [n] |
| Skipped | [n] |

### Failures (if any)
| Endpoint | Error | Expected | Got |
|----------|-------|----------|-----|
| [url] | [error] | [expected] | [actual] |
```

## Next Steps

- Want me to test a specific endpoint in detail?
- Should I test with a different user context?
- Want to see the full endpoint documentation?

## Related Skills

- Uses [buyer-app](../skills/buyer-app/SKILL.md) for buyer API endpoints
- Uses [seller-app](../skills/seller-app/SKILL.md) for seller API endpoints
- Cross-references [line-integration](../../line-platform/CONNECTORS.md) for auth flow
