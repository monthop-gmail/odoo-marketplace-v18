# /approve-seller

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).

Review and approve or reject a seller application.

## Usage

```
/approve-seller <seller_name_or_id>
/approve-seller --pending         # List all pending applications
```

## How It Works

```
┌─────────────────────────────────────────────────────┐
│                  APPROVE SELLER                      │
├─────────────────────────────────────────────────────┤
│  STANDALONE (always works)                           │
│  ✓ Review seller application data                    │
│  ✓ Check required documents and info                 │
│  ✓ Generate approval/rejection recommendation        │
├─────────────────────────────────────────────────────┤
│  SUPERCHARGED (when ~~marketplace-engine connected)  │
│  + Pull seller record from Odoo (res.partner)        │
│  + Execute status transition (pending → approved)    │
│  + Auto-create seller.shop + ~~wallet                │
│  + Assign marketplace_seller_group + ~~rich-menu     │
│  + Send ~~messaging notification to seller           │
└─────────────────────────────────────────────────────┘
```

## What I Need From You

- Seller name, partner ID, or LINE user ID
- Or paste the application data directly

## Workflow

1. **Fetch Application** — Pull seller record from ~~crm (res.partner where seller_status=pending)
2. **Review Checklist** — Verify required fields and documents against criteria
3. **Recommend** — Generate approval or rejection recommendation with reasoning
4. **Execute** — On your confirmation: transition status, create shop + wallet, assign groups
5. **Notify** — Send ~~messaging push notification to seller via LINE

## Approval Checklist

| Item | Required | Check |
|------|----------|-------|
| Full name | Yes | Non-empty, real name |
| Phone number | Yes | Valid Thai format |
| Email | Yes | Valid format |
| ID document | Yes | Uploaded to attachments |
| Bank account | Recommended | For future withdrawals |
| Shop name | Yes | Non-empty, unique |

## Output

```markdown
## Seller Application Review

**Applicant:** [name] (partner_id: [id])
**LINE:** [line_user_id]
**Applied:** [date]
**Status:** pending → [approved/denied]

### Checklist
- [x/✗] Full name: [value]
- [x/✗] Phone: [value]
- [x/✗] Email: [value]
- [x/✗] ID document: [count] uploaded
- [x/✗] Bank account: [status]
- [x/✗] Shop name: [value]

### Recommendation
[APPROVE/REJECT] — [reason]

### Side Effects (on approval)
- Security group: marketplace_seller_group assigned
- Shop: seller.shop created (url_handler: shop-[id])
- Wallet: seller.wallet created (balance: 0.00)
- Rich menu: Seller menu assigned via LINE API
- LINE notification: Approval message sent
- member_type: synced to 'seller' via sync_member_type_from_partner()
```

## Next Steps

- Want me to approve this seller now?
- Should I send a custom message to the seller?
- Want to review more pending sellers?

## Related Skills

- Uses [seller-lifecycle](../skills/seller-lifecycle/SKILL.md) for status flow logic
- Triggers [line-integration](../../line-platform/CONNECTORS.md) for notifications
- Triggers [wallet](../../finance/CONNECTORS.md) for wallet creation
