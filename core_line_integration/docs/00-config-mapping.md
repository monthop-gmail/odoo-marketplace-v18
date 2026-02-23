# Configuration Mapping Guide

คู่มือการ mapping ค่า config ระหว่าง LINE Developers Console กับ Odoo

## สารบัญ

1. [ภาพรวม](#ภาพรวม)
2. [LINE → Odoo: ค่าที่ต้องนำมาใส่ใน Odoo](#line--odoo-ค่าที่ต้องนำมาใส่ใน-odoo)
3. [Odoo → LINE: ค่าที่ต้องนำไปใส่ใน LINE](#odoo--line-ค่าที่ต้องนำไปใส่ใน-line)
4. [ขั้นตอนการตั้งค่าตามลำดับ](#ขั้นตอนการตั้งค่าตามลำดับ)
5. [ตาราง Quick Reference](#ตาราง-quick-reference)

---

## ภาพรวม

```
┌─────────────────────────────────────────────────────────────────────┐
│                    LINE Developers Console                           │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │ Messaging API Channel                                        │    │
│  │  • Channel ID ─────────────────────────────┐                │    │
│  │  • Channel Secret ─────────────────────────┼──┐             │    │
│  │  • Channel Access Token ───────────────────┼──┼──┐          │    │
│  │  • Webhook URL ◄───────────────────────────┼──┼──┼────┐     │    │
│  └─────────────────────────────────────────────┼──┼──┼────┼────┘    │
│  ┌─────────────────────────────────────────────┼──┼──┼────┼────┐    │
│  │ LIFF App                                    │  │  │    │    │    │
│  │  • LIFF ID ────────────────────────────────┼──┼──┼──┐ │    │    │
│  │  • Endpoint URL ◄──────────────────────────┼──┼──┼──┼─┼─┐  │    │
│  └─────────────────────────────────────────────┼──┼──┼──┼─┼─┼──┘    │
└───────────────────────────────────────────────┼──┼──┼──┼─┼─┼────────┘
                                                │  │  │  │ │ │
                    ┌───────────────────────────┼──┼──┼──┼─┼─┼────────┐
                    │          ▼  ▼  ▼  ▼ │ │                         │
                    │  ┌────────────────────┼─┼──────────────────┐    │
                    │  │ LINE Channel (Odoo)│ │                  │    │
                    │  │  • Channel ID      │ │                  │    │
                    │  │  • Channel Secret  │ │                  │    │
                    │  │  • Access Token    │ │                  │    │
                    │  │  • Channel Code ───┼─┼──► Webhook URL   │    │
                    │  └────────────────────┼─┼──────────────────┘    │
                    │  ┌────────────────────┼─┼──────────────────┐    │
                    │  │ LIFF App (Odoo)    ▼ ▼                  │    │
                    │  │  • LIFF ID                              │    │
                    │  │  • Endpoint URL ────► LIFF Endpoint     │    │
                    │  └─────────────────────────────────────────┘    │
                    │                      Odoo Backend               │
                    └─────────────────────────────────────────────────┘

    ─────►  = ค่าจาก LINE นำมาใส่ใน Odoo
    ◄─────  = ค่าจาก Odoo นำไปใส่ใน LINE
```

---

## LINE → Odoo: ค่าที่ต้องนำมาใส่ใน Odoo

### 1. Channel Credentials (Messaging API)

**ที่มา:** LINE Developers Console > Channel > Basic settings / Messaging API

| ค่าจาก LINE | ใส่ที่ไหนใน Odoo | ตัวอย่าง |
|-------------|------------------|----------|
| **Channel ID** | Settings > LINE Marketplace > LINE Channels > **Channel ID** | `1234567890` |
| **Channel Secret** | Settings > LINE Marketplace > LINE Channels > **Channel Secret** | `abc123def456ghi789` |
| **Channel Access Token** | Settings > LINE Marketplace > LINE Channels > **Channel Access Token** | `eyJhbGciOiJIUzI1...` (ยาวมาก) |

#### วิธีหาค่าใน LINE Developers Console

```
LINE Developers Console
└── Your Provider
    └── Your Channel (Messaging API)
        ├── Basic settings
        │   ├── Channel ID: 1234567890        ← คัดลอกค่านี้
        │   └── Channel secret: abc123...     ← คัดลอกค่านี้
        │
        └── Messaging API
            └── Channel access token
                └── [Issue] ← คลิกเพื่อสร้าง token ใหม่
                    └── eyJhbGciOiJI...       ← คัดลอกค่านี้
```

### 2. LIFF ID

**ที่มา:** LINE Developers Console > Channel > LIFF

| ค่าจาก LINE | ใส่ที่ไหนใน Odoo | ตัวอย่าง |
|-------------|------------------|----------|
| **LIFF ID** | Settings > LINE Marketplace > LIFF Apps > **LIFF ID** | `1234567890-AbCdEfGh` |

#### วิธีหาค่าใน LINE Developers Console

```
LINE Developers Console
└── Your Provider
    └── Your Channel
        └── LIFF
            └── Your LIFF App
                └── LIFF ID: 1234567890-AbCdEfGh  ← คัดลอกค่านี้
```

---

## Odoo → LINE: ค่าที่ต้องนำไปใส่ใน LINE

### 1. Webhook URL

**ที่มา:** สร้างจาก Channel Code ใน Odoo

| ค่าจาก Odoo | ใส่ที่ไหนใน LINE | รูปแบบ |
|-------------|------------------|--------|
| **Webhook URL** | LINE Developers > Messaging API > Webhook URL | `https://{domain}/api/line-buyer/webhook/{channel_code}` |

#### วิธีสร้าง Webhook URL

```
สูตร: https://{your-domain}/api/line-buyer/webhook/{channel_code}

ตัวอย่าง:
├── Domain: shop.example.com
├── Channel Code (จาก Odoo): my_coop
└── Webhook URL: https://shop.example.com/api/line-buyer/webhook/my_coop
                 ▲
                 └── นำไปใส่ใน LINE Developers Console
```

#### ตั้งค่าใน LINE Developers Console

```
LINE Developers Console
└── Your Channel
    └── Messaging API
        └── Webhook settings
            ├── Webhook URL: https://shop.example.com/api/line-buyer/webhook/my_coop
            │                ▲
            │                └── วาง URL ที่นี่
            ├── Use webhook: [Enable] ← เปิด
            └── [Verify] ← คลิกทดสอบ
```

### 2. LIFF Endpoint URL

**ที่มา:** URL ของ LIFF frontend application

| ค่าจาก Odoo/Frontend | ใส่ที่ไหนใน LINE | รูปแบบ |
|---------------------|------------------|--------|
| **Endpoint URL** | LINE Developers > LIFF > Endpoint URL | `https://{domain}/line/liff/{type}` |

#### ตัวอย่าง Endpoint URLs

```
LIFF Type     Endpoint URL
─────────────────────────────────────────────────────
buyer         https://shop.example.com/line/liff/buyer
seller        https://shop.example.com/line/liff/seller
admin         https://shop.example.com/line/liff/admin
promotion     https://shop.example.com/line/liff/promotion
```

#### ตั้งค่าใน LINE Developers Console

```
LINE Developers Console
└── Your Channel
    └── LIFF
        └── Add / Edit LIFF app
            ├── LIFF app name: Buyer App
            ├── Size: Full
            ├── Endpoint URL: https://shop.example.com/line/liff/buyer
            │                 ▲
            │                 └── ใส่ URL ของ frontend app
            ├── Scope: ✓ profile, ✓ openid
            └── Bot link feature: Aggressive
```

---

## ขั้นตอนการตั้งค่าตามลำดับ

### Step 1: สร้าง Channel ใน LINE (รับค่า 3 ตัว)

```
┌─────────────────────────────────────────────────────────────┐
│  LINE Developers Console                                     │
│                                                              │
│  1. สร้าง Messaging API Channel                              │
│  2. จดบันทึกค่า:                                              │
│     ✓ Channel ID: 1234567890                                │
│     ✓ Channel Secret: abc123def456...                       │
│     ✓ Channel Access Token: eyJhbGci... (กด Issue)          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼ นำค่ามาใส่
┌─────────────────────────────────────────────────────────────┐
│  Odoo: Settings > LINE Marketplace > LINE Channels > Create       │
│                                                              │
│  Name: [ชื่อที่ต้องการ]                                       │
│  Code: [my_coop] ← สำคัญ! ใช้สร้าง Webhook URL               │
│  Channel ID: [1234567890]                                   │
│  Channel Secret: [abc123def456...]                          │
│  Channel Access Token: [eyJhbGci...]                        │
│                                                              │
│  [Save]                                                      │
└─────────────────────────────────────────────────────────────┘
```

### Step 2: ตั้งค่า Webhook URL (ส่งค่า 1 ตัวกลับ LINE)

```
┌─────────────────────────────────────────────────────────────┐
│  Odoo: LINE Channel record                                   │
│                                                              │
│  Webhook URL (auto-generated):                               │
│  https://shop.example.com/api/line-buyer/webhook/my_coop    │
│                    ▲                              ▲          │
│                    │                              │          │
│                 domain                      channel code     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼ คัดลอกไปใส่
┌─────────────────────────────────────────────────────────────┐
│  LINE Developers Console > Messaging API > Webhook settings │
│                                                              │
│  Webhook URL: https://shop.example.com/api/line-buyer/...   │
│  Use webhook: ✓ Enable                                      │
│                                                              │
│  [Verify] ← ต้องได้ Success                                  │
└─────────────────────────────────────────────────────────────┘
```

### Step 3: สร้าง LIFF App (รับค่า 1 ตัว, ส่งค่า 1 ตัว)

```
┌─────────────────────────────────────────────────────────────┐
│  LINE Developers Console > LIFF > Add                        │
│                                                              │
│  LIFF app name: Buyer App                                   │
│  Size: Full                                                  │
│  Endpoint URL: https://shop.example.com/line/liff/buyer     │
│                ▲                                             │
│                └── ค่าจาก Frontend/Odoo                       │
│  Scope: ✓ profile ✓ openid                                  │
│  Bot link feature: Aggressive                                │
│                                                              │
│  [Create] → LIFF ID: 1234567890-AbCdEfGh                    │
│                      ▲                                       │
│                      └── จดบันทึกค่านี้                        │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼ นำค่ามาใส่
┌─────────────────────────────────────────────────────────────┐
│  Odoo: Settings > LINE Marketplace > LIFF Apps > Create           │
│                                                              │
│  Name: Buyer LIFF                                           │
│  LIFF ID: [1234567890-AbCdEfGh] ← ค่าจาก LINE               │
│  Channel: [เลือก Channel ที่สร้างไว้]                         │
│  Type: Buyer                                                 │
│  Size: Full                                                  │
│                                                              │
│  [Save]                                                      │
└─────────────────────────────────────────────────────────────┘
```

---

## ตาราง Quick Reference

### ค่าจาก LINE → Odoo

| ลำดับ | ค่า | หาจาก LINE ที่ไหน | ใส่ใน Odoo ที่ไหน |
|------|-----|------------------|------------------|
| 1 | Channel ID | Basic settings > Channel ID | LINE Channels > Channel ID |
| 2 | Channel Secret | Basic settings > Channel secret | LINE Channels > Channel Secret |
| 3 | Channel Access Token | Messaging API > Issue token | LINE Channels > Channel Access Token |
| 4 | LIFF ID | LIFF > LIFF ID | LIFF Apps > LIFF ID |

### ค่าจาก Odoo → LINE

| ลำดับ | ค่า | สร้างจาก Odoo ที่ไหน | ใส่ใน LINE ที่ไหน |
|------|-----|---------------------|------------------|
| 1 | Webhook URL | `https://{domain}/api/line-buyer/webhook/{channel_code}` | Messaging API > Webhook URL |
| 2 | LIFF Endpoint URL | URL ของ frontend app | LIFF > Endpoint URL |

### Checklist

```
□ Step 1: LINE → Odoo
  □ คัดลอก Channel ID จาก LINE
  □ คัดลอก Channel Secret จาก LINE
  □ Issue และคัดลอก Channel Access Token จาก LINE
  □ สร้าง LINE Channel ใน Odoo พร้อมใส่ค่าทั้ง 3

□ Step 2: Odoo → LINE
  □ สร้าง Webhook URL จาก channel code
  □ ใส่ Webhook URL ใน LINE Developers
  □ Verify webhook ได้ Success

□ Step 3: LIFF (สองทาง)
  □ กำหนด Endpoint URL สำหรับ LIFF frontend
  □ ใส่ Endpoint URL ใน LINE Developers
  □ คัดลอก LIFF ID จาก LINE
  □ สร้าง LIFF record ใน Odoo พร้อมใส่ LIFF ID

□ Step 4: ทดสอบ
  □ Follow LINE OA → เห็น member ใหม่ใน Odoo
  □ เปิด LIFF app → แสดงหน้าร้านค้า
  □ สั่งซื้อ → ได้รับ notification ใน LINE
```

---

## Visual Summary

```
╔═══════════════════════════════════════════════════════════════════════════╗
║                         CONFIGURATION FLOW                                 ║
╠═══════════════════════════════════════════════════════════════════════════╣
║                                                                            ║
║   LINE Developers Console                    Odoo Backend                  ║
║   ───────────────────────                    ────────────                  ║
║                                                                            ║
║   ┌─────────────────────┐                    ┌─────────────────────┐      ║
║   │ Channel ID          │ ──────────────────►│ Channel ID          │      ║
║   │ 1234567890          │        ①           │                     │      ║
║   └─────────────────────┘                    └─────────────────────┘      ║
║                                                                            ║
║   ┌─────────────────────┐                    ┌─────────────────────┐      ║
║   │ Channel Secret      │ ──────────────────►│ Channel Secret      │      ║
║   │ abc123def456...     │        ②           │                     │      ║
║   └─────────────────────┘                    └─────────────────────┘      ║
║                                                                            ║
║   ┌─────────────────────┐                    ┌─────────────────────┐      ║
║   │ Access Token        │ ──────────────────►│ Access Token        │      ║
║   │ eyJhbGciOiJI...     │        ③           │                     │      ║
║   └─────────────────────┘                    └─────────────────────┘      ║
║                                                                            ║
║   ┌─────────────────────┐                    ┌─────────────────────┐      ║
║   │ Webhook URL         │ ◄──────────────────│ Channel Code        │      ║
║   │                     │        ④           │ my_coop             │      ║
║   │ https://xxx/api/    │    (สร้าง URL)     │     ↓               │      ║
║   │ line-buyer/webhook/ │                    │ Webhook URL:        │      ║
║   │ my_coop             │                    │ https://xxx/api/    │      ║
║   └─────────────────────┘                    │ line-buyer/webhook/ │      ║
║                                              │ my_coop             │      ║
║                                              └─────────────────────┘      ║
║                                                                            ║
║   ┌─────────────────────┐                    ┌─────────────────────┐      ║
║   │ LIFF ID             │ ──────────────────►│ LIFF ID             │      ║
║   │ 1234567890-AbCd...  │        ⑤           │                     │      ║
║   └─────────────────────┘                    └─────────────────────┘      ║
║                                                                            ║
║   ┌─────────────────────┐                    ┌─────────────────────┐      ║
║   │ LIFF Endpoint URL   │ ◄──────────────────│ Frontend App URL    │      ║
║   │                     │        ⑥           │                     │      ║
║   │ https://xxx/line/   │    (URL ของ app)   │ https://xxx/line/   │      ║
║   │ liff/buyer          │                    │ liff/buyer          │      ║
║   └─────────────────────┘                    └─────────────────────┘      ║
║                                                                            ║
║   ─────► = ค่าจาก LINE ไป Odoo (คัดลอกมา)                                  ║
║   ◄───── = ค่าจาก Odoo ไป LINE (สร้างแล้วนำไปใส่)                           ║
║                                                                            ║
╚═══════════════════════════════════════════════════════════════════════════╝
```

---

## ถัดไป

- [Setup Guide (รายละเอียดเพิ่มเติม)](./01-setup-guide.md)
- [API Reference](./02-api-reference.md)
- [Troubleshooting](./05-troubleshooting.md)
