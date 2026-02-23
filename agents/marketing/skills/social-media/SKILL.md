---
name: social-media
description: Social media platform strategy for YouTube, Facebook, and TikTok. Activate when working on social content funneling into LINE OA, platform-specific strategies, cross-posting, or social media metrics.
---

# Social Media (โซเชียลมีเดีย)

You manage the social media strategy that funnels audiences from YouTube, Facebook, and TikTok into LINE OA — the central customer hub.

> If you see unfamiliar `~~category` placeholders, see [CONNECTORS.md](../../CONNECTORS.md).

## Architecture Flow

```
Social Media (YouTube / Facebook / TikTok)
    ↓ Value-Based Content (80% content, 20% selling)
LINE OA (Customer Hub)
    ↓ Identity, CRM, Broadcast, Notifications
LIFF Mini App (Marketplace UI)
    ↓ Shopping, Orders, Wallet
Odoo 18 (Backend Engine)
```

Social media is the **top of funnel**. LINE OA is where relationships live. LIFF is where transactions happen.

## Platform Strategy

| Platform | Content Type | Audience | CTA Goal |
|----------|-------------|----------|----------|
| **YouTube** | Long-form how-to, reviews, tutorials | Search-driven, evergreen | "เพิ่มเพื่อนใน LINE เพื่อรับส่วนลด" |
| **Facebook** | Community posts, photos, live sales | Existing community, shares | "แตะลิงก์เพิ่มเพื่อน LINE OA" |
| **TikTok** | Short-form, trending, behind-scenes | Discovery, younger audience | "ลิงก์ใน bio → LINE OA" |

## Platform-Specific Guidelines

### YouTube
- Video length: 5-15 minutes for how-to, 1-3 minutes for shorts
- SEO: Thai keywords in title, description, tags
- Always include LINE OA link in description + pinned comment
- End screen: "เพิ่มเพื่อน LINE OA" card

### Facebook
- Post types: photo carousel, short video, live stream, story
- Facebook Group for community building
- Live selling sessions → direct to LINE OA for ordering
- Share buyer testimonials and behind-scenes

### TikTok
- 15-60 second videos, hook in first 3 seconds
- Follow trending sounds and hashtags (Thai trends)
- Product demonstration in native, casual style
- Bio link → LINE OA add-friend URL

## Cross-Platform Calendar

| Time | Monday | Tuesday | Wednesday | Thursday | Friday | Saturday | Sunday |
|------|--------|---------|-----------|----------|--------|----------|--------|
| 10:00 | YouTube | FB Post | YouTube | FB Post | TikTok | FB Live | - |
| 14:00 | TikTok | TikTok | FB Post | TikTok | FB Post | TikTok | TikTok |
| 19:00 | FB Post | - | TikTok | - | YouTube | - | FB Post |

## Key Metrics

| Metric | Platform | Target |
|--------|----------|--------|
| Views / Reach | All | Growing month-over-month |
| Engagement Rate | All | >5% (Thai market benchmark) |
| LINE Add-Friend Rate | All → LINE | >2% of reach |
| Follower Growth | All | +10%/month |
| Content → Order Conversion | Full funnel | Track via UTM params |

## UTM Tracking
All social links to LINE OA should include UTM parameters:
```
https://line.me/R/ti/p/@shop?utm_source=youtube&utm_medium=video&utm_campaign=howto-leather
```

## Anti-Patterns

| Don't | Do Instead |
|-------|-----------|
| Post same content on all platforms | Adapt format per platform norms |
| Direct social followers to website | Funnel to LINE OA first, then LIFF |
| Ignore platform analytics | Review weekly, adjust strategy |
| Buy followers/engagement | Organic growth through value content |
| Post without CTA to LINE | Every post should have LINE OA mention |

## Cross-References
- [content-strategy](../content-strategy/SKILL.md) — 80/20 content balance
- [brand-voice](../brand-voice/SKILL.md) — Thai copywriting tone
- [campaign-management](../campaign-management/SKILL.md) — Coordinated campaigns
