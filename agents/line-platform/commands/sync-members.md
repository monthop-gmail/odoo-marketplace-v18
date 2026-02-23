# /sync-members

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).

Sync LINE members with Odoo partner records and role assignments.

## Usage

```
/sync-members                         # Full sync all members
/sync-members <line_user_id>          # Sync specific user
/sync-members --check                  # Dry run: show out-of-sync members
/sync-members --role buyer|seller|admin # Sync specific role group
```

## How It Works

```
┌─────────────────────────────────────────────────────┐
│                SYNC MEMBERS                          │
├─────────────────────────────────────────────────────┤
│  STANDALONE (always works)                           │
│  ✓ Explain sync logic and field mapping              │
│  ✓ Describe member_type resolution rules             │
│  ✓ Show rich menu assignment flow                    │
├─────────────────────────────────────────────────────┤
│  SUPERCHARGED (when ~~marketplace-engine connected)  │
│  + Pull all line.channel.member records              │
│  + Compare member_type with res.partner status       │
│  + Fix mismatches (member_type, rich menu)           │
│  + Reassign ~~rich-menu based on current role        │
│  + Report sync results                               │
└─────────────────────────────────────────────────────┘
```

## Sync Fields

| Field | Source (Odoo) | Target (LINE) | Sync Direction |
|-------|--------------|---------------|----------------|
| member_type | res.partner.seller_status + groups | line.channel.member.member_type | Odoo → LINE |
| rich_menu | Determined by member_type | LINE Rich Menu API assignment | Odoo → LINE |
| display_name | res.partner.name | line.channel.member (display) | Odoo → LINE |
| status | LINE follow/unfollow events | line.channel.member.status | LINE → Odoo |

## Member Type Resolution

```python
# Priority order:
1. Is admin? (officer/manager group) → member_type = 'admin'
2. Is seller? (seller_status = 'approved') → member_type = 'seller'
3. Is staff? (seller.shop.staff active) → member_type = 'seller'
4. Default → member_type = 'buyer'
```

## Key Method

```
line.channel.member.sync_member_type_from_partner()
    → Resolves member_type from partner status/groups
    → Assigns correct rich menu via assign_role_rich_menu()
    → Sends LINE notification on role change
```

## Workflow

1. **Scan** -- Pull all line.channel.member records from ~~crm
2. **Compare** -- Check member_type against res.partner current status
3. **Identify Mismatches** -- List members with wrong type or menu
4. **Fix** -- Update member_type and reassign ~~rich-menu
5. **Report** -- Summary of changes made

## Output

```markdown
## Member Sync Report

**Date:** [timestamp]
**Total Members:** [count]

### Sync Summary
| Status | Count |
|--------|-------|
| Already in sync | [n] |
| Updated | [n] |
| Errors | [n] |
| Unfollowed (skipped) | [n] |

### Changes Made
| LINE User ID | Name | Old Type | New Type | Rich Menu | Status |
|-------------|------|----------|----------|-----------|--------|
| [uid] | [name] | buyer | seller | Seller v4 assigned | OK |
| [uid] | [name] | seller | buyer | Buyer v19 assigned | OK |

### Errors (if any)
| LINE User ID | Error | Action Needed |
|-------------|-------|---------------|
| [uid] | [error_msg] | [suggested_fix] |

### Member Distribution
| Type | Count | % |
|------|-------|---|
| Buyer | [n] | [%] |
| Seller | [n] | [%] |
| Admin | [n] | [%] |
```

## Next Steps

- Want to sync a specific user?
- Should I reassign rich menus for all members?
- Want to check for orphaned LINE members (no partner)?

## Related Skills

- Uses [member-management](../skills/member-management/SKILL.md) for member data
- Uses [rich-menu](../skills/rich-menu/SKILL.md) for menu assignment
- Cross-references [seller-lifecycle](../../seller-engine/skills/seller-lifecycle/SKILL.md) for role verification
