# /send-broadcast

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).

Send LINE broadcast messages to marketplace users.

## Usage

```
/send-broadcast <message>                    # Broadcast text to all users
/send-broadcast --segment buyer|seller|admin  # Target specific role
/send-broadcast --preview                     # Preview without sending
/send-broadcast --flex <template>             # Send flex message
```

## How It Works

```
┌─────────────────────────────────────────────────────┐
│               SEND BROADCAST                         │
├─────────────────────────────────────────────────────┤
│  STANDALONE (always works)                           │
│  ✓ Compose broadcast message content                 │
│  ✓ Design flex message templates                     │
│  ✓ Plan targeting and segmentation                   │
├─────────────────────────────────────────────────────┤
│  SUPERCHARGED (when ~~messaging connected)           │
│  + Send broadcast via LINE Messaging API             │
│  + Target by segment (member_type)                   │
│  + Send flex, image, or text messages                │
│  + Log to ~~notification (line.notify.log)           │
│  + Preview message before sending                    │
└─────────────────────────────────────────────────────┘
```

## Message Types

| Type | Format | Use Case |
|------|--------|----------|
| Text | Plain text string | Announcements, updates |
| Flex | LINE Flex Message JSON | Product cards, promotions, rich layouts |
| Image | Image URL + preview URL | Visual announcements, banner ads |
| Template | Buttons/Confirm/Carousel | Interactive messages with actions |

## Safety Checklist

| Step | Description |
|------|-------------|
| 1. Preview | Always preview message content before sending |
| 2. Confirm count | Show target audience size before broadcast |
| 3. Rate limit | Respect LINE broadcast quota (free tier: 500/month) |
| 4. Timing | Avoid sending during late night hours (22:00-08:00) |
| 5. Log | Record broadcast in line.notify.log for audit |

## Segmentation

| Segment | member_type | Typical Count |
|---------|-------------|---------------|
| All users | * | All LINE members |
| Buyers | buyer | Default role users |
| Sellers | seller | Approved sellers + staff |
| Admins | admin | Platform officers/managers |

## Workflow

1. **Compose** -- Draft message content (text, flex, or image)
2. **Target** -- Select audience segment (all, buyer, seller, admin)
3. **Preview** -- Show message preview and target count
4. **Confirm** -- Get explicit approval before sending
5. **Send** -- Broadcast via ~~messaging (LINE Messaging API)
6. **Log** -- Record in ~~notification (line.notify.log)

## Output

```markdown
## Broadcast Sent

**Type:** [text/flex/image]
**Segment:** [all/buyer/seller/admin]
**Recipients:** [count] users
**Sent at:** [timestamp]

### Message Content
[Preview of message content]

### Delivery Status
| Metric | Value |
|--------|-------|
| Sent | [count] |
| Delivered | [count] |
| Failed | [count] |
| Quota Used | [used]/[limit] this month |
```

## Next Steps

- Want to send to a different segment?
- Should I create a flex message template?
- Want to check delivery status?

## Related Skills

- Uses [messaging](../skills/messaging/SKILL.md) for LINE API operations
- Uses [member-management](../skills/member-management/SKILL.md) for segmentation
- Logs to [notification](../skills/notification/SKILL.md) for audit trail
