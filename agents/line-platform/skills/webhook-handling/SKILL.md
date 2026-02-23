---
name: webhook-handling
description: LINE webhook event processing. Activate when working on webhook endpoint,
  event types (follow/unfollow/message/postback), signature validation, follow flow,
  member registration, or event routing.
---

# Webhook Handling (การจัดการ Webhook)

You are an expert at processing LINE webhook events in the marketplace platform, handling signature validation, event routing, member auto-registration, and message processing.

> If you see unfamiliar `~~category` placeholders, see [CONNECTORS.md](../../CONNECTORS.md).

## Webhook Endpoint

```
POST /api/line-buyer/webhook/<channel_code>
Headers: X-Line-Signature (HMAC-SHA256)
Body: { "events": [...] }
```

## Signature Validation

Every webhook request must be validated:

```python
import hmac, hashlib, base64

def validate_signature(body, signature, channel_secret):
    hash = hmac.new(
        channel_secret.encode('utf-8'),
        body.encode('utf-8'),
        hashlib.sha256
    ).digest()
    expected = base64.b64encode(hash).decode('utf-8')
    return hmac.compare_digest(signature, expected)
```

## Event Types

| Event Type | Trigger | Handler Action |
|------------|---------|----------------|
| `follow` | User adds LINE OA as friend | Create/reactivate `line.channel.member` |
| `unfollow` | User blocks/removes LINE OA | Deactivate member, clear rich menu |
| `message` | User sends text/image/sticker | Route to appropriate handler |
| `postback` | User clicks rich menu/button | Parse `data` param, execute action |

## Follow Flow (Most Critical)

```
User follows LINE OA
    ↓
Webhook receives follow event
    ↓
Extract userId from event.source
    ↓
Search existing line.channel.member
    ├── Found (returning): reactivate, sync role
    └── Not found (new): create member record
        ↓
    Set member_type = 'buyer' (default)
        ↓
    Assign buyer rich menu via ~~rich-menu
        ↓
    Send welcome message via ~~messaging
```

## Postback Data Format

```
action=navigate&page=products
action=quick_post
action=view_order&order_id=123
```

Parsed as query string parameters for flexible routing.

## Event Processing Pipeline

```python
@http.route('/api/line-buyer/webhook/<channel_code>', auth='none', methods=['POST'])
def webhook(self, channel_code, **kwargs):
    # 1. Find channel by code
    # 2. Validate X-Line-Signature
    # 3. Parse events from body
    # 4. For each event:
    #    - follow -> _handle_follow()
    #    - unfollow -> _handle_unfollow()
    #    - message -> _handle_message()
    #    - postback -> _handle_postback()
    # 5. Return 200 OK (LINE requires < 1 second)
```

## Owned Files

| File | Purpose |
|------|---------|
| `core_line_integration/controllers/webhook.py` | Webhook endpoint + event routing |
| `core_line_integration/services/line_api.py` | LINE API calls for profile fetch |
| `core_line_integration/models/line_channel_member.py` | Member create/update on events |

## Anti-Patterns

| Don't | Do Instead |
|-------|-----------|
| Skip signature validation | Always validate HMAC-SHA256 |
| Do heavy processing in webhook handler | Return 200 fast, process async if needed |
| Create duplicate members on re-follow | Search existing first, reactivate if found |
| Ignore unfollow events | Deactivate member to stop sending messages |
| Log full event body with user data | Log event type + userId only |

## Cross-References

| Direction | Skill | Interaction |
|-----------|-------|-------------|
| ← | [channel-management](../channel-management/SKILL.md) | Channel provides secret for validation |
| → | [user-identity](../user-identity/SKILL.md) | Follow → create/update member record |
| → | [rich-menu-system](../rich-menu-system/SKILL.md) | Follow → assign default rich menu |
| → | [messaging-api](../messaging-api/SKILL.md) | Follow → send welcome message |
| → | [notification-triggers](../notification-triggers/SKILL.md) | Events trigger notifications |
