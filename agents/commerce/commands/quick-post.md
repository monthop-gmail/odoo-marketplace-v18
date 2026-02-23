# /quick-post

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).

Mobile-first product posting -- the core UX principle of this marketplace.

## Usage

```
/quick-post                  # Review the quick post flow
/quick-post --improve        # Suggest UX improvements
/quick-post --debug          # Debug quick post issues
```

## Core Concept

```
เจอสินค้าข้างนอก → เปิด LINE OA → ถ่ายรูป → กรอกราคา → Post ทันที
```

**ยิ่งมีคนช่วย post → สินค้าเยอะ → Marketplace มีคุณค่า**

## How It Works

```
┌─────────────────────────────────────────────────────┐
│                   QUICK POST                         │
├─────────────────────────────────────────────────────┤
│  STANDALONE (always works)                           │
│  ✓ Design the quick post UX flow                     │
│  ✓ Review current implementation                     │
│  ✓ Suggest mobile-first improvements                 │
├─────────────────────────────────────────────────────┤
│  SUPERCHARGED (in ~~liff-app)                        │
│  + Camera/gallery image capture                      │
│  + Square crop + resize (1024px, JPEG 85%)           │
│  + Category selection (with auto-create)             │
│  + One-tap publish via ~~api                         │
│  + Staff can post to owner's shop                    │
└─────────────────────────────────────────────────────┘
```

## Minimum Required Fields

| Field | Required | Input Type |
|-------|----------|-----------|
| Photo | Yes | Camera / gallery (auto square crop) |
| Name | Yes | Text input |
| Price | Yes | Number input |
| Category | Yes | Dropdown (with `+ สร้างหมวดหมู่ใหม่`) |
| Description | No | Textarea (optional) |

## Image Processing Pipeline

```
Camera/Gallery → fileToBase64() → center-crop square → resize max 1024px → JPEG 85% → upload
```

## Staff Quick Post

| Role | Can Quick Post? | Whose Shop? |
|------|----------------|-------------|
| Owner | Yes | Own shop |
| Staff | Yes | Owner's shop (via context switch) |
| Buyer | No | Must apply as seller first |

## Current API Flow

```
POST /api/line-seller/products
Body: {
    "name": "สินค้าใหม่",
    "list_price": 299,
    "categ_id": 5,          // or categ_name: "หมวดใหม่"
    "image_1920": "base64...",
    "description": "optional"
}
→ Creates product.template with marketplace_seller_id = seller partner
```

## UX Principles

1. **Minimum taps** -- Photo → Name → Price → Category → Done
2. **Mobile-first** -- Big buttons, camera-ready, one-hand operation
3. **Forgiving** -- Can edit later, don't block on optional fields
4. **Fast** -- Image processed client-side, single API call

## Anti-Patterns

| Don't | Do Instead |
|-------|-----------|
| Require all fields upfront | Only photo + name + price + category |
| Upload raw camera images (5MB+) | Crop + resize + compress client-side |
| Force complex category trees | Flat dropdown + auto-create option |
| Block posting on slow connection | Show optimistic UI, retry on failure |

## Next Steps

- Want me to review the current quick post implementation?
- Should I optimize the image upload flow?
- Want to add batch product posting?

## Related Skills

- Uses [product-catalog](../skills/product-catalog/SKILL.md) for product creation
- Uses [buyer-app](../../liff-apps/skills/buyer-app/SKILL.md) for UI implementation
- Uses [staff-management](../../seller-engine/skills/staff-management/SKILL.md) for staff permission model
