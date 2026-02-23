# /ui-review

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).

Review LIFF app UI/UX for mobile usability, Thai localization, and best practices.

## Usage

```
/ui-review buyer               # Review buyer app UI
/ui-review seller              # Review seller app UI
/ui-review admin               # Review admin app UI
/ui-review <page>              # Review specific page (e.g., "cart", "product-form")
```

## How It Works

```
┌─────────────────────────────────────────────────────┐
│                   UI REVIEW                          │
├─────────────────────────────────────────────────────┤
│  STANDALONE (always works)                           │
│  ✓ Review HTML/CSS/JS for mobile best practices      │
│  ✓ Check Thai label completeness                     │
│  ✓ Validate accessibility and touch targets          │
├─────────────────────────────────────────────────────┤
│  SUPERCHARGED (when ~~liff-app accessible)           │
│  + Scan actual HTML/CSS/JS source files              │
│  + Check responsive breakpoints                      │
│  + Verify loading states and error handling          │
│  + Validate cache busting (style.css?v=N)            │
│  + Identify hardcoded strings (missing Thai)         │
└─────────────────────────────────────────────────────┘
```

## UI/UX Checklist

| Category | Check | Priority |
|----------|-------|----------|
| **Mobile Layout** | Viewport meta tag set | Required |
| | Content fits 375px width without horizontal scroll | Required |
| | Touch targets >= 44x44px | Required |
| | No tiny text (min 14px body) | Required |
| **Thai Labels** | All buttons in Thai | Required |
| | All form labels in Thai | Required |
| | Error messages in Thai | Required |
| | Placeholder text in Thai | Recommended |
| **Button Size** | Primary actions >= 48px height | Required |
| | Sufficient spacing between buttons (8px+) | Required |
| | Clear visual hierarchy (primary/secondary) | Required |
| **Loading States** | Spinner shown during API calls | Required |
| | Button disabled during submission | Required |
| | Skeleton/placeholder while loading data | Recommended |
| **Error Handling** | Network error shown to user (Thai) | Required |
| | Form validation before submit | Required |
| | Retry option on failure | Recommended |
| **Cache Busting** | CSS: `style.css?v=N` updated on changes | Required |
| | JS: `app.js?v=N` updated on changes | Required |
| | API: `api.js?v=N` updated on changes | Required |

## App File Locations

| App | HTML | JS | CSS |
|-----|------|-----|-----|
| Buyer | `static/liff/index.html` | `static/liff/js/app.js` | `static/liff/css/style.css` |
| Seller | `static/liff_seller/index.html` | `static/liff_seller/js/app.js` | `static/liff_seller/css/style.css` |
| Admin | `static/liff_admin/index.html` | `static/liff_admin/js/app.js` | `static/liff_admin/css/style.css` |

## Design Standards

| Property | Value |
|----------|-------|
| Primary font | System default + NotoSansThai |
| Primary color (buyer) | Green (#28a745) |
| Primary color (seller) | Orange (#fd7e14) |
| Primary color (admin) | Dark blue (#1a237e) |
| Border radius | 8px (cards), 4px (inputs) |
| Card shadow | `0 2px 4px rgba(0,0,0,0.1)` |
| Spacing unit | 8px grid |

## Output

```markdown
## UI Review -- [app_name]

**App:** [buyer/seller/admin]
**Files Reviewed:** [count]
**Date:** [timestamp]

### Compliance
| Category | Pass | Fail | Notes |
|----------|------|------|-------|
| Mobile Layout | [n] | [n] | [details] |
| Thai Labels | [n] | [n] | [details] |
| Button Size | [n] | [n] | [details] |
| Loading States | [n] | [n] | [details] |
| Error Handling | [n] | [n] | [details] |
| Cache Busting | [n] | [n] | [details] |

### Issues Found
| Page | Issue | Severity | Fix |
|------|-------|----------|-----|
| [page] | [description] | high/medium/low | [suggested fix] |

### Recommendations
1. [Priority improvement]
2. [Priority improvement]
3. [Priority improvement]
```

## Next Steps

- Want me to fix the identified issues?
- Should I review a specific page in detail?
- Want me to check the responsive layout at different widths?

## Related Skills

- Uses [buyer-app](../skills/buyer-app/SKILL.md) for buyer UI patterns
- Uses [seller-app](../skills/seller-app/SKILL.md) for seller UI patterns
- Cross-references [line-integration](../../line-platform/CONNECTORS.md) for LIFF SDK usage
