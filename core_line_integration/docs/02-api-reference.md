# API Reference

เอกสารอ้างอิง REST API สำหรับ core_line_integration module

## สารบัญ

1. [ภาพรวม](#ภาพรวม)
2. [Authentication](#authentication)
3. [Products API](#products-api)
4. [Cart API](#cart-api)
5. [Checkout API](#checkout-api)
6. [Orders API](#orders-api)
7. [Profile API](#profile-api)
8. [Address API](#address-api)
9. [Wishlist API](#wishlist-api)
10. [Compare API](#compare-api)
11. [Webhook](#webhook)

---

## ภาพรวม

### Base URL

```
Production: https://your-domain.com/api/line-buyer
Development: http://localhost:8069/api/line-buyer
```

### Response Format

**Success Response:**
```json
{
  "success": true,
  "data": { ... },
  "message": "Optional success message"
}
```

**Error Response:**
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable error message"
  }
}
```

### CORS Headers

ทุก response จะมี headers:
```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization, X-Line-User-Id, X-Channel-Code
```

---

## Authentication

### Production Mode (LIFF)

ใช้ LIFF Access Token ที่ได้จาก `liff.getAccessToken()`

```http
Authorization: Bearer <liff_access_token>
X-Channel-Code: <channel_code>
```

### Mock Mode (Development)

สำหรับการพัฒนา เมื่อเปิด Mock Mode:

```http
X-Line-User-Id: <line_user_id>
X-Channel-Code: <channel_code>
```

### Mock Login

สร้าง session token สำหรับ development:

```http
POST /api/line-buyer/auth/mock/login
Content-Type: application/json

{
  "line_user_id": "U1234567890abcdef",
  "display_name": "Test User",
  "channel_code": "demo_coop"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "session_token": "eyJ0eXAi...",
    "line_user_id": "U1234567890abcdef",
    "display_name": "Test User",
    "channel": {
      "code": "demo_coop",
      "name": "Demo Cooperative"
    },
    "expires_at": "2024-01-02T12:00:00Z"
  }
}
```

---

## Products API

### List Products

```http
GET /api/line-buyer/products
```

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| page | int | 1 | หน้าที่ต้องการ |
| limit | int | 20 | จำนวนต่อหน้า (max: 100) |
| category_id | int | - | กรองตามหมวดหมู่ |
| seller_id | int | - | กรองตามร้านค้า |
| search | string | - | ค้นหาชื่อสินค้า |
| sort | string | name | เรียงตาม: name, list_price, create_date |
| order | string | asc | ลำดับ: asc, desc |

**Response:**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "name": "สินค้าตัวอย่าง",
        "list_price": 100.00,
        "description": "รายละเอียดสินค้า",
        "image_url": "https://...",
        "category": {
          "id": 1,
          "name": "หมวดหมู่"
        },
        "seller": {
          "id": 1,
          "name": "ร้านค้า"
        },
        "qty_available": 50,
        "is_in_wishlist": false
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total_items": 100,
      "total_pages": 5,
      "has_next": true,
      "has_prev": false
    }
  }
}
```

### Get Product Detail

```http
GET /api/line-buyer/products/<product_id>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "สินค้าตัวอย่าง",
    "list_price": 100.00,
    "description": "รายละเอียดสินค้า",
    "description_sale": "คำอธิบายการขาย",
    "image_url": "https://...",
    "images": [
      {"id": 1, "url": "https://..."},
      {"id": 2, "url": "https://..."}
    ],
    "category": {"id": 1, "name": "หมวดหมู่"},
    "seller": {"id": 1, "name": "ร้านค้า"},
    "qty_available": 50,
    "uom": "ชิ้น",
    "is_in_wishlist": false,
    "attributes": [
      {"name": "สี", "values": ["แดง", "น้ำเงิน"]},
      {"name": "ขนาด", "values": ["S", "M", "L"]}
    ]
  }
}
```

### List Categories

```http
GET /api/line-buyer/categories
```

**Response:**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "name": "อาหารและเครื่องดื่ม",
        "parent_id": null,
        "product_count": 25
      },
      {
        "id": 2,
        "name": "ผักสด",
        "parent_id": 1,
        "product_count": 10
      }
    ]
  }
}
```

### Get Products by Category

```http
GET /api/line-buyer/categories/<category_id>/products
```

รับ parameters เดียวกับ List Products

---

## Cart API

### Get Cart

```http
GET /api/line-buyer/cart
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 123,
    "items": [
      {
        "line_id": 1,
        "product_id": 10,
        "product_name": "สินค้า A",
        "product_image": "https://...",
        "quantity": 2,
        "price_unit": 100.00,
        "price_subtotal": 200.00
      }
    ],
    "amount_untaxed": 200.00,
    "amount_tax": 14.00,
    "amount_total": 214.00,
    "item_count": 1
  }
}
```

### Add to Cart

```http
POST /api/line-buyer/cart/items
Content-Type: application/json

{
  "product_id": 10,
  "quantity": 1
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "line_id": 1,
    "product_id": 10,
    "quantity": 1,
    "price_subtotal": 100.00
  },
  "message": "เพิ่มสินค้าลงตะกร้าแล้ว"
}
```

### Update Cart Item

```http
PUT /api/line-buyer/cart/items/<line_id>
Content-Type: application/json

{
  "quantity": 3
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "line_id": 1,
    "quantity": 3,
    "price_subtotal": 300.00
  }
}
```

### Remove Cart Item

```http
DELETE /api/line-buyer/cart/items/<line_id>
```

**Response:**
```json
{
  "success": true,
  "message": "ลบสินค้าออกจากตะกร้าแล้ว"
}
```

### Clear Cart

```http
POST /api/line-buyer/cart/clear
```

**Response:**
```json
{
  "success": true,
  "message": "ล้างตะกร้าแล้ว"
}
```

---

## Checkout API

### Place Order

```http
POST /api/line-buyer/checkout/place-order
Content-Type: application/json

{
  "shipping_address_id": 5,
  "note": "หมายเหตุเพิ่มเติม"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "order_id": 456,
    "order_name": "SO00123",
    "amount_total": 214.00,
    "state": "sale"
  },
  "message": "สั่งซื้อสำเร็จ"
}
```

---

## Orders API

### List Orders

```http
GET /api/line-buyer/orders
```

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| page | int | 1 | หน้าที่ต้องการ |
| limit | int | 20 | จำนวนต่อหน้า |
| state | string | - | กรองตามสถานะ: draft, sale, done, cancel |

**Response:**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 456,
        "name": "SO00123",
        "date_order": "2024-01-15T10:30:00Z",
        "state": "sale",
        "state_label": "Sales Order",
        "amount_total": 214.00,
        "item_count": 2,
        "shipping_status": "pending"
      }
    ],
    "pagination": { ... }
  }
}
```

### Get Order Detail

```http
GET /api/line-buyer/orders/<order_id>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 456,
    "name": "SO00123",
    "date_order": "2024-01-15T10:30:00Z",
    "state": "sale",
    "state_label": "Sales Order",
    "shipping_status": "shipped",
    "tracking_number": "TH1234567890",
    "lines": [
      {
        "id": 1,
        "product_id": 10,
        "product_name": "สินค้า A",
        "product_image": "https://...",
        "quantity": 2,
        "price_unit": 100.00,
        "price_subtotal": 200.00
      }
    ],
    "shipping_address": {
      "name": "สมชาย ใจดี",
      "phone": "0891234567",
      "street": "123/45 ถ.สุขุมวิท",
      "city": "กรุงเทพฯ",
      "zip": "10110"
    },
    "amount_untaxed": 200.00,
    "amount_tax": 14.00,
    "amount_total": 214.00
  }
}
```

---

## Profile API

### Get Profile

```http
GET /api/line-buyer/profile
```

**Response:**
```json
{
  "success": true,
  "data": {
    "line_user_id": "U1234567890abcdef",
    "display_name": "สมชาย",
    "picture_url": "https://profile.line-scdn.net/...",
    "channel": {
      "code": "demo_coop",
      "name": "Demo Cooperative"
    },
    "registration_state": "verified",
    "partner": {
      "id": 100,
      "name": "สมชาย ใจดี",
      "email": "somchai@email.com",
      "phone": "0891234567",
      "street": "123/45 ถ.สุขุมวิท",
      "city": "กรุงเทพฯ",
      "zip": "10110"
    },
    "preferences": {
      "notify_orders": true,
      "notify_promotions": false
    },
    "stats": {
      "order_count": 5,
      "total_spent": 2500.00
    }
  }
}
```

### Update Profile

```http
PUT /api/line-buyer/profile
Content-Type: application/json

{
  "name": "สมชาย ใจดี",
  "email": "somchai@email.com",
  "phone": "0891234567",
  "notify_orders": true,
  "notify_promotions": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "อัปเดตโปรไฟล์แล้ว"
}
```

---

## Address API

### List Addresses

```http
GET /api/line-buyer/addresses
```

**Response:**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 5,
        "name": "บ้าน",
        "recipient_name": "สมชาย ใจดี",
        "phone": "0891234567",
        "street": "123/45 ถ.สุขุมวิท",
        "street2": "แขวงคลองตัน",
        "city": "เขตคลองเตย",
        "state_id": {"id": 1, "name": "กรุงเทพมหานคร"},
        "zip": "10110",
        "is_default": true
      }
    ]
  }
}
```

### Create Address

```http
POST /api/line-buyer/addresses
Content-Type: application/json

{
  "name": "ที่ทำงาน",
  "recipient_name": "สมชาย ใจดี",
  "phone": "0891234567",
  "street": "999 อาคาร ABC ชั้น 10",
  "street2": "แขวงสีลม",
  "city": "เขตบางรัก",
  "state_id": 1,
  "zip": "10500",
  "is_default": false
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 6,
    "name": "ที่ทำงาน"
  },
  "message": "เพิ่มที่อยู่แล้ว"
}
```

### Update Address

```http
PUT /api/line-buyer/addresses/<address_id>
Content-Type: application/json

{
  "phone": "0899999999"
}
```

### Delete Address

```http
DELETE /api/line-buyer/addresses/<address_id>
```

### Set Default Address

```http
POST /api/line-buyer/addresses/<address_id>/set-default
```

### List Provinces (Thailand)

```http
GET /api/line-buyer/provinces
```

**Response:**
```json
{
  "success": true,
  "data": {
    "items": [
      {"id": 1, "name": "กรุงเทพมหานคร", "code": "BKK"},
      {"id": 2, "name": "เชียงใหม่", "code": "CNX"},
      ...
    ]
  }
}
```

---

## Wishlist API

### List Wishlist

```http
GET /api/line-buyer/wishlist
```

**Query Parameters:**
- `page` (int): หน้าที่ต้องการ
- `limit` (int): จำนวนต่อหน้า

**Response:**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "product_id": 10,
        "product_name": "สินค้า A",
        "product_image": "https://...",
        "price_when_added": 120.00,
        "current_price": 100.00,
        "price_dropped": true,
        "added_date": "2024-01-10T08:00:00Z"
      }
    ],
    "pagination": { ... }
  }
}
```

### Add to Wishlist

```http
POST /api/line-buyer/wishlist/<product_id>
```

### Remove from Wishlist

```http
DELETE /api/line-buyer/wishlist/<product_id>
```

### Get Price Dropped Items

```http
GET /api/line-buyer/wishlist/price-dropped
```

---

## Compare API

### Get Compare List

```http
GET /api/line-buyer/compare
```

**Response:**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 10,
        "name": "สินค้า A",
        "price": 100.00,
        "image_url": "https://...",
        "category": "หมวดหมู่",
        "attributes": {
          "สี": "แดง",
          "ขนาด": "M"
        }
      },
      {
        "id": 11,
        "name": "สินค้า B",
        "price": 120.00,
        "image_url": "https://...",
        "category": "หมวดหมู่",
        "attributes": {
          "สี": "น้ำเงิน",
          "ขนาด": "L"
        }
      }
    ],
    "comparison_matrix": {
      "สี": {"10": "แดง", "11": "น้ำเงิน"},
      "ขนาด": {"10": "M", "11": "L"},
      "ราคา": {"10": 100.00, "11": 120.00}
    },
    "max_items": 4
  }
}
```

### Add to Compare

```http
POST /api/line-buyer/compare/add/<product_id>
```

### Remove from Compare

```http
DELETE /api/line-buyer/compare/remove/<product_id>
```

### Clear Compare List

```http
POST /api/line-buyer/compare/clear
```

---

## Webhook

### Webhook URL

```
POST /api/line-buyer/webhook/<channel_code>
```

### Signature Validation

ทุก request จาก LINE จะมี header:
```
X-Line-Signature: <signature>
```

Signature คำนวณจาก:
```
signature = Base64(HMAC-SHA256(channel_secret, request_body))
```

### Event Types

#### Follow Event
```json
{
  "type": "follow",
  "replyToken": "xxx",
  "source": {
    "type": "user",
    "userId": "U1234567890abcdef"
  }
}
```

#### Message Event
```json
{
  "type": "message",
  "replyToken": "xxx",
  "source": {
    "type": "user",
    "userId": "U1234567890abcdef"
  },
  "message": {
    "type": "text",
    "text": "shop"
  }
}
```

#### Postback Event
```json
{
  "type": "postback",
  "replyToken": "xxx",
  "source": {
    "type": "user",
    "userId": "U1234567890abcdef"
  },
  "postback": {
    "data": "action=view_order&order_id=123"
  }
}
```

### Supported Keywords

| Keyword | Response |
|---------|----------|
| help | แสดงคำสั่งที่ใช้ได้ |
| shop | ลิงก์ไปหน้าร้านค้า (LIFF) |
| cart | ลิงก์ไปตะกร้าสินค้า |
| orders | ลิงก์ไปประวัติการสั่งซื้อ |
| hello, hi, สวัสดี | ข้อความทักทาย |

---

## Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| UNAUTHORIZED | 401 | ไม่ได้ login หรือ token หมดอายุ |
| FORBIDDEN | 403 | ไม่มีสิทธิ์เข้าถึง |
| NOT_FOUND | 404 | ไม่พบข้อมูล |
| VALIDATION_ERROR | 400 | ข้อมูลไม่ถูกต้อง |
| CART_EMPTY | 400 | ตะกร้าว่างเปล่า |
| PRODUCT_NOT_AVAILABLE | 400 | สินค้าไม่พร้อมขาย |
| INSUFFICIENT_STOCK | 400 | สินค้าไม่เพียงพอ |
| INTERNAL_ERROR | 500 | ข้อผิดพลาดภายในระบบ |

---

## Rate Limits

- API requests: 100 requests/minute ต่อ user
- Webhook: ไม่จำกัด (แต่ต้องตอบกลับภายใน 20 วินาที)

---

## ถัดไป

- [Flex Messages](./03-flex-messages.md) - การสร้าง Flex Message
- [Rich Menu](./04-rich-menu.md) - การตั้งค่า Rich Menu
- [Troubleshooting](./05-troubleshooting.md) - แก้ปัญหาที่พบบ่อย
