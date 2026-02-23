# /approve-seller

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).

Review and approve or reject a seller application.

## Usage

```
/approve-seller <seller_name_or_id>
```

## How It Works

```
┌─────────────────────────────────────────────────────┐
│                  APPROVE SELLER                      │
├─────────────────────────────────────────────────────┤
│  STANDALONE (always works)                           │
│  ✓ Review seller application data                    │
│  ✓ Check required documents/info                     │
│  ✓ Generate approval/rejection recommendation        │
├─────────────────────────────────────────────────────┤
│  SUPERCHARGED (when ~~marketplace-engine connected)  │
│  + Pull seller record from Odoo                      │
│  + Execute status transition in DB                   │
│  + Auto-create seller.shop + ~~wallet                │
│  + Assign security group + ~~rich-menu               │
│  + Send ~~messaging notification to seller           │
└─────────────────────────────────────────────────────┘
```

## What I Need From You

- Seller name, partner ID, or LINE user ID
- Or paste the application data directly

## Workflow

1. **Fetch Application** — Pull seller record from ~~crm (res.partner)
2. **Review Checklist** — Verify required fields and documents
3. **Recommend** — Generate approval or rejection recommendation
4. **Execute** — On your approval: transition status, create shop + wallet, assign groups
5. **Notify** — Send ~~messaging push + email notification to seller

## Approval Checklist

| Item | Required | Check |
|------|----------|-------|
| Full name | Yes | Non-empty |
| Phone number | Yes | Valid format |
| Email | Yes | Valid format |
| ID document | Yes | Uploaded |
| Bank account | Recommended | For withdrawal |
| Shop name | Yes | Non-empty |

## Output

```markdown
## Seller Application Review

**Applicant:** [name] (partner_id: [id])
**Applied:** [date]
**Status:** pending → [approved/denied]

### Checklist
- [x/✗] Full name: [value]
- [x/✗] Phone: [value]
- [x/✗] Email: [value]
- [x/✗] Documents: [count] uploaded
- [x/✗] Shop name: [value]

### Recommendation
[APPROVE/REJECT] — [reason]

### Side Effects (on approval)
- Security group: marketplace_seller_group assigned
- Shop: seller.shop created (url_handler: shop-[id])
- Wallet: seller.wallet created (balance: 0)
- Rich menu: Seller menu assigned
- LINE notification: Sent
```

## Next Steps

- Want me to approve this seller now?
- Should I send a custom message to the seller?
- Want to review more pending sellers?

## Related Skills

- Uses [seller-engine](../skills/seller-engine/SKILL.md) for status flow logic
- Triggers [line-integration](../skills/line-integration/SKILL.md) for notifications
- Triggers [commission-wallet](../skills/commission-wallet/SKILL.md) for wallet creation
