# Troubleshooting Guide

คู่มือแก้ปัญหาที่พบบ่อยสำหรับ LINE OA Integration

## สารบัญ

1. [Webhook Issues](#webhook-issues)
2. [Authentication Issues](#authentication-issues)
3. [LIFF Issues](#liff-issues)
4. [Message Sending Issues](#message-sending-issues)
5. [Rich Menu Issues](#rich-menu-issues)
6. [API Issues](#api-issues)
7. [Database Issues](#database-issues)
8. [Performance Issues](#performance-issues)

---

## Webhook Issues

### Webhook Verification Failed

**อาการ:**
- LINE Developers Console แสดง "Verification failed"
- Webhook URL ไม่ตอบสนอง

**สาเหตุและวิธีแก้:**

1. **URL ไม่ถูกต้อง**
   ```
   ✓ ถูกต้อง: https://your-domain.com/api/line-buyer/webhook/my_coop
   ✗ ผิด: http://your-domain.com/... (ต้องเป็น HTTPS)
   ✗ ผิด: https://your-domain.com/line/webhook (path ผิด)
   ```

2. **Channel code ไม่ตรง**
   - ตรวจสอบ channel code ใน Odoo กับ URL ที่ตั้งค่า
   - Channel code ต้องตรงกัน case-sensitive

3. **Odoo server ไม่ทำงาน**
   ```bash
   # ตรวจสอบ Odoo service
   systemctl status odoo

   # ตรวจสอบ log
   tail -f /var/log/odoo/odoo.log
   ```

4. **Firewall block**
   ```bash
   # ตรวจสอบ port 443/8069 เปิดอยู่
   sudo ufw status
   sudo ufw allow 443
   ```

### Signature Validation Failed (403 Error)

**อาการ:**
- Webhook ได้รับ request แต่ return 403
- Log แสดง "Invalid signature"

**สาเหตุและวิธีแก้:**

1. **Channel Secret ไม่ถูกต้อง**
   ```
   ตรวจสอบใน LINE Developers Console:
   Channel > Basic settings > Channel secret

   ต้องตรงกับค่าใน Odoo:
   Settings > LINE Marketplace > LINE Channels > Channel Secret
   ```

2. **Request body ถูกแก้ไข**
   - ตรวจสอบ reverse proxy (nginx) ไม่ได้แก้ไข body
   - ตรวจสอบว่าไม่มี middleware แก้ไข request

3. **Debug: Log signature**
   ```python
   # ใน webhook.py เพิ่ม logging
   import logging
   _logger = logging.getLogger(__name__)

   def webhook(self, channel_code, **kwargs):
       signature = request.httprequest.headers.get('X-Line-Signature')
       body = request.httprequest.get_data(as_text=True)
       _logger.info("Signature: %s", signature)
       _logger.info("Body: %s", body[:200])
   ```

### Events ไม่ถูกประมวลผล

**อาการ:**
- Webhook return 200 แต่ไม่มีอะไรเกิดขึ้น
- Follow event ไม่สร้าง member

**วิธีแก้:**

1. ตรวจสอบ Odoo log:
   ```bash
   grep "webhook" /var/log/odoo/odoo.log | tail -50
   ```

2. ตรวจสอบว่า events ถูก parse ถูกต้อง:
   ```python
   # ใน webhook handler
   events = request.jsonrequest.get('events', [])
   _logger.info("Received %d events", len(events))
   for event in events:
       _logger.info("Event type: %s", event.get('type'))
   ```

---

## Authentication Issues

### LIFF Token Validation Failed

**อาการ:**
- API return 401 Unauthorized
- "Invalid access token" error

**สาเหตุและวิธีแก้:**

1. **Token หมดอายุ**
   - LIFF access token มีอายุจำกัด
   - Frontend ต้อง refresh token เมื่อหมดอายุ
   ```javascript
   // ใน LIFF app
   if (!liff.isLoggedIn()) {
     liff.login();
   }
   const token = liff.getAccessToken();
   ```

2. **Channel ID ไม่ตรง**
   - Token ออกให้ channel หนึ่ง ใช้กับ channel อื่นไม่ได้
   - ตรวจสอบ X-Channel-Code header ถูกต้อง

3. **Production vs Sandbox**
   - Token จาก production ใช้กับ sandbox ไม่ได้
   - ตรวจสอบ environment ตรงกัน

### Mock Mode ไม่ทำงาน

**อาการ:**
- X-Line-User-Id header ไม่ถูก recognize
- API ยังคงต้องการ Bearer token

**วิธีแก้:**

1. ตรวจสอบ setting:
   ```
   Settings > LINE Marketplace > Mock Authentication Mode = ✓
   ```

2. ตรวจสอบ headers:
   ```bash
   curl -X GET "http://localhost:8069/api/line-buyer/products" \
     -H "X-Line-User-Id: test_user" \
     -H "X-Channel-Code: demo_coop"
   ```

3. ตรวจสอบ config parameter:
   ```sql
   SELECT * FROM ir_config_parameter
   WHERE key = 'line_buyer.mock_auth';
   ```

---

## LIFF Issues

### LIFF ไม่โหลด

**อาการ:**
- หน้าขาว หรือ error เมื่อเปิด LIFF
- "LIFF initialization failed"

**สาเหตุและวิธีแก้:**

1. **LIFF ID ไม่ถูกต้อง**
   ```javascript
   // ตรวจสอบ LIFF ID format
   // ถูกต้อง: 1234567890-AbCdEfGh
   liff.init({ liffId: "1234567890-AbCdEfGh" })
   ```

2. **Endpoint URL ไม่ถูกต้อง**
   - ตรวจสอบใน LINE Developers Console
   - URL ต้องเป็น HTTPS
   - URL ต้อง accessible จาก internet

3. **CORS Error**
   ```javascript
   // Console error: "Blocked by CORS policy"

   // แก้ใน Odoo controller
   response.headers['Access-Control-Allow-Origin'] = '*'
   ```

4. **Mixed Content**
   - LIFF ต้องโหลดจาก HTTPS
   - ห้ามมี HTTP resources ใน page

### LIFF ไม่ได้รับ Profile

**อาการ:**
- `liff.getProfile()` return null
- ไม่ได้ LINE user ID

**วิธีแก้:**

1. ตรวจสอบ Scope ใน LINE Developers:
   ```
   LIFF > Edit > Scopes
   ✓ profile
   ✓ openid (optional)
   ```

2. ตรวจสอบ Bot link feature:
   ```
   LIFF > Edit > Bot link feature = Aggressive
   ```

3. Code example:
   ```javascript
   liff.init({ liffId: 'xxx' })
     .then(() => {
       if (liff.isLoggedIn()) {
         return liff.getProfile();
       } else {
         liff.login();
       }
     })
     .then(profile => {
       console.log('User ID:', profile.userId);
     })
     .catch(err => {
       console.error('LIFF Error:', err);
     });
   ```

---

## Message Sending Issues

### Push Message Failed

**อาการ:**
- LINE notification ไม่ถูกส่ง
- Notification Log แสดง state = "failed"

**สาเหตุและวิธีแก้:**

1. **Channel Access Token หมดอายุ**
   ```
   LINE Developers > Channel > Messaging API > Channel access token
   คลิก "Issue" เพื่อสร้างใหม่
   อัปเดตใน Odoo
   ```

2. **User blocked bot**
   - ผู้ใช้ block LINE OA
   - ไม่สามารถส่งข้อความได้
   ```python
   # Error response จาก LINE
   {"message": "User has blocked the bot"}
   ```

3. **Rate limit exceeded**
   - Free plan: 500 messages/month
   - ตรวจสอบ usage ใน LINE Official Account Manager

4. **Invalid user ID**
   ```python
   # User ID ต้องขึ้นต้นด้วย "U"
   # ถูกต้อง: U1234567890abcdef1234567890abcdef
   # ผิด: 1234567890
   ```

### Flex Message Error

**อาการ:**
- "Invalid flex message" error
- Flex message ไม่แสดงผลถูกต้อง

**วิธีแก้:**

1. **ตรวจสอบ JSON structure**
   ```python
   import json
   flex_json = json.dumps(flex_content, indent=2)
   print(flex_json)  # ดู structure
   ```

2. **ใช้ Simulator ทดสอบ**
   - [Flex Message Simulator](https://developers.line.biz/flex-message-simulator/)
   - Copy JSON ไปทดสอบ

3. **ตรวจสอบ required fields**
   ```json
   {
     "type": "flex",
     "altText": "ต้องมี altText",  // Required!
     "contents": { ... }
   }
   ```

4. **ขนาดเกิน 50KB**
   ```python
   import json
   size = len(json.dumps(flex_content).encode('utf-8'))
   if size > 50000:
       print(f"Too large: {size} bytes")
   ```

---

## Rich Menu Issues

### Rich Menu ไม่แสดง

**อาการ:**
- ผู้ใช้ไม่เห็น Rich Menu
- Menu bar ว่างเปล่า

**วิธีแก้:**

1. **ยังไม่ได้ Create on LINE**
   ```
   Rich Menu record > คลิก "Create on LINE"
   State ต้องเปลี่ยนเป็น "Uploaded"
   ```

2. **ยังไม่ได้ Set as Default**
   ```
   Rich Menu record > คลิก "Set as Default"
   ```

3. **ผู้ใช้มี Rich Menu เฉพาะ**
   - ตรวจสอบว่าไม่มี user-specific rich menu

4. **Cache ใน LINE app**
   - ปิด/เปิด LINE app
   - Unfollow แล้ว Follow ใหม่

### Rich Menu Image ไม่ชัด

**วิธีแก้:**

1. ใช้ขนาดที่ถูกต้อง:
   - Full: 2500 x 1686 pixels
   - Half: 2500 x 843 pixels

2. ใช้ PNG สำหรับ text/icons

3. ตรวจสอบ file size < 1MB

---

## API Issues

### CORS Error

**อาการ:**
- Browser console แสดง "Blocked by CORS policy"
- API ทำงานจาก Postman แต่ไม่ทำงานจาก browser

**วิธีแก้:**

ตรวจสอบ CORS headers ใน response:
```python
# ใน controller
from odoo import http

class LineApiController(http.Controller):
    def _add_cors_headers(self, response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Line-User-Id, X-Channel-Code'
        return response
```

### 500 Internal Server Error

**วิธี Debug:**

1. ตรวจสอบ Odoo log:
   ```bash
   tail -f /var/log/odoo/odoo.log | grep -i error
   ```

2. เปิด debug mode ใน API:
   ```
   Settings > LINE Marketplace > API Debug Mode = ✓
   ```

3. ตรวจสอบ traceback:
   ```python
   import traceback
   try:
       # code
   except Exception as e:
       _logger.error("Error: %s\n%s", str(e), traceback.format_exc())
   ```

### Slow API Response

**วิธีแก้:**

1. ตรวจสอบ database queries:
   ```python
   # เปิด query logging
   # ใน odoo.conf
   log_level = debug_sql
   ```

2. ใช้ pagination:
   ```
   GET /api/line-buyer/products?page=1&limit=20
   ```

3. ลด data ที่ return:
   ```python
   # ใช้ fields selection
   products = env['product.template'].search_read(
       domain,
       fields=['id', 'name', 'list_price'],  # เฉพาะ fields ที่ต้องการ
       limit=20
   )
   ```

---

## Database Issues

### Member ซ้ำ

**อาการ:**
- LINE user มีหลาย member records
- Orders กระจายไปหลาย members

**วิธีแก้:**

1. ตรวจสอบ SQL constraint:
   ```sql
   SELECT line_user_id, channel_id, count(*)
   FROM line_channel_member
   GROUP BY line_user_id, channel_id
   HAVING count(*) > 1;
   ```

2. Merge members:
   ```python
   # รวม member ซ้ำ
   members = env['line.channel.member'].search([
       ('line_user_id', '=', 'Uxxx'),
       ('channel_id', '=', channel_id)
   ])
   if len(members) > 1:
       # เก็บ member แรก ลบที่เหลือ
       keep = members[0]
       duplicates = members[1:]
       for dup in duplicates:
           # ย้าย related records ไป keep
           dup.partner_id.line_member_ids -= dup
           dup.partner_id.line_member_ids += keep
           dup.unlink()
   ```

### Partner ไม่เชื่อมกับ LINE

**อาการ:**
- มี partner แต่ไม่มี LINE member
- ส่ง notification ไม่ได้

**วิธีแก้:**

1. ตรวจสอบ link:
   ```sql
   SELECT p.id, p.name, m.line_user_id
   FROM res_partner p
   LEFT JOIN line_channel_member m ON m.partner_id = p.id
   WHERE p.line_user_id IS NOT NULL
   AND m.id IS NULL;
   ```

2. สร้าง member จาก partner:
   ```python
   partner = env['res.partner'].browse(partner_id)
   if partner.line_user_id and not partner.line_member_ids:
       env['line.channel.member'].create({
           'line_user_id': partner.line_user_id,
           'channel_id': channel_id,
           'partner_id': partner.id,
           'display_name': partner.name,
       })
   ```

---

## Performance Issues

### Notification Queue Slow

**อาการ:**
- Pending notifications มากเกินไป
- Notifications ถูกส่งช้า

**วิธีแก้:**

1. ตรวจสอบ cron job:
   ```
   Settings > Technical > Automation > Scheduled Actions
   ค้นหา "Process Pending LINE Notifications"
   ตรวจสอบว่า Active และ Interval เหมาะสม
   ```

2. เพิ่ม limit ต่อ batch:
   ```python
   # ใน line_notify_log.py
   @api.model
   def process_pending_notifications(self, limit=100):  # เพิ่มจาก default
       ...
   ```

3. ใช้ multicast แทน push:
   ```python
   # แทนที่จะส่งทีละคน
   for user_id in user_ids:
       service.push_message(user_id, messages)

   # ใช้ multicast (สูงสุด 500 คน)
   service.multicast(user_ids, messages)
   ```

### High Memory Usage

**วิธีแก้:**

1. ใช้ iterator แทน list:
   ```python
   # แทนที่
   orders = env['sale.order'].search([...])
   for order in orders:
       ...

   # ใช้
   for order in env['sale.order'].search([...]):
       ...
       env.cr.commit()  # commit ทีละ batch
   ```

2. Clear cache:
   ```python
   env.invalidate_all()
   ```

---

## Quick Reference

### Log Locations

| Log | Path |
|-----|------|
| Odoo | `/var/log/odoo/odoo.log` |
| Nginx | `/var/log/nginx/access.log` |
| System | `journalctl -u odoo` |

### Useful Commands

```bash
# Restart Odoo
sudo systemctl restart odoo

# Check Odoo status
sudo systemctl status odoo

# Watch logs
tail -f /var/log/odoo/odoo.log

# Test webhook manually
curl -X POST "https://your-domain.com/api/line-buyer/webhook/my_coop" \
  -H "Content-Type: application/json" \
  -H "X-Line-Signature: test" \
  -d '{"events":[]}'

# Test API
curl -X GET "http://localhost:8069/api/line-buyer/products" \
  -H "X-Line-User-Id: test_user" \
  -H "X-Channel-Code: demo_coop"
```

### Contact Support

หากยังแก้ไขไม่ได้ ติดต่อทีมพัฒนาพร้อมข้อมูล:

1. Odoo log (ช่วง error)
2. Request/Response ที่เกี่ยวข้อง
3. Steps to reproduce
4. Environment (Odoo version, OS, etc.)
