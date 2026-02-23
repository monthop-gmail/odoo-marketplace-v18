---
name: mobile-ux
description: Mobile-first UX patterns for LIFF Mini Apps. Activate when working on LIFF SDK integration, deep linking, responsive design, touch interactions, loading states, or mobile user experience optimization.
---

# Mobile UX (ประสบการณ์มือถือ)

You ensure all LIFF Mini Apps deliver a fast, native-feeling mobile experience inside LINE. Every interaction should feel like a native app, not a slow web page.

> If you see unfamiliar `~~category` placeholders, see [CONNECTORS.md](../../CONNECTORS.md).

## LIFF SDK Integration

### Initialization
```javascript
liff.init({ liffId: CONFIG.LIFF_ID }).then(() => {
    if (!liff.isLoggedIn()) liff.login();
    const profile = await liff.getProfile();
    // App is ready
});
```

### Deep Link Fix (sessionStorage)
LIFF SDK double-loads: first with `liff.state=?page%3Dprofile`, second reload with empty params.

```javascript
// BEFORE liff.init — save target page
const params = new URLSearchParams(window.location.search);
if (params.get('page')) sessionStorage.setItem('targetPage', params.get('page'));

// AFTER liff.init — restore and navigate
liff.init({ liffId }).then(() => {
    const page = sessionStorage.getItem('targetPage') || 'home';
    sessionStorage.removeItem('targetPage');
    navigateTo(page);
});
```

Applied to all 3 LIFF apps: buyer (app.js?v=7), seller (app.js?v=2), admin (app.js?v=2).

## Standalone vs Supercharged

| Feature | Standalone (Browser) | Supercharged (LINE) |
|---------|---------------------|---------------------|
| Auth | Mock `X-Line-User-Id` header | Real LIFF access token |
| Profile | Manual input | `liff.getProfile()` auto-fill |
| Deep links | URL params | ~~rich-menu LIFF URLs |
| Share | Copy link | `liff.shareTargetPicker()` |
| Notifications | None | ~~messaging push via LINE |
| Close app | Browser tab | `liff.closeWindow()` |

## UX Principles

### 1. Minimum Taps
- Quick Post: photo → price → category → done (4 taps)
- Add to cart: single "หยิบใส่ตะกร้า" button
- No unnecessary confirmation dialogs

### 2. Mobile-First Layout
- Single column, full-width cards
- Bottom navigation for primary actions
- Thumb-reachable action buttons (bottom 60% of screen)
- Minimum touch target: 44x44px

### 3. Fast Loading
- No heavy frameworks (vanilla JS only)
- Lazy load images below the fold
- Cache bust with `?v=N` on deploys
- Thai address data loaded on-demand (404KB)

### 4. Forgiving Input
- Auto-format phone numbers
- Cascading dropdowns reduce typing
- Camera-first for product images
- Reasonable defaults for optional fields

### 5. Thai-Native Feel
- All labels in Thai (ตะกร้า, สั่งซื้อ, โปรไฟล์)
- Thai currency format: ฿1,234.00
- Thai date format where applicable
- Respectful tone in messages (ครับ/ค่ะ)

## Loading States
- Skeleton screens for lists (not spinners)
- Inline loading for buttons (disable + "กำลังดำเนินการ...")
- Pull-to-refresh on list pages
- Toast notifications for success/error (auto-dismiss 3s)

## Anti-Patterns

| Don't | Do Instead |
|-------|-----------|
| Use alert()/confirm() dialogs | Custom toast or inline messages |
| Full page reload on action | SPA navigation with `navigateTo()` |
| Tiny tap targets | Minimum 44x44px touch area |
| Load everything upfront | Lazy load, paginate, defer |
| Ignore offline state | Show friendly "ไม่มีสัญญาณ" message |

## Cross-References
- [buyer-app](../buyer-app/SKILL.md) — Buyer shopping UX
- [seller-app](../seller-app/SKILL.md) — Seller posting UX
- [admin-app](../admin-app/SKILL.md) — Admin moderation UX
- [thai-localization](../thai-localization/SKILL.md) — Thai text and formatting
