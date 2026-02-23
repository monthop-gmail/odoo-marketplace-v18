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
│  + Create rich menu via LINE API                     │
│  + Upload menu image                                 │
│  + Set as default or assign to users                 │
│  + Update line.rich.menu record in Odoo              │
└─────────────────────────────────────────────────────┘
```

## Menu Specifications

| Menu | Size | Style | Buttons |
|------|------|-------|---------|
| Buyer | 2500x843px | White bg, green rounded buttons | ร้านค้า, ตะกร้า, คำสั่งซื้อ, โปรไฟล์ |
| Seller | 2500x843px | White bg, orange rounded buttons | แดชบอร์ด, โพสต์สินค้า, สินค้า, กระเป๋าเงิน |
| Admin | 2500x843px | White bg, dark blue rounded buttons | Pending redesign |

**Design Assets:**
- Icons: Font Awesome 5 Solid (`/tmp/fa-solid-900.ttf`)
- Font: NotoSansThai-Bold (`/tmp/NotoSansThai-Bold.ttf`)
- All menus: `selected=true` (expanded by default)

## Workflow

1. **Select Role** — Choose buyer, seller, or admin
2. **Generate Image** — Create 2500x843px menu image with PIL
3. **Create Menu** — POST to LINE Rich Menu API
4. **Upload Image** — Upload image to created menu
5. **Assign** — Set as default or assign to role members
6. **Record** — Save rich menu ID in Odoo line.rich.menu

## Output

```markdown
## Rich Menu Deployed

**Role:** [buyer/seller/admin]
**Menu ID:** richmenu-[hash]
**Size:** 2500x843px
**Buttons:** [count]

### Button Map
| Area | Label | Action |
|------|-------|--------|
| [x,y,w,h] | [label] | [uri/postback] |

### Assignment
- Default for role: [yes/no]
- Users assigned: [count]
```

## Next Steps

- Want me to deploy another role's menu?
- Should I reassign menus to existing users?
- Want to preview the menu design first?

## Related Skills

- Uses [line-integration](../skills/line-integration/SKILL.md) for LINE API operations
- Full design spec in `memory/rich_menu_design.md`
