# /escalate

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).

Escalate a support ticket to a higher tier with full context handoff.

## Usage

```
/escalate <ticket>
/escalate <ticket> --to T2 --reason "ลูกค้าต้องการคืนเงิน ไม่สามารถดำเนินการ T1 ได้"
/escalate <ticket> --to T3 --priority P1
```

## How It Works

```
┌─────────────────────────────────────────────────────┐
│                    ESCALATE                           │
├─────────────────────────────────────────────────────┤
│  STANDALONE (always works)                           │
│  ✓ Build escalation summary from provided context    │
│  ✓ Determine appropriate tier based on issue type    │
│  ✓ Draft handoff notes with timeline and actions     │
│  ✓ Recommend owner based on tier routing table       │
├─────────────────────────────────────────────────────┤
│  SUPERCHARGED (when ~~crm + ~~api connected)         │
│  + Pull full ticket history and customer profile     │
│  + Update ticket status and assignment in system     │
│  + Notify new owner via ~~messaging                  │
│  + Notify customer of escalation via ~~notification  │
│  + Log escalation event for SLA tracking             │
└─────────────────────────────────────────────────────┘
```

## Tier Definitions

| Tier | Role | Handles | Escalates To |
|------|------|---------|-------------|
| **T1** | Self-serve / Bot | FAQ, order status, tracking | T2 |
| **T2** | Officer | Refunds, disputes, seller issues | T3 |
| **T3** | Manager | Complex refunds, policy exceptions, bugs | T4 |
| **T4** | Engineering / Executive | System failures, legal, critical bugs | — |

## Escalation Checklist

| Item | Required | Purpose |
|------|----------|---------|
| Ticket ID | Yes | Tracking reference |
| Customer context | Yes | Name, LINE ID, partner_id |
| Issue summary | Yes | Clear problem statement |
| Actions taken | Yes | What T(n-1) already tried |
| Reason for escalation | Yes | Why current tier cannot resolve |
| Suggested resolution | Recommended | Help next tier act faster |

## Output

```markdown
## Escalation Report

**Ticket:** [id]
**From:** T[n] → T[n+1]
**Priority:** [P1-P4]
**Customer:** [name] (partner_id: [id])

### Issue Summary
[Concise problem description]

### Actions Taken (T[n])
1. [action and result]
2. [action and result]

### Reason for Escalation
[Why current tier cannot resolve]

### Recommended Action
[Suggested next steps for receiving tier]

### Timeline
| Time | Event |
|------|-------|
| [datetime] | Ticket created |
| [datetime] | T1 response sent |
| [datetime] | Escalated to T[n+1] |
```

## Next Steps

- Want me to notify the customer about the escalation?
- Should I assign a specific agent at the next tier?
- Want to set a follow-up reminder?

## Related Skills

- Uses [customer-support](../skills/) for tier routing and SLA rules
- Triggers [line-integration](../../line-platform/skills/) for notifications
