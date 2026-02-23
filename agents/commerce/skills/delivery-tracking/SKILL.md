---
name: delivery-tracking
description: Shipping status and delivery tracking. Activate when working on
  delivery carrier configuration, shipment tracking, delivery notifications,
  shipping label generation, or delivery status updates.
---

# Delivery Tracking (การติดตามการจัดส่ง)

You are an expert at managing shipping and delivery workflows in a multi-vendor marketplace, handling carrier configuration, tracking updates, and delivery notifications.

> If you see unfamiliar `~~category` placeholders, see [CONNECTORS.md](../../CONNECTORS.md).

## Delivery Flow

```
Order Confirmed → stock.picking (assigned) → Shipped → In Transit → Delivered
                                            ↓
                                    Tracking number assigned
                                            ↓
                                    ~~messaging notify buyer
```

| Status | Who Acts | Buyer Sees | Notification |
|--------|----------|------------|--------------|
| Assigned | System | "กำลังเตรียมจัดส่ง" | -- |
| Shipped | Seller marks | "จัดส่งแล้ว" | LINE push with tracking |
| In Transit | Carrier update | "อยู่ระหว่างจัดส่ง" | Optional update |
| Delivered | Confirm delivery | "จัดส่งสำเร็จ" | LINE push confirmation |

## Carrier Integration

Marketplace uses Odoo's `delivery` module with marketplace extensions:

```python
# stock.picking marketplace extension
class StockPicking(models.Model):
    _inherit = 'stock.picking'
    marketplace_seller_id = fields.Many2one('res.partner')
    carrier_tracking_ref = fields.Char()  # tracking number
```

## Tracking Notification Flow

1. Seller adds tracking number → `carrier_tracking_ref` updated
2. System fires write trigger → ~~notification to buyer
3. Buyer receives LINE push with tracking info
4. Delivery confirmed → triggers invoice + commission flow

## Seller Shipping Dashboard

Sellers see their pending shipments via:
- LIFF seller app: orders with shipping status
- Odoo backend: `stock.picking` filtered by `marketplace_seller_id`

## Owned Files

| File | Purpose |
|------|---------|
| `core_marketplace/models/stock.py` | stock.picking delivery extensions |
| `core_marketplace/views/mp_stock_view.xml` | Delivery management views |
| `core_line_integration/services/line_messaging.py` | Delivery notification messages |

## Anti-Patterns

| Don't | Do Instead |
|-------|-----------|
| Let seller A update seller B's delivery | Scope by `marketplace_seller_id` |
| Skip tracking notification to buyer | Always notify via ~~messaging on tracking update |
| Mark delivered without confirmation | Require explicit delivery confirmation |
| Allow delivery edit after completion | Lock completed deliveries |

## Cross-References

| Direction | Skill | Interaction |
|-----------|-------|-------------|
| ← | [stock-management](../stock-management/SKILL.md) | Picking created → delivery tracking begins |
| ← | [order-processing](../order-processing/SKILL.md) | Order confirm → picking → delivery |
| → | [commission-engine](../../../finance/skills/commission-engine/SKILL.md) | Delivery confirmed → commission settlement |
| → | [messaging-api](../../../line-platform/skills/messaging-api/SKILL.md) | Tracking update → LINE push to buyer |
| → | [notification-triggers](../../../line-platform/skills/notification-triggers/SKILL.md) | Delivery events → notification routing |
