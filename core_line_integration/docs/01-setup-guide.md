# LINE OA Setup Guide

คู่มือการตั้งค่า LINE Official Account สำหรับ core_line_integration module

## สารบัญ

1. [ข้อกำหนดเบื้องต้น](#ข้อกำหนดเบื้องต้น)
2. [สร้าง LINE Official Account](#สร้าง-line-official-account)
3. [ตั้งค่า LINE Developers Console](#ตั้งค่า-line-developers-console)
4. [ตั้งค่าใน Odoo](#ตั้งค่าใน-odoo)
5. [ตั้งค่า LIFF App](#ตั้งค่า-liff-app)
6. [ตั้งค่า Webhook](#ตั้งค่า-webhook)
7. [ทดสอบการเชื่อมต่อ](#ทดสอบการเชื่อมต่อ)

---

## ข้อกำหนดเบื้องต้น

- Odoo 18 พร้อม module `core_line_integration` และ `core_marketplace`
- LINE Official Account (แนะนำ Verified Account สำหรับ production)
- Domain ที่มี HTTPS certificate (สำหรับ Webhook และ LIFF)
- สิทธิ์ Admin ใน Odoo

---

## สร้าง LINE Official Account

### ขั้นตอนที่ 1: สมัคร LINE Official Account

1. ไปที่ [LINE Official Account Manager](https://manager.line.biz/)
2. คลิก "Create a LINE Official Account"
3. กรอกข้อมูล:
   - ชื่อบัญชี (ชื่อสหกรณ์/ร้านค้า)
   - หมวดหมู่ธุรกิจ
   - ที่อยู่และข้อมูลติดต่อ
4. ยืนยันตัวตนตามที่ LINE กำหนด

### ขั้นตอนที่ 2: เลือกแผนบริการ

| แผน | ข้อความ/เดือน | ราคา | เหมาะสำหรับ |
|-----|--------------|------|-------------|
| Free | 500 | ฟรี | ทดสอบ/เริ่มต้น |
| Light | 4,000 | 300 บาท | ธุรกิจขนาดเล็ก |
| Standard | 25,000+ | ตามจำนวน | ธุรกิจขนาดกลาง-ใหญ่ |

---

## ตั้งค่า LINE Developers Console

### ขั้นตอนที่ 1: สร้าง Provider และ Channel

1. ไปที่ [LINE Developers Console](https://developers.line.biz/console/)
2. สร้าง Provider ใหม่ (หรือใช้ที่มีอยู่)
3. สร้าง **Messaging API Channel**:
   - Channel name: ชื่อ channel
   - Channel description: คำอธิบาย
   - Category: เลือกตามธุรกิจ
   - Email: email สำหรับติดต่อ

### ขั้นตอนที่ 2: รับ Credentials

เข้าไปที่ Channel ที่สร้าง และจดบันทึกข้อมูลต่อไปนี้:

```
Tab: Basic Settings
├── Channel ID: 1234567890
└── Channel Secret: abc123def456...

Tab: Messaging API
├── Channel Access Token: (คลิก Issue)
└── Webhook URL: (จะตั้งค่าภายหลัง)
```

### ขั้นตอนที่ 3: ตั้งค่า Messaging API

1. ไปที่ Tab "Messaging API"
2. **Use webhooks**: Enable
3. **Webhook redelivery**: Enable (แนะนำ)
4. **Allow bot to join groups**: ตามต้องการ
5. **Auto-reply messages**: Disable (ใช้ระบบของเรา)
6. **Greeting messages**: Disable (ใช้ระบบของเรา)

---

## ตั้งค่าใน Odoo

### ขั้นตอนที่ 1: เข้าถึง LINE Channel Settings

1. ไปที่ **Settings > LINE Marketplace > LINE Channels**
2. คลิก **Create** เพื่อสร้าง Channel ใหม่

### ขั้นตอนที่ 2: กรอกข้อมูล Channel

```
General Information:
├── Name: ชื่อ Channel (แสดงภายใน Odoo)
├── Code: รหัสย่อ เช่น "my_coop" (ใช้ใน URL)
├── Cooperative: เลือกสหกรณ์ที่เชื่อมโยง

LINE Credentials:
├── Channel ID: [จาก LINE Developers]
├── Channel Secret: [จาก LINE Developers]
└── Channel Access Token: [จาก LINE Developers]

Settings:
├── Auto Welcome Message: ✓
├── Welcome Message: "ยินดีต้อนรับสู่สหกรณ์..."
├── Notify on Order: ✓
└── Notify on Shipping: ✓
```

### ขั้นตอนที่ 3: บันทึกและทดสอบ

1. คลิก **Save**
2. คลิกปุ่ม **Test Connection** เพื่อทดสอบ credentials
3. ระบบจะแสดงข้อความยืนยันการเชื่อมต่อ

---

## ตั้งค่า LIFF App

### ขั้นตอนที่ 1: สร้าง LIFF App ใน LINE Developers

1. ไปที่ Channel ใน LINE Developers Console
2. Tab "LIFF" > คลิก "Add"
3. กรอกข้อมูล:

```
LIFF app name: Coop Buyer App
Size: Full (แนะนำ)
Endpoint URL: https://your-domain.com/line/liff/buyer
Scope: ✓ profile, ✓ openid
Bot link feature: Aggressive (แนะนำ)
```

4. บันทึก และจดบันทึก **LIFF ID** (เช่น `1234567890-AbCdEfGh`)

### ขั้นตอนที่ 2: ลงทะเบียน LIFF ใน Odoo

1. ไปที่ **Settings > LINE Marketplace > LIFF Apps**
2. คลิก **Create**
3. กรอกข้อมูล:

```
Name: Buyer LIFF
LIFF ID: 1234567890-AbCdEfGh
Channel: [เลือก Channel ที่สร้างไว้]
Type: Buyer
Size: Full

Features:
├── ✓ Browse Products
├── ✓ Shopping Cart
├── ✓ Checkout
├── ✓ Order History
└── ✓ Profile Management
```

### LIFF Types

| Type | ใช้สำหรับ |
|------|----------|
| buyer | ผู้ซื้อ - ดูสินค้า, สั่งซื้อ |
| seller | ผู้ขาย - จัดการร้านค้า |
| admin | แอดมิน - จัดการระบบ |
| promotion | โปรโมชั่น - แสดงโปรโมชั่น |
| support | ช่วยเหลือ - FAQ, ติดต่อ |
| other | อื่นๆ |

---

## ตั้งค่า Webhook

### ขั้นตอนที่ 1: กำหนด Webhook URL

Webhook URL สำหรับระบบนี้คือ:

```
https://your-domain.com/api/line-buyer/webhook/<channel_code>
```

ตัวอย่าง: ถ้า channel code คือ `my_coop`:
```
https://your-domain.com/api/line-buyer/webhook/my_coop
```

### ขั้นตอนที่ 2: ตั้งค่าใน LINE Developers

1. ไปที่ Channel > Tab "Messaging API"
2. Webhook settings:
   - **Webhook URL**: ใส่ URL ข้างต้น
   - **Use webhook**: Enable
   - **Webhook redelivery**: Enable

3. คลิก **Verify** เพื่อทดสอบ

### ขั้นตอนที่ 3: Events ที่รองรับ

| Event | การทำงาน |
|-------|---------|
| follow | สมาชิกใหม่ติดตาม → สร้าง member, ส่งข้อความต้อนรับ |
| unfollow | เลิกติดตาม → อัปเดตสถานะ |
| message | ข้อความเข้ามา → ตอบกลับตาม keyword |
| postback | กดปุ่ม → ดำเนินการตาม data |
| join | Bot เข้ากลุ่ม |
| leave | Bot ออกจากกลุ่ม |

---

## ทดสอบการเชื่อมต่อ

### ทดสอบ Webhook

1. เปิด LINE app
2. Add บัญชี LINE OA ที่ตั้งค่าไว้เป็นเพื่อน
3. ตรวจสอบใน Odoo:
   - ไปที่ **LINE Marketplace > Members**
   - ควรเห็น record ใหม่ที่สร้างจากการ follow

### ทดสอบ LIFF

1. ส่งข้อความ "shop" ใน LINE chat
2. ระบบจะตอบกลับพร้อมลิงก์ LIFF
3. คลิกลิงก์เพื่อเปิด LIFF app
4. ตรวจสอบว่า app โหลดถูกต้อง

### ทดสอบ Notification

1. สร้าง order ผ่าน LIFF app
2. ตรวจสอบว่าได้รับ LINE notification
3. ตรวจสอบใน **LINE Marketplace > Notification Logs**

---

## Mock Mode (สำหรับ Development)

ระบบรองรับ Mock Mode สำหรับการพัฒนาโดยไม่ต้องใช้ LINE credentials จริง

### เปิดใช้งาน Mock Mode

1. ไปที่ **Settings > LINE Marketplace**
2. เปิด **Mock Authentication Mode**
3. บันทึก

### ใช้งาน Mock Mode

```bash
# API Request with Mock Auth
curl -X GET "https://your-domain.com/api/line-buyer/products" \
  -H "X-Line-User-Id: test_user_001" \
  -H "X-Channel-Code: demo_coop"
```

### Mock Login Endpoint

```bash
POST /api/line-buyer/auth/mock/login

Request:
{
  "line_user_id": "test_user_001",
  "display_name": "Test User",
  "channel_code": "demo_coop"
}

Response:
{
  "success": true,
  "data": {
    "session_token": "abc123...",
    "expires_at": "2024-01-02T00:00:00Z"
  }
}
```

---

## Checklist

- [ ] สร้าง LINE Official Account
- [ ] สร้าง Messaging API Channel ใน LINE Developers
- [ ] Issue Channel Access Token
- [ ] สร้าง LINE Channel ใน Odoo
- [ ] ทดสอบ Connection
- [ ] สร้าง LIFF App ใน LINE Developers
- [ ] ลงทะเบียน LIFF ใน Odoo
- [ ] ตั้งค่า Webhook URL
- [ ] Verify Webhook
- [ ] ทดสอบ Follow event
- [ ] ทดสอบ LIFF app
- [ ] ทดสอบ Order notification

---

## ถัดไป

- [API Reference](./02-api-reference.md) - รายละเอียด REST API ทั้งหมด
- [Flex Messages](./03-flex-messages.md) - การสร้าง Flex Message
- [Rich Menu](./04-rich-menu.md) - การตั้งค่า Rich Menu
- [Troubleshooting](./05-troubleshooting.md) - แก้ปัญหาที่พบบ่อย
