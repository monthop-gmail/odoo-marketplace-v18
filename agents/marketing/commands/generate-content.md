# /generate-content

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).

Generate marketing content following the 80/20 value-to-selling ratio.

## Usage

```
/generate-content value              # Generate value-based content (80%)
/generate-content selling            # Generate selling content (20%)
/generate-content --product <name>   # Content for specific product
/generate-content --platform          # Platform-level content (about marketplace)
```

## How It Works

```
┌─────────────────────────────────────────────────────┐
│              GENERATE CONTENT                        │
├─────────────────────────────────────────────────────┤
│  STANDALONE (always works)                           │
│  ✓ Generate content following 80/20 rule             │
│  ✓ Create social media posts (YouTube/FB/TikTok)     │
│  ✓ Draft LINE messages and flex templates            │
├─────────────────────────────────────────────────────┤
│  SUPERCHARGED (when ~~marketplace-engine connected)  │
│  + Pull product data for product-specific content    │
│  + Pull seller stories for community content         │
│  + Generate flex messages with real product data     │
│  + Create content calendar with scheduling           │
└─────────────────────────────────────────────────────┘
```

## Content Strategy: 80/20 Rule

```
Social Media (YouTube/Facebook/TikTok)
    ↓ 80% value content, 20% selling
LINE OA (Customer Hub)
    ↓ Engagement, notifications, community
LIFF Mini App (Marketplace UI)
    ↓ Conversion, transactions, retention
```

## Value Content (80%)

| Type | Format | Channel | Example |
|------|--------|---------|---------|
| How-to Guide | Video/Post | YouTube/FB | "5 วิธีเลือกซื้อสินค้าออนไลน์อย่างปลอดภัย" |
| Seller Story | Interview/Post | FB/LINE | "เรื่องราวของร้าน [shop] จากแม่ค้าออนไลน์สู่ธุรกิจ" |
| Tips & Tricks | Carousel/Short | TikTok/IG | "3 เคล็ดลับถ่ายรูปสินค้าให้ขายดี" |
| Behind the Scenes | Video/Story | FB/TikTok | "เบื้องหลังการทำงานของ Marketplace" |
| Community Highlight | Post | FB/LINE | "สมาชิกเด่นประจำสัปดาห์" |
| Product Education | Article/Video | YouTube/FB | "วิธีดูแลรักษา [product_type]" |

## Selling Content (20%)

| Type | Format | Channel | Example |
|------|--------|---------|---------|
| New Arrival | Flex Message | LINE | "สินค้าใหม่เข้าร้าน [shop]!" |
| Flash Sale | Image + CTA | LINE/FB | "ลดราคา 24 ชม.! เริ่มต้น ฿99" |
| Featured Product | Carousel | LINE/FB | "สินค้าแนะนำประจำสัปดาห์" |
| Seller Promotion | Post | FB/LINE | "ร้านค้าน่าสนใจ: [shop_name]" |
| Seasonal | Campaign | All | "โปรฯ ต้อนรับเทศกาล [event]" |

## Content Templates

### LINE Text Message
```
[Emoji] [Headline]

[2-3 lines of value content]

[CTA with LIFF link]
```

### LINE Flex Message
```json
{
    "type": "bubble",
    "hero": { "type": "image", "url": "[product_image]" },
    "body": {
        "type": "box",
        "contents": [
            { "type": "text", "text": "[product_name]", "weight": "bold" },
            { "type": "text", "text": "฿[price]", "color": "#28a745" }
        ]
    },
    "footer": {
        "type": "box",
        "contents": [
            { "type": "button", "action": { "type": "uri", "label": "ดูรายละเอียด", "uri": "[liff_url]" }}
        ]
    }
}
```

## Output

```markdown
## Generated Content

**Type:** [value/selling]
**Channel:** [LINE/Facebook/YouTube/TikTok]
**Target:** [audience]

### Content

**Headline:** [headline]

**Body:**
[Full content text in Thai]

**CTA:** [Call to action with link]

### Metadata
| Field | Value |
|-------|-------|
| Content Ratio | [value/selling] (current: [n]% value / [n]% selling) |
| Word Count | [n] |
| Estimated Reach | [n] users |
| Best Post Time | [time] |

### Variations
1. [Short version for TikTok/Story]
2. [Medium version for Facebook]
3. [Long version for YouTube/Blog]
```

## Next Steps

- Want me to create more content variations?
- Should I generate a full content calendar?
- Want to schedule this content as a broadcast?

## Related Skills

- Uses [content-strategy](../skills/content-strategy/SKILL.md) for 80/20 planning
- Uses [campaign-analytics](../skills/campaign-analytics/SKILL.md) for performance data
- Cross-references [product-catalog](../../commerce/CONNECTORS.md) for product data
