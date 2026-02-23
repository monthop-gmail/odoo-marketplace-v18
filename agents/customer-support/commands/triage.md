# /triage

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).

Triage an incoming support request — classify, prioritize, route, and draft initial response.

## Usage

```
/triage <description>
/triage "ลูกค้าสั่งซื้อแล้วไม่ได้รับของ order SO-1234"
/triage --bulk                    # Process all unassigned tickets
```

## How It Works

```
┌─────────────────────────────────────────────────────┐
│                     TRIAGE                            │
├─────────────────────────────────────────────────────┤
│  STANDALONE (always works)                           │
│  ✓ Classify category (order/payment/product/account) │
│  ✓ Assign priority P1-P4                             │
│  ✓ Suggest routing (T1 self-serve → T4 escalation)   │
│  ✓ Draft initial Thai response                       │
├─────────────────────────────────────────────────────┤
│  SUPERCHARGED (when ~~crm + ~~api connected)         │
│  + Look up customer by name/LINE ID/partner_id       │
│  + Check recent orders via ~~marketplace-engine      │
│  + Create support ticket in system                   │
│  + Auto-assign agent based on category               │
│  + Send ~~messaging acknowledgment to customer       │
└─────────────────────────────────────────────────────┘
```

## Priority Matrix

| Priority | Response SLA | Criteria |
|----------|-------------|----------|
| **P1 Critical** | 1 hour | Payment stuck, order lost, account locked |
| **P2 High** | 4 hours | Wrong item, refund request, seller dispute |
| **P3 Medium** | 24 hours | Shipping delay, product question, edit request |
| **P4 Low** | 48 hours | Feature request, general inquiry, feedback |

## Category Routing

| Category | Route | Owner |
|----------|-------|-------|
| Order issues | T1 → Commerce team | Officer |
| Payment/Refund | T2 → Finance team | Manager |
| Seller dispute | T2 → Seller Engine | Officer |
| Product quality | T1 → Commerce team | Officer |
| Account/LINE | T1 → LINE Integration | Officer |
| Technical bug | T3 → Engineering | Manager |

## Output

```markdown
## Support Triage

**Ticket:** [id]
**Customer:** [name] (partner_id: [id])
**Received:** [datetime]

### Classification
- **Category:** [order/payment/product/account/seller/technical]
- **Priority:** [P1/P2/P3/P4] — [reason]
- **Route:** [T1/T2/T3/T4] → [team]

### Analysis
[Brief description of the issue and context]

### Suggested Response
[Thai response draft following Acknowledge→Empathize→Solve→Follow-up]

### Next Actions
1. [action item]
2. [action item]
```

## Next Steps

- Want me to send this response to the customer?
- Should I escalate to a higher tier?
- Want to see this customer's full history?

## Related Skills

- Uses [customer-support](../skills/) for triage logic and response templates
- Cross-references [commerce](../../commerce/skills/) for order context
- Triggers [line-integration](../../line-platform/skills/) for messaging
