# LINE OA Integration Documentation

เอกสารประกอบการใช้งาน LINE Official Account Integration สำหรับ core_line_integration module

## เอกสาร

| เอกสาร | คำอธิบาย |
|--------|---------|
| [00-config-mapping.md](./00-config-mapping.md) | **Mapping ค่า config ระหว่าง LINE ↔ Odoo** |
| [01-setup-guide.md](./01-setup-guide.md) | คู่มือการตั้งค่า LINE OA, LIFF, Webhook |
| [02-api-reference.md](./02-api-reference.md) | รายละเอียด REST API ทั้งหมด |
| [03-flex-messages.md](./03-flex-messages.md) | การสร้าง Flex Message |
| [04-rich-menu.md](./04-rich-menu.md) | การตั้งค่า Rich Menu |
| [05-troubleshooting.md](./05-troubleshooting.md) | แก้ปัญหาที่พบบ่อย |

## Quick Start

### 1. ตั้งค่า LINE Channel

```
Settings > LINE Marketplace > LINE Channels > Create

กรอก:
- Name: ชื่อ Channel
- Code: รหัสสำหรับ URL (เช่น my_coop)
- Channel ID: จาก LINE Developers
- Channel Secret: จาก LINE Developers
- Channel Access Token: จาก LINE Developers
```

### 2. ตั้งค่า Webhook

```
LINE Developers Console > Messaging API > Webhook settings

Webhook URL: https://your-domain.com/api/line-buyer/webhook/<channel_code>
Use webhook: Enable
```

### 3. ตั้งค่า LIFF

```
LINE Developers Console > LIFF > Add

LIFF app name: Buyer App
Size: Full
Endpoint URL: https://your-domain.com/line/liff/buyer
```

ลงทะเบียนใน Odoo:
```
Settings > LINE Marketplace > LIFF Apps > Create

LIFF ID: <from LINE Developers>
Channel: <your channel>
Type: Buyer
```

### 4. ทดสอบ

1. Add LINE OA เป็นเพื่อน
2. พิมพ์ "shop" เพื่อเปิด LIFF app
3. ทดสอบดูสินค้า, เพิ่มตะกร้า, สั่งซื้อ

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    LINE Platform                         │
├─────────────────────────────────────────────────────────┤
│  LINE OA  ←→  Messaging API  ←→  LIFF App               │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                    Odoo Backend                          │
├─────────────────────────────────────────────────────────┤
│  Webhook Handler  │  REST API  │  LINE Services         │
├───────────────────┼────────────┼────────────────────────┤
│  line.channel     │ Products   │ LineApiService         │
│  line.liff        │ Cart       │ FlexMessageBuilder     │
│  line.member      │ Orders     │ MockLineApiService     │
│  line.notify.log  │ Profile    │                        │
└─────────────────────────────────────────────────────────┘
```

## Key Features

### For Buyers (ผู้ซื้อ)
- ดูสินค้าผ่าน LINE
- เพิ่มลงตะกร้า / Wishlist
- สั่งซื้อและชำระเงิน
- ติดตามสถานะ order
- รับ notification ผ่าน LINE

### For Admins (ผู้ดูแล)
- จัดการ LINE Channels
- กำหนด LIFF Apps
- ออกแบบ Rich Menu
- ดู Notification Logs
- ดู Member Analytics

## API Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/line-buyer/products | รายการสินค้า |
| GET | /api/line-buyer/cart | ดูตะกร้า |
| POST | /api/line-buyer/cart/items | เพิ่มสินค้า |
| POST | /api/line-buyer/checkout/place-order | สั่งซื้อ |
| GET | /api/line-buyer/orders | ประวัติ orders |
| GET | /api/line-buyer/profile | โปรไฟล์ |

ดูรายละเอียดเพิ่มเติมใน [API Reference](./02-api-reference.md)

## Authentication

### Production (LIFF)
```
Authorization: Bearer <liff_access_token>
X-Channel-Code: <channel_code>
```

### Development (Mock Mode)
```
X-Line-User-Id: <line_user_id>
X-Channel-Code: <channel_code>
```

## Support

- [Troubleshooting Guide](./05-troubleshooting.md)
- LINE Developers Documentation: https://developers.line.biz/en/docs/
- Odoo Documentation: https://www.odoo.com/documentation/18.0/
