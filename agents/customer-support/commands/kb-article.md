# /kb-article

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).

Create, update, or search knowledge base articles for the support team.

## Usage

```
/kb-article create "วิธีติดตามสถานะคำสั่งซื้อ"
/kb-article update <article_id> --section steps
/kb-article search "คืนเงิน"
/kb-article list --category orders
```

## How It Works

```
┌─────────────────────────────────────────────────────┐
│                   KB ARTICLE                         │
├─────────────────────────────────────────────────────┤
│  STANDALONE (always works)                           │
│  ✓ Draft article following standard structure        │
│  ✓ Search existing articles by keyword               │
│  ✓ Suggest improvements to existing articles         │
│  ✓ Generate FAQ entries from support patterns        │
├─────────────────────────────────────────────────────┤
│  SUPERCHARGED (when ~~api + filesystem connected)    │
│  + Create/update article files in docs/              │
│  + Index articles for search                         │
│  + Link related articles automatically               │
│  + Track article usage and helpfulness               │
└─────────────────────────────────────────────────────┘
```

## Article Structure

| Section | Required | Description |
|---------|----------|-------------|
| **Title** | Yes | Clear, searchable Thai title |
| **Short Answer** | Yes | 1-2 sentence TL;DR |
| **Category** | Yes | orders / payment / product / account / seller |
| **Steps** | Yes | Numbered step-by-step instructions |
| **Screenshots** | Recommended | Visual aids for LIFF app flows |
| **Related Articles** | Recommended | Links to related topics |
| **Tags** | Yes | Search keywords |

## Article Categories

| Category | Topics |
|----------|--------|
| `orders` | สั่งซื้อ, ติดตาม, ยกเลิก, ประวัติ |
| `payment` | ชำระเงิน, คืนเงิน, ใบเสร็จ |
| `product` | ค้นหา, รายละเอียด, เปรียบเทียบ |
| `account` | โปรไฟล์, ที่อยู่, LINE เชื่อมต่อ |
| `seller` | สมัครขาย, จัดการร้าน, สินค้า, กระเป๋าเงิน |

## Output

```markdown
## KB Article

**ID:** KB-[number]
**Title:** [Thai title]
**Category:** [category]
**Tags:** [tag1], [tag2], [tag3]

### Short Answer
[1-2 sentence summary that directly answers the question]

### Steps
1. เปิด LINE OA แล้วกดเมนู [menu item]
2. [step description]
3. [step description]

### Screenshots
- [description of where screenshot should go]

### Related Articles
- KB-[id]: [related title]
- KB-[id]: [related title]
```

## Next Steps

- Want me to create this article now?
- Should I generate articles from recent support tickets?
- Want to review and update existing articles?

## Related Skills

- Uses [customer-support](../skills/) for common issue patterns
- Cross-references [liff-frontend](../../liff-apps/skills/) for UI flow descriptions
