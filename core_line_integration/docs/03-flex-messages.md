# Flex Message Guide

คู่มือการสร้างและใช้งาน Flex Message สำหรับ core_line_integration module

## สารบัญ

1. [ภาพรวม Flex Message](#ภาพรวม-flex-message)
2. [โครงสร้างพื้นฐาน](#โครงสร้างพื้นฐาน)
3. [การใช้ FlexMessageBuilder](#การใช้-flexmessagebuilder)
4. [Templates ที่มีอยู่](#templates-ที่มีอยู่)
5. [ตัวอย่างการสร้าง Flex Message](#ตัวอย่างการสร้าง-flex-message)
6. [Best Practices](#best-practices)
7. [Debugging](#debugging)

---

## ภาพรวม Flex Message

Flex Message คือรูปแบบข้อความที่ปรับแต่งได้อย่างยืดหยุ่นใน LINE โดยใช้ JSON structure คล้ายกับ CSS Flexbox

### ข้อดีของ Flex Message

- ออกแบบ layout ได้อิสระ
- รองรับรูปภาพ, ปุ่ม, ข้อความหลากหลายรูปแบบ
- แสดงผลสวยงามทั้งบน iOS และ Android
- รองรับ interactive actions

### ข้อจำกัด

- ขนาด Bubble สูงสุด 50KB
- Carousel สูงสุด 12 Bubbles
- altText จำเป็นสำหรับ notifications

---

## โครงสร้างพื้นฐาน

### Container Types

```
Flex Message
├── Bubble (ข้อความเดี่ยว)
│   ├── header (optional)
│   ├── hero (รูปภาพหลัก, optional)
│   ├── body (เนื้อหาหลัก)
│   └── footer (ปุ่มกด, optional)
│
└── Carousel (หลาย bubbles)
    ├── Bubble 1
    ├── Bubble 2
    └── ... (สูงสุด 12)
```

### Component Types

| Component | ใช้สำหรับ |
|-----------|----------|
| box | Container สำหรับจัดกลุ่ม components |
| text | แสดงข้อความ |
| image | แสดงรูปภาพ |
| button | ปุ่มกด |
| icon | ไอคอนขนาดเล็ก |
| separator | เส้นแบ่ง |
| spacer | ช่องว่าง |
| filler | ตัวเติมช่องว่าง (สำหรับ flexbox) |

### Action Types

| Action | การทำงาน |
|--------|---------|
| uri | เปิด URL |
| postback | ส่ง data กลับไปยัง webhook |
| message | ส่งข้อความแทนผู้ใช้ |
| datetimepicker | เลือกวันที่/เวลา |

---

## การใช้ FlexMessageBuilder

### Import

```python
from odoo.addons.core_line_integration.services.line_messaging import (
    FlexMessageBuilder,
    LineMessageBuilder,
    OrderNotificationTemplates
)
```

### สร้าง Text Component

```python
# Text ธรรมดา
text = FlexMessageBuilder.text_component("สวัสดีครับ")

# Text พร้อม styling
text = FlexMessageBuilder.text_component(
    "หัวข้อ",
    size="xl",       # xxs, xs, sm, md, lg, xl, xxl, 3xl, 4xl, 5xl
    weight="bold",   # regular, bold
    color="#333333",
    wrap=True,       # ตัดบรรทัดอัตโนมัติ
    align="center"   # start, center, end
)
```

### สร้าง Image Component

```python
image = FlexMessageBuilder.image_component(
    "https://example.com/image.jpg",
    aspectRatio="1:1",    # 1:1, 1.51:1, 1.91:1, 4:3, 16:9, 20:13
    aspectMode="cover",   # cover, fit
    size="full"           # xxs, xs, sm, md, lg, xl, full
)
```

### สร้าง Button Component

```python
# Button with URI action
button = FlexMessageBuilder.button(
    FlexMessageBuilder.uri_action("เปิดร้านค้า", "https://liff.line.me/xxx"),
    style="primary",   # primary, secondary, link
    color="#00B900",   # สีปุ่ม (primary/secondary only)
    height="sm"        # sm, md
)

# Button with Postback action
button = FlexMessageBuilder.button(
    FlexMessageBuilder.postback_action(
        "ดูรายละเอียด",
        "action=view_product&id=123",
        "ดูสินค้า #123"  # displayText (optional)
    ),
    style="secondary"
)
```

### สร้าง Box (Container)

```python
# Vertical layout
box = FlexMessageBuilder.box(
    "vertical",
    [
        FlexMessageBuilder.text_component("บรรทัด 1"),
        FlexMessageBuilder.text_component("บรรทัด 2"),
    ],
    spacing="md",        # none, xs, sm, md, lg, xl, xxl
    margin="lg",
    paddingAll="20px",
    backgroundColor="#FFFFFF"
)

# Horizontal layout
box = FlexMessageBuilder.box(
    "horizontal",
    [
        FlexMessageBuilder.text_component("ซ้าย", flex=1),
        FlexMessageBuilder.text_component("ขวา", flex=1, align="end"),
    ]
)

# Baseline layout (จัด baseline ของ text)
box = FlexMessageBuilder.box(
    "baseline",
    [
        FlexMessageBuilder.text_component("฿", size="sm"),
        FlexMessageBuilder.text_component("100", size="xxl", weight="bold"),
    ]
)
```

### สร้าง Bubble

```python
bubble = FlexMessageBuilder.bubble(
    header=FlexMessageBuilder.box("vertical", [
        FlexMessageBuilder.text_component("หัวข้อ", weight="bold", size="xl")
    ]),
    hero=FlexMessageBuilder.image_component(
        "https://example.com/image.jpg",
        aspectRatio="20:13",
        size="full"
    ),
    body=FlexMessageBuilder.box("vertical", [
        FlexMessageBuilder.text_component("ชื่อสินค้า", weight="bold", size="lg"),
        FlexMessageBuilder.text_component("฿100", color="#00B900", size="xl"),
    ]),
    footer=FlexMessageBuilder.box("vertical", [
        FlexMessageBuilder.button(
            FlexMessageBuilder.uri_action("ซื้อเลย", "https://..."),
            style="primary"
        )
    ]),
    styles={
        "header": {"backgroundColor": "#00B900"},
        "body": {"backgroundColor": "#FFFFFF"},
        "footer": {"backgroundColor": "#F5F5F5"}
    }
)
```

### สร้าง Carousel

```python
bubbles = [bubble1, bubble2, bubble3]
carousel = FlexMessageBuilder.carousel(bubbles)

# Wrap เป็น Flex Message
message = FlexMessageBuilder.flex_message(
    "รายการสินค้า",  # altText
    carousel
)
```

---

## Templates ที่มีอยู่

### OrderNotificationTemplates

#### Order Confirmation

```python
from odoo.addons.core_line_integration.services.line_messaging import OrderNotificationTemplates

# สร้าง order data
order_data = {
    "order_name": "SO00123",
    "date_order": "15/01/2024 10:30",
    "items": [
        {"name": "สินค้า A", "quantity": 2, "subtotal": 200.00},
        {"name": "สินค้า B", "quantity": 1, "subtotal": 150.00},
    ],
    "amount_total": 350.00,
    "shipping_address": "123/45 ถ.สุขุมวิท กรุงเทพฯ 10110"
}

message = OrderNotificationTemplates.order_confirmation(
    order_data,
    liff_url="https://liff.line.me/xxx"
)
```

**ตัวอย่างผลลัพธ์:**
```
┌─────────────────────────────┐
│  ✓ ยืนยันคำสั่งซื้อ         │
├─────────────────────────────┤
│ หมายเลข: SO00123            │
│ วันที่: 15/01/2024 10:30    │
│                             │
│ สินค้า A x2         ฿200    │
│ สินค้า B x1         ฿150    │
│ ─────────────────────────── │
│ รวมทั้งหมด          ฿350    │
│                             │
│ ที่อยู่จัดส่ง:              │
│ 123/45 ถ.สุขุมวิท...        │
├─────────────────────────────┤
│      [ดูรายละเอียด]         │
└─────────────────────────────┘
```

#### Shipping Notification

```python
message = OrderNotificationTemplates.shipping_notification(
    order_data={
        "order_name": "SO00123",
        "carrier_name": "Kerry Express"
    },
    tracking_number="TH1234567890",
    tracking_url="https://th.kerryexpress.com/track/TH1234567890"
)
```

#### Welcome Message

```python
message = OrderNotificationTemplates.welcome_message(
    channel_name="สหกรณ์ตัวอย่าง",
    liff_url="https://liff.line.me/xxx"
)
```

#### Product Carousel

```python
products = [
    {
        "id": 1,
        "name": "สินค้า A",
        "price": 100.00,
        "image_url": "https://...",
        "description": "รายละเอียด..."
    },
    # ... more products (max 10)
]

message = OrderNotificationTemplates.product_carousel(
    products,
    base_url="https://your-domain.com"
)
```

---

## ตัวอย่างการสร้าง Flex Message

### Product Card

```python
def create_product_card(product):
    """สร้าง Product Card Flex Message"""

    return FlexMessageBuilder.bubble(
        hero=FlexMessageBuilder.image_component(
            product['image_url'],
            aspectRatio="4:3",
            aspectMode="cover",
            size="full",
            action=FlexMessageBuilder.uri_action(
                "View",
                f"https://liff.line.me/xxx?product={product['id']}"
            )
        ),
        body=FlexMessageBuilder.box("vertical", [
            # ชื่อสินค้า
            FlexMessageBuilder.text_component(
                product['name'],
                weight="bold",
                size="lg",
                wrap=True
            ),
            # ราคา
            FlexMessageBuilder.box("baseline", [
                FlexMessageBuilder.text_component(
                    "฿",
                    size="sm",
                    color="#00B900"
                ),
                FlexMessageBuilder.text_component(
                    f"{product['price']:,.0f}",
                    size="xl",
                    weight="bold",
                    color="#00B900"
                ),
            ], margin="md"),
            # รายละเอียด
            FlexMessageBuilder.text_component(
                product.get('description', ''),
                size="sm",
                color="#888888",
                wrap=True,
                margin="md"
            ),
        ], spacing="sm"),
        footer=FlexMessageBuilder.box("vertical", [
            FlexMessageBuilder.button(
                FlexMessageBuilder.postback_action(
                    "เพิ่มลงตะกร้า",
                    f"action=add_to_cart&product_id={product['id']}",
                    "เพิ่มสินค้าลงตะกร้า"
                ),
                style="primary",
                color="#00B900"
            ),
            FlexMessageBuilder.button(
                FlexMessageBuilder.uri_action(
                    "ดูรายละเอียด",
                    f"https://liff.line.me/xxx?product={product['id']}"
                ),
                style="secondary",
                margin="sm"
            ),
        ], spacing="sm")
    )
```

### Order Status Card

```python
def create_order_status_card(order):
    """สร้าง Order Status Flex Message"""

    status_colors = {
        'pending': '#FFA500',
        'processing': '#1E90FF',
        'shipped': '#00B900',
        'delivered': '#00B900',
        'cancelled': '#FF0000'
    }

    status_labels = {
        'pending': 'รอดำเนินการ',
        'processing': 'กำลังจัดเตรียม',
        'shipped': 'จัดส่งแล้ว',
        'delivered': 'ส่งถึงแล้ว',
        'cancelled': 'ยกเลิก'
    }

    color = status_colors.get(order['status'], '#888888')
    label = status_labels.get(order['status'], order['status'])

    contents = [
        # Header
        FlexMessageBuilder.text_component(
            f"คำสั่งซื้อ {order['name']}",
            weight="bold",
            size="lg"
        ),
        FlexMessageBuilder.separator(margin="md"),
        # Status
        FlexMessageBuilder.box("horizontal", [
            FlexMessageBuilder.text_component("สถานะ:", size="sm", color="#888888"),
            FlexMessageBuilder.text_component(
                label,
                size="sm",
                weight="bold",
                color=color,
                align="end"
            ),
        ], margin="md"),
    ]

    # Tracking info (if shipped)
    if order.get('tracking_number'):
        contents.append(
            FlexMessageBuilder.box("horizontal", [
                FlexMessageBuilder.text_component("เลขพัสดุ:", size="sm", color="#888888"),
                FlexMessageBuilder.text_component(
                    order['tracking_number'],
                    size="sm",
                    align="end"
                ),
            ], margin="sm")
        )

    # Total
    contents.extend([
        FlexMessageBuilder.separator(margin="md"),
        FlexMessageBuilder.box("horizontal", [
            FlexMessageBuilder.text_component("ยอดรวม", weight="bold"),
            FlexMessageBuilder.text_component(
                f"฿{order['amount_total']:,.2f}",
                weight="bold",
                color="#00B900",
                align="end"
            ),
        ], margin="md"),
    ])

    return FlexMessageBuilder.bubble(
        body=FlexMessageBuilder.box("vertical", contents, spacing="sm"),
        footer=FlexMessageBuilder.box("vertical", [
            FlexMessageBuilder.button(
                FlexMessageBuilder.uri_action(
                    "ดูรายละเอียด",
                    f"https://liff.line.me/xxx/orders/{order['id']}"
                ),
                style="primary"
            ),
        ])
    )
```

### Quick Reply Buttons

```python
def create_quick_reply_message(text):
    """สร้างข้อความพร้อม Quick Reply"""

    return LineMessageBuilder.text(
        text,
        quick_reply=LineMessageBuilder.quick_reply([
            LineMessageBuilder.quick_reply_action("ดูสินค้า", "action=browse"),
            LineMessageBuilder.quick_reply_action("ตะกร้า", "action=cart"),
            LineMessageBuilder.quick_reply_action("คำสั่งซื้อ", "action=orders"),
            LineMessageBuilder.quick_reply_message("ติดต่อเรา", "ติดต่อ"),
        ])
    )
```

---

## Best Practices

### 1. altText ที่ดี

```python
# ไม่ดี
message = FlexMessageBuilder.flex_message("message", bubble)

# ดี
message = FlexMessageBuilder.flex_message(
    "ยืนยันคำสั่งซื้อ SO00123 - ฿350",
    bubble
)
```

### 2. รองรับ Thai Text

```python
# ใช้ wrap=True สำหรับข้อความยาว
text = FlexMessageBuilder.text_component(
    "สินค้าคุณภาพดีจากเกษตรกรไทย",
    wrap=True,
    maxLines=2  # จำกัดจำนวนบรรทัด
)
```

### 3. ขนาดภาพที่เหมาะสม

```python
# Hero image - ใช้ 20:13 หรือ 1.91:1
hero = FlexMessageBuilder.image_component(url, aspectRatio="20:13")

# Product thumbnail - ใช้ 1:1 หรือ 4:3
thumb = FlexMessageBuilder.image_component(url, aspectRatio="1:1")
```

### 4. ปุ่มที่ชัดเจน

```python
# Primary action - ใช้สีเขียว LINE
FlexMessageBuilder.button(action, style="primary", color="#00B900")

# Secondary action - ไม่ต้องมีสี
FlexMessageBuilder.button(action, style="secondary")
```

### 5. ตรวจสอบขนาด

```python
import json

def check_bubble_size(bubble):
    """ตรวจสอบขนาด bubble (ต้อง < 50KB)"""
    json_str = json.dumps(bubble, ensure_ascii=False)
    size_kb = len(json_str.encode('utf-8')) / 1024
    print(f"Bubble size: {size_kb:.2f} KB")
    return size_kb < 50
```

---

## Debugging

### ใช้ LINE Flex Message Simulator

1. ไปที่ [LINE Flex Message Simulator](https://developers.line.biz/flex-message-simulator/)
2. Copy JSON ของ Flex Message
3. Paste และดู preview

### Log Flex Message

```python
import json
import logging

_logger = logging.getLogger(__name__)

def send_flex_message(channel, user_id, flex_content):
    # Log สำหรับ debug
    _logger.info("Sending Flex Message: %s",
                 json.dumps(flex_content, ensure_ascii=False, indent=2))

    # ส่งข้อความ
    line_service = LineApiService(channel.channel_access_token)
    line_service.push_message(user_id, [flex_content])
```

### ตรวจสอบใน Notification Log

1. ไปที่ **LINE Marketplace > Notification Logs**
2. ดู `flex_json` field
3. ดู `api_response` สำหรับ error จาก LINE

---

## ถัดไป

- [Rich Menu](./04-rich-menu.md) - การตั้งค่า Rich Menu
- [Troubleshooting](./05-troubleshooting.md) - แก้ปัญหาที่พบบ่อย
