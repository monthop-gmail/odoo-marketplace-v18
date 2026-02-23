# /liff-deploy

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).

Deploy or check status of LIFF mini apps.

## Usage

```
/liff-deploy buyer            # Deploy buyer LIFF app
/liff-deploy seller           # Deploy seller LIFF app
/liff-deploy admin            # Deploy admin LIFF app
/liff-deploy --status          # Show all app deployment status
```

## How It Works

```
┌─────────────────────────────────────────────────────┐
│                  LIFF DEPLOY                         │
├─────────────────────────────────────────────────────┤
│  STANDALONE (always works)                           │
│  ✓ Show current LIFF app status and versions         │
│  ✓ Review app configuration and endpoints            │
│  ✓ Validate LIFF ID registration                     │
├─────────────────────────────────────────────────────┤
│  SUPERCHARGED (when ~~liff-app accessible)           │
│  + Verify static files are served correctly          │
│  + Check API endpoint connectivity                   │
│  + Validate LIFF SDK initialization                  │
│  + Update cache-busting version parameters           │
│  + Register/update LIFF ID in line.liff model        │
└─────────────────────────────────────────────────────┘
```

## App Status

| App | Path | Status | Completion |
|-----|------|--------|-----------|
| Buyer | `static/liff/` | Deployed | 100% |
| Seller | `static/liff_seller/` | Deployed | 100% |
| Admin | `static/liff_admin/` | Deployed | 100% |
| Promotion | `static/liff_promotion/` | Stub | 5% (no models, no API, no JS) |
| Support | `static/liff_support/` | Stub | 5% (no models, no API, no JS) |

## LIFF App Structure

```
static/liff*/
├── index.html          # Main HTML (single page)
├── js/
│   ├── app.js          # Main application logic
│   ├── api.js          # API client wrapper
│   └── thai-address-data.js  # (buyer only) cascading address
├── css/
│   └── style.css       # Styles
└── img/                # Static images
```

## LIFF Configuration

| Setting | Value |
|---------|-------|
| LIFF Size | Full |
| Endpoint URL | `https://[domain]/core_line_integration/static/liff*/index.html` |
| Scope | profile, openid |
| Bot link | Aggressive |

## Deep Link Pattern

```
line://app/[LIFF_ID]?page=products
    → sessionStorage saves target page
    → liff.init() completes
    → app reads sessionStorage and navigates
```

## Deployment Checklist

| Check | Description |
|-------|-------------|
| HTML loads | index.html accessible via browser |
| LIFF init | `liff.init()` succeeds with correct LIFF ID |
| API connectivity | Test endpoint returns valid JSON |
| Auth flow | LIFF token or dev mock header works |
| Cache bust | CSS/JS version params updated (style.css?v=N) |
| Deep links | Page parameter routing works |

## Output

```markdown
## LIFF Deployment Status

**Date:** [timestamp]

### App Status
| App | URL | Version | LIFF ID | Status |
|-----|-----|---------|---------|--------|
| Buyer | /static/liff/ | app.js?v=[n] | [liff_id] | OK/ERROR |
| Seller | /static/liff_seller/ | app.js?v=[n] | [liff_id] | OK/ERROR |
| Admin | /static/liff_admin/ | app.js?v=[n] | [liff_id] | OK/ERROR |

### Deployment Actions
| Action | App | Result |
|--------|-----|--------|
| [Updated/Verified] | [app] | [details] |
```

## Next Steps

- Want me to check a specific app's API connectivity?
- Should I update cache-busting versions?
- Want to start building the Promotion or Support app?

## Related Skills

- Uses [buyer-app](../skills/buyer-app/SKILL.md) for buyer LIFF
- Uses [seller-app](../skills/seller-app/SKILL.md) for seller LIFF
- Cross-references [line-integration](../../line-platform/CONNECTORS.md) for LIFF registration
