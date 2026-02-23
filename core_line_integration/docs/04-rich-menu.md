# Rich Menu Configuration Guide

คู่มือการสร้างและจัดการ Rich Menu สำหรับ LINE Official Account

## สารบัญ

1. [ภาพรวม Rich Menu](#ภาพรวม-rich-menu)
2. [ข้อกำหนดรูปภาพ](#ข้อกำหนดรูปภาพ)
3. [สร้าง Rich Menu ใน Odoo](#สร้าง-rich-menu-ใน-odoo)
4. [กำหนด Tap Areas](#กำหนด-tap-areas)
5. [Action Types](#action-types)
6. [การจัดการ Rich Menu](#การจัดการ-rich-menu)
7. [Rich Menu ต่อผู้ใช้](#rich-menu-ต่อผู้ใช้)
8. [Best Practices](#best-practices)

---

## ภาพรวม Rich Menu

Rich Menu คือเมนูที่แสดงด้านล่างของหน้าจอ chat ใน LINE ช่วยให้ผู้ใช้เข้าถึงฟังก์ชันต่างๆ ได้ง่าย

### ข้อดี

- เพิ่ม engagement กับผู้ใช้
- นำทางไปยังฟีเจอร์สำคัญได้ง่าย
- ปรับแต่งได้ตามต้องการ
- เปลี่ยน Rich Menu ต่อผู้ใช้ได้

### ข้อจำกัด

- รูปภาพต้องตรงตาม specification
- มี action types จำกัด
- ไม่รองรับ animation

---

## ข้อกำหนดรูปภาพ

### ขนาดรูปภาพ

| Size | ความกว้าง x สูง | ใช้สำหรับ |
|------|-----------------|----------|
| Full | 2500 x 1686 px | แสดงแบบเต็ม |
| Half | 2500 x 843 px | แสดงแบบครึ่งจอ |

### รูปแบบไฟล์

- **Format:** JPEG หรือ PNG
- **File size:** ไม่เกิน 1 MB
- **Color mode:** RGB

### Template Layouts

#### Full Size (2500 x 1686)

```
┌─────────────────────────────────────┐
│         2500 x 1686 pixels          │
├─────────┬─────────┬─────────────────┤
│    1    │    2    │        3        │  843px
├─────────┼─────────┼─────────────────┤
│    4    │    5    │        6        │  843px
└─────────┴─────────┴─────────────────┘
   833px     833px       834px
```

#### Half Size (2500 x 843)

```
┌─────────┬─────────┬─────────────────┐
│    1    │    2    │        3        │  843px
└─────────┴─────────┴─────────────────┘
   833px     833px       834px
```

---

## สร้าง Rich Menu ใน Odoo

### ขั้นตอนที่ 1: เตรียมรูปภาพ

1. ออกแบบรูปภาพตามขนาดที่กำหนด
2. แบ่งพื้นที่สำหรับแต่ละปุ่ม
3. บันทึกเป็น JPEG หรือ PNG

### ขั้นตอนที่ 2: สร้าง Rich Menu Record

1. ไปที่ **Settings > LINE Marketplace > Rich Menus**
2. คลิก **Create**
3. กรอกข้อมูล:

```
General:
├── Name: Main Menu
├── Channel: [เลือก LINE Channel]
├── Size: Full (2500x1686) หรือ Half (2500x843)
├── Chat Bar Text: "เมนู" (ข้อความแสดงบน menu bar)
└── Selected: ✓ (เปิดเมนูเป็นค่าเริ่มต้น)

Image:
└── อัปโหลดรูปภาพ Rich Menu
```

### ขั้นตอนที่ 3: บันทึก

คลิก **Save** เพื่อบันทึก (ยังไม่อัปโหลดไป LINE)

---

## กำหนด Tap Areas

Tap Areas คือพื้นที่ที่ผู้ใช้แตะได้บน Rich Menu

### เพิ่ม Tap Area

1. ใน Rich Menu record คลิก **Add a line** ในส่วน Areas
2. กรอกข้อมูล:

```
Area Definition:
├── Name: ปุ่มร้านค้า
├── X: 0 (ตำแหน่งซ้าย)
├── Y: 0 (ตำแหน่งบน)
├── Width: 833
└── Height: 843

Action:
├── Action Type: LIFF
├── LIFF App: [เลือก Buyer LIFF]
└── (หรือกำหนด action อื่น)
```

### ตัวอย่าง Layout 6 ปุ่ม

```python
# Full Size: 2500 x 1686
areas = [
    # Row 1
    {"name": "ร้านค้า",   "x": 0,    "y": 0,   "width": 833,  "height": 843},
    {"name": "หมวดหมู่", "x": 833,  "y": 0,   "width": 833,  "height": 843},
    {"name": "โปรโมชั่น", "x": 1666, "y": 0,   "width": 834,  "height": 843},
    # Row 2
    {"name": "ตะกร้า",   "x": 0,    "y": 843, "width": 833,  "height": 843},
    {"name": "คำสั่งซื้อ", "x": 833,  "y": 843, "width": 833,  "height": 843},
    {"name": "โปรไฟล์",  "x": 1666, "y": 843, "width": 834,  "height": 843},
]
```

### Coordinate System

```
(0,0) ─────────────────────────────► X (width)
  │
  │    ┌────────────────┐
  │    │                │
  │    │   Tap Area     │
  │    │                │
  │    └────────────────┘
  │
  ▼
  Y (height)
```

---

## Action Types

### 1. URI Action

เปิด URL ภายนอกหรือ Deep link

```
Action Type: URI
URI: https://example.com
```

### 2. Message Action

ส่งข้อความแทนผู้ใช้

```
Action Type: Message
Text: "ดูสินค้าใหม่"
```

### 3. Postback Action

ส่ง data กลับมายัง webhook (ผู้ใช้ไม่เห็น)

```
Action Type: Postback
Data: action=view_promotions
Display Text: "ดูโปรโมชั่น" (optional - แสดงใน chat)
```

### 4. LIFF Action

เปิด LIFF App

```
Action Type: LIFF
LIFF App: [เลือกจาก dropdown]
```

### 5. Rich Menu Switch

สลับไปยัง Rich Menu อื่น

```
Action Type: Rich Menu Switch
Target Rich Menu: [เลือก Rich Menu]
```

### สรุป Action Types

| Action | Use Case |
|--------|----------|
| URI | เปิดเว็บไซต์, Deep link |
| Message | คำสั่งง่ายๆ เช่น "help", "สินค้า" |
| Postback | Actions ที่ต้องการ track/process |
| LIFF | เปิด Mini App |
| Rich Menu Switch | เปลี่ยนเมนู |

---

## การจัดการ Rich Menu

### อัปโหลดไป LINE

1. เปิด Rich Menu record
2. คลิก **Create on LINE**
3. รอจนสถานะเปลี่ยนเป็น "Uploaded"

### ตั้งเป็น Default

1. คลิก **Set as Default**
2. Rich Menu นี้จะแสดงให้ผู้ใช้ทุกคนที่ยังไม่ได้กำหนด Rich Menu เฉพาะ

### ลบจาก LINE

1. คลิก **Delete from LINE**
2. Rich Menu จะถูกลบออกจาก LINE (record ใน Odoo ยังอยู่)

### States

| State | คำอธิบาย |
|-------|---------|
| Draft | ยังไม่ได้อัปโหลด |
| Uploaded | อัปโหลดแล้ว แต่ไม่ได้ใช้งาน |
| Active | ใช้งานอยู่ (เป็น default หรือ assigned ให้ users) |
| Archived | เก็บถาวร |

---

## Rich Menu ต่อผู้ใช้

สามารถกำหนด Rich Menu ที่แตกต่างกันให้ผู้ใช้แต่ละคนได้

### Use Cases

- **ผู้ใช้ทั่วไป:** เมนูดูสินค้า, สั่งซื้อ
- **สมาชิก VIP:** เมนูพิเศษพร้อมโปรโมชั่น
- **ผู้ขาย:** เมนูจัดการร้านค้า

### กำหนดผ่าน Odoo

```
Rich Menu record:
├── Target Type: Specific Users
└── Target Members: [เลือกสมาชิก]
```

### กำหนดผ่าน Code

```python
from odoo.addons.core_line_integration.services.line_api import LineApiService

def assign_rich_menu(channel, line_user_id, rich_menu_id):
    """กำหนด Rich Menu ให้ผู้ใช้"""
    service = LineApiService(channel.channel_access_token)
    service.set_user_rich_menu(line_user_id, rich_menu_id)
```

### ลบ Rich Menu ของผู้ใช้

```python
def unlink_rich_menu(channel, line_user_id):
    """ยกเลิก Rich Menu ของผู้ใช้ (กลับไปใช้ default)"""
    service = LineApiService(channel.channel_access_token)
    service.unlink_user_rich_menu(line_user_id)
```

---

## Best Practices

### 1. ออกแบบที่ชัดเจน

```
✓ ไอคอนที่เข้าใจง่าย
✓ ข้อความสั้น กระชับ
✓ สีที่ contrast ดี
✓ ขนาดปุ่มที่แตะง่าย (อย่างน้อย 44x44 dp)
```

### 2. จัดลำดับความสำคัญ

```
ตำแหน่งซ้ายบน → ความสำคัญสูงสุด
┌─────────┬─────────┬─────────┐
│    1    │    2    │    3    │
├─────────┼─────────┼─────────┤
│    4    │    5    │    6    │
└─────────┴─────────┴─────────┘
```

### 3. รองรับมือถือ

- ทดสอบบนหน้าจอหลายขนาด
- ตรวจสอบว่าข้อความอ่านง่าย
- ตรวจสอบ tap targets ไม่เล็กเกินไป

### 4. ใช้ Postback สำหรับ Analytics

```
# แทนที่จะใช้ Message
action_type = "message"
text = "สินค้า"

# ใช้ Postback เพื่อ track
action_type = "postback"
data = "action=view_products&source=rich_menu"
display_text = "ดูสินค้า"
```

### 5. เตรียม Rich Menu หลายแบบ

```
1. Main Menu - สำหรับผู้ใช้ทั่วไป
2. Member Menu - สำหรับสมาชิก (เพิ่มปุ่มสิทธิพิเศษ)
3. Seller Menu - สำหรับผู้ขาย (จัดการร้าน, ดูยอดขาย)
4. Promotion Menu - ช่วงโปรโมชั่น (เน้นปุ่มโปรโมชั่น)
```

---

## ตัวอย่าง Rich Menu Configuration

### E-commerce Menu (Full Size)

```python
rich_menu_config = {
    "name": "E-commerce Main Menu",
    "size": "full",  # 2500 x 1686
    "chat_bar_text": "เมนู",
    "selected": True,
    "areas": [
        {
            "name": "ร้านค้า",
            "bounds": {"x": 0, "y": 0, "width": 833, "height": 843},
            "action": {
                "type": "liff",
                "liff_id": "1234567890-AbCdEfGh"
            }
        },
        {
            "name": "หมวดหมู่",
            "bounds": {"x": 833, "y": 0, "width": 833, "height": 843},
            "action": {
                "type": "postback",
                "data": "action=categories",
                "displayText": "ดูหมวดหมู่"
            }
        },
        {
            "name": "โปรโมชั่น",
            "bounds": {"x": 1666, "y": 0, "width": 834, "height": 843},
            "action": {
                "type": "uri",
                "uri": "https://liff.line.me/xxx/promotions"
            }
        },
        {
            "name": "ตะกร้า",
            "bounds": {"x": 0, "y": 843, "width": 833, "height": 843},
            "action": {
                "type": "liff",
                "liff_id": "1234567890-AbCdEfGh",
                "uri": "https://your-domain.com/liff/cart"
            }
        },
        {
            "name": "คำสั่งซื้อ",
            "bounds": {"x": 833, "y": 843, "width": 833, "height": 843},
            "action": {
                "type": "postback",
                "data": "action=orders",
                "displayText": "ดูคำสั่งซื้อ"
            }
        },
        {
            "name": "โปรไฟล์",
            "bounds": {"x": 1666, "y": 843, "width": 834, "height": 843},
            "action": {
                "type": "liff",
                "liff_id": "1234567890-AbCdEfGh",
                "uri": "https://your-domain.com/liff/profile"
            }
        }
    ]
}
```

---

## Troubleshooting

### Rich Menu ไม่แสดง

1. ตรวจสอบว่า Create on LINE สำเร็จ
2. ตรวจสอบว่า Set as Default แล้ว
3. ลอง unfollow และ follow ใหม่
4. ตรวจสอบ LINE app version

### รูปภาพไม่ชัด

1. ใช้รูปขนาดถูกต้อง (2500x1686 หรือ 2500x843)
2. ใช้ไฟล์ PNG สำหรับข้อความ/ไอคอน
3. ตรวจสอบว่าไฟล์ไม่เกิน 1MB

### Tap Area ไม่ตรงตำแหน่ง

1. ตรวจสอบ coordinate (x, y, width, height)
2. ใช้ [Rich Menu Simulator](https://developers.line.biz/console/) ทดสอบ
3. ตรวจสอบว่า areas ไม่ทับซ้อนกัน

---

## ถัดไป

- [Troubleshooting](./05-troubleshooting.md) - แก้ปัญหาที่พบบ่อย
