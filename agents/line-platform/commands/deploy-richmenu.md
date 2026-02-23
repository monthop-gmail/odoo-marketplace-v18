# /deploy-richmenu

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).

Deploy or update LINE Rich Menus for buyer, seller, or admin roles.

## Usage

```
/deploy-richmenu buyer     # Deploy buyer rich menu
/deploy-richmenu seller    # Deploy seller rich menu
/deploy-richmenu admin     # Deploy admin rich menu
/deploy-richmenu --all     # Deploy all three
```

## How It Works

```
┌─────────────────────────────────────────────────────┐
│                DEPLOY RICH MENU                      │
├─────────────────────────────────────────────────────┤
│  STANDALONE (always works)                           │
│  ✓ Show current rich menu configuration              │
│  ✓ Generate menu design spec                         │
│  ✓ Validate button areas and actions                 │
├─────────────────────────────────────────────────────┤
│  SUPERCHARGED (when ~~messaging connected)           │
│  + Generate 2500x843 menu image with PIL             │
│  + Create rich menu via LINE API                     │
│  + Upload menu image to LINE                         │
│  + Set as default or assign to role members          │
│  + Update line.rich.menu record in Odoo              │
└─────────────────────────────────────────────────────┘
```

## Menu Specifications

| Menu | Size | Background | Button Style | Buttons |
|------|------|-----------|-------------|---------|
| Buyer | 2500x843px | White | Green rounded | ร้านค้า, ตะกร้า, คำสั่งซื้อ, โปรไฟล์ |
| Seller | 2500x843px | White | Orange rounded | แดชบอร์ด, โพสต์สินค้า, สินค้า, กระเป๋าเงิน |
| Admin | 2500x843px | White | Dark blue rounded | Pending redesign |

**Design Assets:**
- Icons: Font Awesome 5 Solid (`/tmp/fa-solid-900.ttf`)
- Font: NotoSansThai-Bold (`/tmp/NotoSansThai-Bold.ttf`)
- All menus: `selected=true` (expanded by default)

## Current Menu IDs

| Menu | Rich Menu ID | Version |
|------|-------------|---------|
| Buyer | `richmenu-7a6e070685505e1468295a6f30f7698d` | v19 |
| Seller | `richmenu-535463298053979e6737d61aeb8163b6` | v4 |
| Admin | `richmenu-0fe9475592e57ad478d183a030deb0a1` | old style |

## Deployment Workflow

1. **Generate Image** -- Create 2500x843px menu image using PIL with FA5 icons + Thai labels
2. **Create Menu** -- POST to LINE Rich Menu API with button areas and actions
3. **Upload Image** -- Upload generated image to the created menu
4. **Assign** -- Set as default for role or assign to individual users
5. **Record** -- Save new rich menu ID in Odoo `line.rich.menu` model
6. **Verify** -- Confirm menu appears correctly in LINE app

## Auto-Assignment

```
res.partner.write() → seller_status changes
    → sync_member_type_from_partner()
    → assign_role_rich_menu()
    → LineApiService.set_user_rich_menu()
```

## Output

```markdown
## Rich Menu Deployed

**Role:** [buyer/seller/admin]
**Menu ID:** richmenu-[hash]
**Version:** v[n]
**Size:** 2500x843px
**Buttons:** [count]

### Button Map
| Area | Label | Icon | Action |
|------|-------|------|--------|
| [x,y,w,h] | [Thai label] | [FA5 icon] | [uri/postback] |

### Assignment
- Default for role: [yes/no]
- Users assigned: [count]
- Previous menu: [old_id] (replaced)
```

## Next Steps

- Want me to deploy another role's menu?
- Should I reassign menus to existing users?
- Want to preview the menu design first?

## Related Skills

- Uses [rich-menu](../skills/rich-menu/SKILL.md) for menu configuration
- Uses [webhook](../skills/webhook/SKILL.md) for LINE API operations
- Full design spec in `memory/rich_menu_design.md`
