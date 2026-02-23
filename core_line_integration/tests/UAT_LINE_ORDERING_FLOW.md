# UAT: LINE Marketplace Ordering Flow
# ทดสอบ Flow การสั่งซื้อสินค้าผ่าน LINE API

**Version:** 1.0
**Module:** core_line_integration
**Base URL:** `http://localhost:8076`
**API Base:** `/api/line-buyer`

---

## Prerequisites (ข้อกำหนดเบื้องต้น)

- [ ] Odoo server running on port 8076
- [ ] LINE Channel "demo_coop" configured in Settings
- [ ] Mock mode enabled (ไม่ต้องใช้ LINE credentials จริง)
- [ ] มีสินค้าอย่างน้อย 2 รายการในระบบ
- [ ] มี Product Category อย่างน้อย 1 หมวดหมู่

---

## Test Data (ข้อมูลทดสอบ)

| Field | Value |
|-------|-------|
| Test User ID | `Utest_20260128120000` |
| Display Name | `ผู้ทดสอบ LINE` |
| Channel Code | `demo_coop` |
| Test Phone | `0812345678` |
| Test Address | `123 ถนนทดสอบ` |

---

## UAT Test Cases

### Step 1: Authentication (เข้าสู่ระบบ)

| Test ID | UAT-001 |
|---------|---------|
| **Test Case** | Mock Login - เข้าสู่ระบบด้วย LINE User ID |
| **Precondition** | Server running, Mock mode enabled |

#### วิธีทดสอบ (Test Steps)

| Step | Action | Input/URL |
|------|--------|-----------|
| 1.1 | เปิด API Testing Tool (Postman/curl) | - |
| 1.2 | สร้าง POST request | `POST /api/line-buyer/auth/mock/login` |
| 1.3 | ตั้ง Header | `Content-Type: application/json` |
| 1.4 | ใส่ Body (JSON) | ```{"line_user_id": "Utest_001", "display_name": "ผู้ทดสอบ LINE", "channel_code": "demo_coop"}``` |
| 1.5 | กด Send | - |

#### ผลที่คาดหวัง (Expected Results)

| Check | Expected |
|-------|----------|
| HTTP Status | `200 OK` |
| Response.success | `true` |
| Response.data.session_token | ได้รับ token (string ยาว) |
| Response.data.line_user_id | `Utest_001` |
| Response.data.display_name | `ผู้ทดสอบ LINE` |
| Response.data.channel.code | `demo_coop` |
| Odoo Log | `[INFO] LINE mock login: Utest_001` |

#### ตัวอย่าง Response สำเร็จ
```json
{
  "success": true,
  "data": {
    "session_token": "abc123xyz...",
    "line_user_id": "Utest_001",
    "display_name": "ผู้ทดสอบ LINE",
    "channel": {
      "code": "demo_coop",
      "name": "Demo Coop Channel"
    }
  }
}
```

---

### Step 2: Browse Products (ดูรายการสินค้า)

| Test ID | UAT-002a |
|---------|----------|
| **Test Case** | Get Categories - ดูหมวดหมู่สินค้า |

#### วิธีทดสอบ

| Step | Action | Input/URL |
|------|--------|-----------|
| 2.1 | สร้าง GET request | `GET /api/line-buyer/categories` |
| 2.2 | ตั้ง Headers | `X-Line-User-Id: Utest_001` <br> `X-Channel-Code: demo_coop` |
| 2.3 | กด Send | - |

#### ผลที่คาดหวัง

| Check | Expected |
|-------|----------|
| HTTP Status | `200 OK` |
| Response.success | `true` |
| Response.data | Array ของ categories |
| แต่ละ category มี | `id`, `name`, `product_count` |

---

| Test ID | UAT-002b |
|---------|----------|
| **Test Case** | Get Products - ดูรายการสินค้า |

#### วิธีทดสอบ

| Step | Action | Input/URL |
|------|--------|-----------|
| 2.4 | สร้าง GET request | `GET /api/line-buyer/products?limit=10` |
| 2.5 | ตั้ง Headers | `X-Line-User-Id: Utest_001` <br> `X-Channel-Code: demo_coop` |
| 2.6 | กด Send | - |

#### ผลที่คาดหวัง

| Check | Expected |
|-------|----------|
| HTTP Status | `200 OK` |
| Response.success | `true` |
| Response.data.items | Array ของ products (≥1 รายการ) |
| แต่ละ product มี | `id`, `name`, `price`, `image_url` |
| **จดบันทึก** | จด `product_id` ของสินค้า 2 ตัวแรกไว้ใช้ Step 3 |

#### ตัวอย่าง Response
```json
{
  "success": true,
  "data": {
    "items": [
      {"id": 1, "name": "สินค้า A", "price": 100.00},
      {"id": 2, "name": "สินค้า B", "price": 250.00}
    ],
    "total": 2
  }
}
```

---

### Step 3: Add to Cart (เพิ่มสินค้าลงตะกร้า)

| Test ID | UAT-003a |
|---------|----------|
| **Test Case** | Add Product to Cart - เพิ่มสินค้าชิ้นแรก |

#### วิธีทดสอบ

| Step | Action | Input/URL |
|------|--------|-----------|
| 3.1 | สร้าง POST request | `POST /api/line-buyer/cart/add` |
| 3.2 | ตั้ง Headers | `Content-Type: application/json` <br> `X-Line-User-Id: Utest_001` <br> `X-Channel-Code: demo_coop` |
| 3.3 | ใส่ Body | ```{"product_id": 1, "quantity": 2}``` |
| 3.4 | กด Send | - |

#### ผลที่คาดหวัง

| Check | Expected |
|-------|----------|
| HTTP Status | `200 OK` |
| Response.success | `true` |
| Response.message | `"Added to cart"` หรือคล้ายกัน |

---

| Test ID | UAT-003b |
|---------|----------|
| **Test Case** | Add Second Product - เพิ่มสินค้าชิ้นที่ 2 |

#### วิธีทดสอบ

| Step | Action | Input/URL |
|------|--------|-----------|
| 3.5 | สร้าง POST request | `POST /api/line-buyer/cart/add` |
| 3.6 | ใส่ Body | ```{"product_id": 2, "quantity": 1}``` |
| 3.7 | กด Send | - |

#### ผลที่คาดหวัง
- เหมือน UAT-003a

---

| Test ID | UAT-003c |
|---------|----------|
| **Test Case** | Get Cart - ตรวจสอบตะกร้าสินค้า |

#### วิธีทดสอบ

| Step | Action | Input/URL |
|------|--------|-----------|
| 3.8 | สร้าง GET request | `GET /api/line-buyer/cart` |
| 3.9 | ตั้ง Headers | `X-Line-User-Id: Utest_001` <br> `X-Channel-Code: demo_coop` |
| 3.10 | กด Send | - |

#### ผลที่คาดหวัง

| Check | Expected |
|-------|----------|
| HTTP Status | `200 OK` |
| Response.success | `true` |
| Response.data.item_count | `3` (2+1 ชิ้น) |
| Response.data.lines | Array มี 2 รายการ |
| Response.data.subtotal | ราคารวมถูกต้อง (2×100 + 1×250 = 450) |
| Response.data.total | subtotal + tax |

#### ตัวอย่าง Response
```json
{
  "success": true,
  "data": {
    "id": 123,
    "name": "S00001",
    "item_count": 3,
    "subtotal": 450.00,
    "tax": 31.50,
    "total": 481.50,
    "lines": [
      {"product": {"id": 1, "name": "สินค้า A"}, "quantity": 2, "subtotal": 200.00},
      {"product": {"id": 2, "name": "สินค้า B"}, "quantity": 1, "subtotal": 250.00}
    ]
  }
}
```

---

### Step 4: Shipping Address (ที่อยู่จัดส่ง)

| Test ID | UAT-004a |
|---------|----------|
| **Test Case** | Get Existing Addresses - ดูที่อยู่ที่มีอยู่ |

#### วิธีทดสอบ

| Step | Action | Input/URL |
|------|--------|-----------|
| 4.1 | สร้าง GET request | `GET /api/line-buyer/checkout/shipping-addresses` |
| 4.2 | ตั้ง Headers | `X-Line-User-Id: Utest_001` <br> `X-Channel-Code: demo_coop` |
| 4.3 | กด Send | - |

#### ผลที่คาดหวัง

| Check | Expected |
|-------|----------|
| HTTP Status | `200 OK` |
| Response.success | `true` |
| Response.data | Array (อาจว่างเปล่าถ้าไม่มีที่อยู่) |

---

| Test ID | UAT-004b |
|---------|----------|
| **Test Case** | Create New Address - สร้างที่อยู่ใหม่ |

#### วิธีทดสอบ

| Step | Action | Input/URL |
|------|--------|-----------|
| 4.4 | สร้าง POST request | `POST /api/line-buyer/checkout/shipping-address` |
| 4.5 | ตั้ง Headers | `Content-Type: application/json` <br> `X-Line-User-Id: Utest_001` <br> `X-Channel-Code: demo_coop` |
| 4.6 | ใส่ Body | ดูด้านล่าง |
| 4.7 | กด Send | - |

**Request Body:**
```json
{
  "name": "ผู้ทดสอบ LINE",
  "phone": "0812345678",
  "street": "123 ถนนทดสอบ",
  "street2": "แขวงทดสอบ เขตทดสอบ",
  "city": "กรุงเทพมหานคร",
  "zip": "10110"
}
```

#### ผลที่คาดหวัง

| Check | Expected |
|-------|----------|
| HTTP Status | `200 OK` |
| Response.success | `true` |
| Response.data.id | ได้รับ address_id (number) |
| Response.data.name | `ผู้ทดสอบ LINE` |
| Response.data.street | `123 ถนนทดสอบ` |
| **จดบันทึก** | จด `address_id` ไว้ใช้ Step 5 |

---

### Step 5: Checkout (ยืนยันคำสั่งซื้อ)

| Test ID | UAT-005 |
|---------|---------|
| **Test Case** | Confirm Order - ยืนยันคำสั่งซื้อ |
| **Precondition** | ตะกร้ามีสินค้า, มี shipping_address_id |

#### วิธีทดสอบ

| Step | Action | Input/URL |
|------|--------|-----------|
| 5.1 | สร้าง POST request | `POST /api/line-buyer/checkout/confirm` |
| 5.2 | ตั้ง Headers | `Content-Type: application/json` <br> `X-Line-User-Id: Utest_001` <br> `X-Channel-Code: demo_coop` |
| 5.3 | ใส่ Body | ```{"shipping_address_id": <จาก Step 4>, "note": "ทดสอบ UAT"}``` |
| 5.4 | กด Send | - |

#### ผลที่คาดหวัง

| Check | Expected |
|-------|----------|
| HTTP Status | `200 OK` |
| Response.success | `true` |
| Response.data.order.id | ได้รับ order_id |
| Response.data.order.name | เลขที่ order (e.g., `S00001`) |
| Response.data.order.state | `sale` หรือ `draft` |
| Response.data.order.total | ยอดรวมถูกต้อง |
| Odoo Backend | เห็น Sale Order ใหม่ใน Sales > Orders |
| LINE Message (ถ้าเปิด) | ได้รับ Flex Message ยืนยัน order |

#### ตัวอย่าง Response
```json
{
  "success": true,
  "data": {
    "order": {
      "id": 456,
      "name": "S00001",
      "date": "2026-01-28",
      "state": "sale",
      "state_display": "Sales Order",
      "subtotal": 450.00,
      "tax": 31.50,
      "total": 481.50,
      "item_count": 3
    }
  }
}
```

---

### Step 6: Order History (ประวัติคำสั่งซื้อ)

| Test ID | UAT-006a |
|---------|----------|
| **Test Case** | Get Order List - ดูรายการคำสั่งซื้อ |

#### วิธีทดสอบ

| Step | Action | Input/URL |
|------|--------|-----------|
| 6.1 | สร้าง GET request | `GET /api/line-buyer/orders?limit=5` |
| 6.2 | ตั้ง Headers | `X-Line-User-Id: Utest_001` <br> `X-Channel-Code: demo_coop` |
| 6.3 | กด Send | - |

#### ผลที่คาดหวัง

| Check | Expected |
|-------|----------|
| HTTP Status | `200 OK` |
| Response.success | `true` |
| Response.data.orders | Array มี order ที่เพิ่งสร้าง |
| Order ล่าสุด | ตรงกับ order จาก Step 5 |

---

| Test ID | UAT-006b |
|---------|----------|
| **Test Case** | Get Order Detail - ดูรายละเอียด order |

#### วิธีทดสอบ

| Step | Action | Input/URL |
|------|--------|-----------|
| 6.4 | สร้าง GET request | `GET /api/line-buyer/orders/<order_id>` |
| 6.5 | แทน `<order_id>` | ใช้ order_id จาก Step 5 |
| 6.6 | ตั้ง Headers | `X-Line-User-Id: Utest_001` <br> `X-Channel-Code: demo_coop` |
| 6.7 | กด Send | - |

#### ผลที่คาดหวัง

| Check | Expected |
|-------|----------|
| HTTP Status | `200 OK` |
| Response.success | `true` |
| Response.data.name | เลขที่ order |
| Response.data.lines | รายการสินค้าครบ 2 รายการ |
| Response.data.shipping_address | ที่อยู่จัดส่งถูกต้อง |

---

## Test Summary Template

| Test ID | Test Case | Status | Tester | Date | Notes |
|---------|-----------|--------|--------|------|-------|
| UAT-001 | Mock Login | ⬜ Pass / ⬜ Fail | | | |
| UAT-002a | Get Categories | ⬜ Pass / ⬜ Fail | | | |
| UAT-002b | Get Products | ⬜ Pass / ⬜ Fail | | | |
| UAT-003a | Add to Cart (1st) | ⬜ Pass / ⬜ Fail | | | |
| UAT-003b | Add to Cart (2nd) | ⬜ Pass / ⬜ Fail | | | |
| UAT-003c | Get Cart | ⬜ Pass / ⬜ Fail | | | |
| UAT-004a | Get Addresses | ⬜ Pass / ⬜ Fail | | | |
| UAT-004b | Create Address | ⬜ Pass / ⬜ Fail | | | |
| UAT-005 | Confirm Order | ⬜ Pass / ⬜ Fail | | | |
| UAT-006a | Get Order List | ⬜ Pass / ⬜ Fail | | | |
| UAT-006b | Get Order Detail | ⬜ Pass / ⬜ Fail | | | |

**Total:** ___/11 Passed

---

## Curl Commands (Quick Reference)

```bash
# Step 1: Login
curl -X POST http://localhost:8076/api/line-buyer/auth/mock/login \
  -H "Content-Type: application/json" \
  -d '{"line_user_id":"Utest_001","display_name":"ผู้ทดสอบ LINE","channel_code":"demo_coop"}'

# Step 2a: Get Categories
curl -X GET http://localhost:8076/api/line-buyer/categories \
  -H "X-Line-User-Id: Utest_001" \
  -H "X-Channel-Code: demo_coop"

# Step 2b: Get Products
curl -X GET "http://localhost:8076/api/line-buyer/products?limit=10" \
  -H "X-Line-User-Id: Utest_001" \
  -H "X-Channel-Code: demo_coop"

# Step 3a: Add to Cart
curl -X POST http://localhost:8076/api/line-buyer/cart/add \
  -H "Content-Type: application/json" \
  -H "X-Line-User-Id: Utest_001" \
  -H "X-Channel-Code: demo_coop" \
  -d '{"product_id":1,"quantity":2}'

# Step 3c: Get Cart
curl -X GET http://localhost:8076/api/line-buyer/cart \
  -H "X-Line-User-Id: Utest_001" \
  -H "X-Channel-Code: demo_coop"

# Step 4b: Create Address
curl -X POST http://localhost:8076/api/line-buyer/checkout/shipping-address \
  -H "Content-Type: application/json" \
  -H "X-Line-User-Id: Utest_001" \
  -H "X-Channel-Code: demo_coop" \
  -d '{"name":"ผู้ทดสอบ LINE","phone":"0812345678","street":"123 ถนนทดสอบ","city":"กรุงเทพมหานคร","zip":"10110"}'

# Step 5: Confirm Order
curl -X POST http://localhost:8076/api/line-buyer/checkout/confirm \
  -H "Content-Type: application/json" \
  -H "X-Line-User-Id: Utest_001" \
  -H "X-Channel-Code: demo_coop" \
  -d '{"shipping_address_id":1,"note":"ทดสอบ UAT"}'

# Step 6a: Get Orders
curl -X GET "http://localhost:8076/api/line-buyer/orders?limit=5" \
  -H "X-Line-User-Id: Utest_001" \
  -H "X-Channel-Code: demo_coop"

# Step 6b: Get Order Detail (replace 456 with actual order_id)
curl -X GET http://localhost:8076/api/line-buyer/orders/456 \
  -H "X-Line-User-Id: Utest_001" \
  -H "X-Channel-Code: demo_coop"
```

---

## Error Cases to Test (Optional)

| Test ID | Scenario | Expected Error |
|---------|----------|----------------|
| ERR-001 | Login without channel_code | `400 - Channel code required` |
| ERR-002 | Add invalid product_id to cart | `404 - Product not found` |
| ERR-003 | Checkout with empty cart | `400 - Cart is empty` |
| ERR-004 | Get order with wrong user | `403 - Forbidden` |
| ERR-005 | Access without authentication | `401 - Unauthorized` |
