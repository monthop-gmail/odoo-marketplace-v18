---
name: thai-localization
description: Thai language and address localization. Activate when working on Thai UI labels, cascading address dropdowns, province/district/subdistrict data, Thai currency formatting, or Thai text conventions.
---

# Thai Localization (การแปลภาษาไทย)

You manage all Thai language, addressing, and formatting conventions across the LIFF Mini Apps.

> If you see unfamiliar `~~category` placeholders, see [CONNECTORS.md](../../CONNECTORS.md).

## Cascading Address Dropdown

### Data Source
`core_line_integration/static/liff/js/thai-address-data.js` (404KB)
- Source: earthchie/jquery.Thailand.js
- 77 provinces / 928 districts / 7,475 sub-districts
- Province IDs mapped to Odoo `res.country.state` records

### Cascade Flow
```
จังหวัด (Province)  →  อำเภอ (District)  →  ตำบล (Sub-district)  →  รหัสไปรษณีย์ (Zip)
   <select>               <select>              <select>             <input auto-fill>
```

### Form Field IDs
| Field | HTML ID | Odoo Field |
|-------|---------|-----------|
| จังหวัด | `addr-province` | `state_id` (res.country.state) |
| อำเภอ | `addr-district` | `city` |
| ตำบล | `addr-subdistrict` | `street2` |
| รหัสไปรษณีย์ | `addr-zip` | `zip` |

### Save Mapping
- Province select value = Odoo `res.country.state` ID (integer)
- District display text saved to `city` field (string)
- Sub-district display text saved to `street2` field (string)
- Zip auto-filled and saved to `zip` field (string)

## Thai UI Labels

### Navigation
| English | Thai |
|---------|------|
| Home | หน้าแรก |
| Cart | ตะกร้า |
| Orders | คำสั่งซื้อ |
| Profile | โปรไฟล์ |
| Dashboard | แดชบอร์ด |
| Products | สินค้า |
| Wallet | กระเป๋าเงิน |
| Settings | ตั้งค่า |

### Actions
| English | Thai |
|---------|------|
| Add to Cart | หยิบใส่ตะกร้า |
| Details | รายละเอียด |
| Place Order | สั่งซื้อ |
| Post Product | โพสต์สินค้า |
| Save | บันทึก |
| Cancel | ยกเลิก |
| Delete | ลบ |
| Approve | อนุมัติ |
| Reject | ปฏิเสธ |

### Status
| English | Thai |
|---------|------|
| Pending | รอดำเนินการ |
| Approved | อนุมัติแล้ว |
| Rejected | ถูกปฏิเสธ |
| Completed | เสร็จสิ้น |
| Processing | กำลังดำเนินการ |

## Currency Format
- Symbol: ฿ (prefix)
- Format: `฿1,234.00`
- JavaScript: `'฿' + number.toLocaleString('th-TH', { minimumFractionDigits: 2 })`

## Rich Menu Labels (NotoSansThai-Bold)
- Font: NotoSansThai-Bold from Google Fonts CDN
- Icon font: FontAwesome 5 Solid (`fa-solid-900.ttf`)
- All rich menu button labels in Thai

## Anti-Patterns

| Don't | Do Instead |
|-------|-----------|
| Mix English and Thai in UI | Consistent Thai for user-facing text |
| Hardcode province list | Use thai-address-data.js with cascading |
| Skip zip auto-fill | Always auto-fill from sub-district selection |
| Use English date format | Thai Buddhist calendar where appropriate |
| Forget ครับ/ค่ะ in messages | Use polite particles in notification text |

## Cross-References
- [buyer-app](../buyer-app/SKILL.md) — Buyer Thai labels
- [seller-app](../seller-app/SKILL.md) — Seller Thai labels
- [mobile-ux](../mobile-ux/SKILL.md) — Thai-native feel principles
