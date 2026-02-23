# /manage-staff

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).

Manage shop staff members -- list, add, or remove.

## Usage

```
/manage-staff <shop_id>              # List staff for shop
/manage-staff add <shop_id> <user>   # Add staff member
/manage-staff remove <staff_id>      # Remove staff member
```

## How It Works

```
┌─────────────────────────────────────────────────────┐
│                  MANAGE STAFF                        │
├─────────────────────────────────────────────────────┤
│  STANDALONE (always works)                           │
│  ✓ Explain owner vs staff permission model           │
│  ✓ Describe staff constraints (1 person = 1 shop)    │
│  ✓ Show context switch pattern for API access        │
├─────────────────────────────────────────────────────┤
│  SUPERCHARGED (when ~~marketplace-engine connected)  │
│  + List current staff for a shop                     │
│  + Add new staff member (with validation)            │
│  + Remove staff member                               │
│  + Sync LINE member_type via ~~messaging             │
│  + Assign seller ~~rich-menu to new staff            │
└─────────────────────────────────────────────────────┘
```

## Permission Model

| Capability | Owner | Staff |
|------------|-------|-------|
| Quick Post (create products) | Yes | Yes |
| Edit products | Yes | Yes |
| View orders | Yes | No |
| Manage orders | Yes | No |
| Dashboard access | Yes | No |
| Wallet / balance | Yes | No |
| Withdrawal requests | Yes | No |
| Shop settings | Yes | No |
| Profile updates | Yes | No |
| Manage staff | Yes | No |

## Constraints

- **1 person = 1 shop**: `unique(staff_partner_id)` -- a person can only be staff at one shop
- **Context switch**: API resolves staff to shop owner's partner via `require_seller` decorator
- **Request attrs**: `seller_partner` (owner), `is_shop_owner`, `is_shop_staff`, `staff_record`
- **owner_only decorator**: Blocks staff from restricted operations

## Workflow

1. **Identify Shop** -- Resolve shop by ID, seller name, or URL handler
2. **List Staff** -- Show current staff with roles and status
3. **Add/Remove** -- Execute staff change with validation
4. **Sync LINE** -- Update member_type to 'seller' for new staff via ~~messaging
5. **Assign Menu** -- Set seller ~~rich-menu for new staff member

## Output

```markdown
## Shop Staff -- [shop_name]

**Owner:** [name] (partner_id: [id])
**Shop ID:** [id]

### Staff Members
| Name | Partner ID | Role | Status | Since | Invited By |
|------|-----------|------|--------|-------|------------|
| [name] | [id] | staff | active | [date] | [inviter] |

### Action Taken
[Added/Removed] [name] as staff
- LINE member_type: synced to 'seller'
- Rich menu: Seller menu assigned
```

## Next Steps

- Want to add more staff to this shop?
- Should I check what products staff have posted?
- Want to review staff activity?

## Related Skills

- Uses [staff-management](../skills/staff-management/SKILL.md) for staff logic
- Uses [seller-lifecycle](../skills/seller-lifecycle/SKILL.md) for owner verification
- Triggers [line-integration](../../line-platform/CONNECTORS.md) for LINE sync
