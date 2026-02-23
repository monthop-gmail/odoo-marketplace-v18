# /create-campaign

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).

Create a marketing campaign for the marketplace.

## Usage

```
/create-campaign broadcast       # LINE broadcast campaign
/create-campaign flash-sale      # Time-limited flash sale
/create-campaign featured        # Featured product/seller promotion
/create-campaign welcome         # New user welcome sequence
```

## How It Works

```
┌─────────────────────────────────────────────────────┐
│               CREATE CAMPAIGN                        │
├─────────────────────────────────────────────────────┤
│  STANDALONE (always works)                           │
│  ✓ Design campaign strategy and messaging            │
│  ✓ Create content calendar and schedule              │
│  ✓ Define target audience and goals                  │
├─────────────────────────────────────────────────────┤
│  SUPERCHARGED (when ~~messaging connected)           │
│  + Create LINE broadcast messages                    │
│  + Set up flex message templates                     │
│  + Configure targeted segments via ~~crm             │
│  + Schedule delivery via ~~notification              │
│  + Track campaign in line.notify.log                 │
└─────────────────────────────────────────────────────┘
```

## Campaign Types

| Type | Channel | Target | Goal |
|------|---------|--------|------|
| Broadcast | LINE push message | All/segment | Awareness, engagement |
| Flash Sale | LINE + LIFF banner | Buyers | Urgency, conversion |
| Featured | LIFF homepage + LINE | Buyers | Product discovery |
| Welcome | LINE auto-reply | New followers | Onboarding, activation |

## Campaign Template

| Field | Required | Description |
|-------|----------|-------------|
| Name | Yes | Campaign identifier |
| Type | Yes | broadcast/flash-sale/featured/welcome |
| Target | Yes | Audience segment (all/buyer/seller) |
| Content | Yes | Message content (text/flex/image) |
| Schedule | No | Send date/time (default: immediate) |
| Duration | No | For flash-sale: start/end times |
| Goal | No | Target metric (clicks, orders, revenue) |

## Content Guidelines (80/20 Rule)

```
80% Value Content  → Tips, guides, community stories, product education
20% Selling Content → Promotions, new arrivals, flash sales, featured items
```

| Content Type | Examples | Frequency |
|-------------|----------|-----------|
| Value (80%) | How-to guides, seller stories, tips | 4x per week |
| Selling (20%) | New products, flash sales, promotions | 1x per week |

## Workflow

1. **Define** -- Choose campaign type, target, and goals
2. **Create Content** -- Draft messages following 80/20 rule
3. **Design** -- Create flex messages or image assets
4. **Review** -- Preview content and verify targeting
5. **Schedule** -- Set delivery time or trigger conditions
6. **Launch** -- Execute via ~~messaging
7. **Track** -- Monitor delivery and engagement

## Output

```markdown
## Campaign Created

**Name:** [campaign_name]
**Type:** [broadcast/flash-sale/featured/welcome]
**Target:** [segment] ([count] users)
**Schedule:** [date/time or "immediate"]

### Content
**Message Type:** [text/flex/image]
[Preview of message content]

### Goals
| Metric | Target |
|--------|--------|
| Reach | [n] users |
| Click-through | [n]% |
| Conversions | [n] orders |
| Revenue | ฿[amount] |

### Timeline
| Step | Date | Status |
|------|------|--------|
| Content ready | [date] | Done |
| Review approved | [date] | [status] |
| Scheduled send | [date] | [status] |
| Results review | [date] | [status] |
```

## Next Steps

- Want me to create the message content?
- Should I set up the flex message template?
- Want to schedule this campaign?

## Related Skills

- Uses [content-strategy](../skills/content-strategy/SKILL.md) for 80/20 content planning
- Uses [messaging](../../line-platform/CONNECTORS.md) for LINE broadcast
- Uses [campaign-analytics](../skills/campaign-analytics/SKILL.md) for tracking
