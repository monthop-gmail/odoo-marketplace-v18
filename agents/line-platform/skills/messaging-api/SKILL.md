---
name: messaging-api
description: LINE messaging operations. Activate when working on message types
  (reply/push/broadcast), LineApiService, LineMessagingService, flex messages,
  rate limits, or notification delivery.
---

# Messaging API (ระบบส่งข้อความ LINE)

You are an expert at LINE messaging integration in the marketplace, handling reply messages, push notifications, broadcast messages, flex message templates, and rate limit management.

> If you see unfamiliar `~~category` placeholders, see [CONNECTORS.md](../../CONNECTORS.md).

## Message Types

| Type | Method | Use Case | Rate Limit |
|------|--------|----------|------------|
| **Reply** | `reply_message(token, messages)` | Respond to user event | Free (within event) |
| **Push** | `push_message(user_id, messages)` | Proactive notification | Quota-based |
| **Multicast** | `multicast(user_ids, messages)` | Group notification | Quota-based |
| **Broadcast** | `broadcast(messages)` | All followers | Quota-based |

## Service Architecture

### LineApiService (low-level)
```python
# services/line_api.py
class LineApiService:
    def push_message(self, user_id, messages)
    def reply_message(self, reply_token, messages)
    def multicast(self, user_ids, messages)
    def broadcast(self, messages)
    def get_profile(self, user_id)
    def set_user_rich_menu(self, user_id, rich_menu_id)
```

### LineMessagingService (business-level)
```python
# services/line_messaging.py
class LineMessagingService:
    def send_order_confirmation(self, order, member)
    def send_seller_notification(self, seller, message)
    def send_delivery_update(self, picking, member)
    def send_welcome_message(self, member)
    def send_approval_notification(self, partner)
    def send_withdrawal_status(self, withdrawal, member)
```

## Flex Message Templates

Used for rich, interactive notifications:

```json
{
  "type": "flex",
  "altText": "New order #SO123",
  "contents": {
    "type": "bubble",
    "header": { "..." : "..." },
    "body": { "type": "box", "contents": ["..."] },
    "footer": {
      "type": "box",
      "contents": [{
        "type": "button",
        "action": { "type": "uri", "label": "View Details", "uri": "..." }
      }]
    }
  }
}
```

## Rate Limits

| Plan | Monthly Quota | Notes |
|------|--------------|-------|
| Free | 500 messages | Push + multicast + broadcast combined |
| Light | 5,000 | Low-cost tier |
| Standard | 25,000 | Overage charged per message |

**Strategy**: Use reply messages (free) whenever possible. Reserve push for critical notifications.

## Owned Files

| File | Purpose |
|------|---------|
| `core_line_integration/services/line_api.py` | Low-level LINE API wrapper |
| `core_line_integration/services/line_messaging.py` | Business-level messaging |
| `core_line_integration/models/line_notify_log.py` | Notification audit log |

## Anti-Patterns

| Don't | Do Instead |
|-------|-----------|
| Use push when reply token is available | Always prefer reply (free) over push (quota) |
| Send messages to unfollowed users | Check member `is_active` before sending |
| Hard-code message text in services | Use templates with dynamic data |
| Skip error handling on API calls | Handle 429 (rate limit) and retry with backoff |
| Send sensitive data in LINE messages | Include links to LIFF for details, not raw data |

## Cross-References

| Direction | Skill | Interaction |
|-----------|-------|-------------|
| ← | [channel-management](../channel-management/SKILL.md) | Channel token for API auth |
| ← | [webhook-handling](../webhook-handling/SKILL.md) | Webhook event → reply message |
| ← | [notification-triggers](../notification-triggers/SKILL.md) | Business events → message dispatch |
| ← | [rich-menu-system](../rich-menu-system/SKILL.md) | Rich menu assignment via API |
| ← | [user-identity](../user-identity/SKILL.md) | Member record provides LINE user_id |
