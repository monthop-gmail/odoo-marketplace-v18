---
name: escalation
description: Support escalation workflow and tier management. Activate when working on ticket escalation rules, tier definitions, auto-escalation triggers, supervisor notifications, or SLA breach handling.
---

# Escalation (การยกระดับเรื่อง)

You manage the escalation workflow that ensures critical issues reach the right people at the right time.

> If you see unfamiliar `~~category` placeholders, see [CONNECTORS.md](../../CONNECTORS.md).

## Escalation Tiers

| Tier | Role | Handles | Tools |
|------|------|---------|-------|
| T1 | Support Agent | General inquiries, FAQ, simple order issues | ~~messaging, knowledge base |
| T2 | Senior Agent | Complex orders, refunds, seller complaints | ~~marketplace-engine, ~~payment |
| T3 | Platform Officer | Seller approval, product moderation, wallet disputes | ~~wallet, admin LIFF |
| T4 | Platform Manager | Security incidents, legal issues, system outages | Full system access |

## Escalation Flow

```
T1 (Support Agent)
 ↓ Cannot resolve in SLA / meets auto-escalation criteria
T2 (Senior Agent)
 ↓ Requires admin action / policy decision
T3 (Platform Officer)
 ↓ Critical business impact / legal / security
T4 (Platform Manager)
```

## Auto-Escalation Rules

| Trigger | From | To | Condition |
|---------|------|----|-----------|
| SLA breach — response | T1 | T2 | No response within SLA time |
| SLA breach — resolution | T2 | T3 | Not resolved within SLA time |
| Customer repeat contact | T1 | T2 | Same issue reported 3+ times |
| Payment dispute | T1 | T2 | Any refund > ฿1,000 |
| Large refund | T2 | T3 | Refund > ฿5,000 |
| Seller fraud report | T1 | T3 | Fraud keywords detected |
| Security incident | Any | T4 | Account compromise, data leak |
| Negative public review | T1 | T2 | Low rating with complaint text |
| Wallet balance mismatch | T2 | T3 | Discrepancy confirmed |
| System outage | Any | T4 | Multiple users reporting same error |

## Notification Triggers

| Event | Who Gets Notified | Channel |
|-------|-------------------|---------|
| Ticket escalated to T2 | Senior agent on duty | ~~messaging LINE push |
| Ticket escalated to T3 | All officers | ~~messaging LINE push + email |
| Ticket escalated to T4 | Platform manager | ~~messaging LINE push + phone call |
| SLA about to breach (80%) | Current assignee | ~~messaging LINE push |
| SLA breached | Current assignee + supervisor | ~~messaging LINE push |
| Customer marked VIP | Current assignee | In-ticket flag |

## Escalation Data Package

When escalating, the following context must be transferred:

| Data | Source | Required |
|------|--------|----------|
| Full ticket history | Ticket system | Yes |
| Customer profile | ~~identity / ~~crm | Yes |
| Order details | ~~marketplace-engine | If order-related |
| Wallet transactions | ~~wallet | If wallet-related |
| Previous tickets | Ticket system | Yes |
| Attempted resolutions | Agent notes | Yes |
| Screenshots/evidence | Customer attachments | If available |

## Decision Table: When to Escalate

| Situation | Escalate? | To | Reason |
|-----------|-----------|-----|--------|
| Customer asks for refund < ฿1,000 | No | - | T1 can process |
| Customer asks for refund > ฿1,000 | Yes | T2 | Requires senior approval |
| "ร้านหลอกลวง" report | Yes | T3 | Seller investigation needed |
| Simple how-to question | No | - | T1 + knowledge base |
| Technical bug confirmed | Yes | T3 | Developer investigation |
| Customer threatens legal | Yes | T4 | Legal review needed |
| Wallet balance negative | Yes | T3 | Financial investigation |

## Anti-Patterns

| Don't | Do Instead |
|-------|-----------|
| Escalate without trying to resolve | Attempt T1 resolution first |
| Escalate without context | Always include full data package |
| Skip tiers (T1 → T4) | Follow tier order unless security/legal |
| Let SLA silently breach | Auto-notify before breach (80% threshold) |
| Re-assign without notifying customer | Tell customer: "ส่งเรื่องให้ทีมที่ดูแลโดยตรงแล้วค่ะ" |

## Cross-References
- [ticket-triage](../ticket-triage/SKILL.md) — Initial priority that determines SLA
- [response-drafting](../response-drafting/SKILL.md) — Escalation notification templates
- [buyer-research](../buyer-research/SKILL.md) — Customer context for escalation package
