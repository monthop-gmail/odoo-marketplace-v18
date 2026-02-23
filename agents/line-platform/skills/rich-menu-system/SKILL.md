---
name: rich-menu-system
description: Role-based LINE rich menus. Activate when working on rich menu design,
  menu assignment per role, rich menu creation/deployment, design assets, auto-assignment
  on role change, or menu IDs.
---

# Rich Menu System (ระบบ Rich Menu ตามบทบาท)

You are an expert at managing role-based LINE rich menus in the marketplace, handling design, deployment, and automatic assignment based on user roles.

> If you see unfamiliar `~~category` placeholders, see [CONNECTORS.md](../../CONNECTORS.md).

## Three Menus by Role

| Menu | Role | Color | Style | Status |
|------|------|-------|-------|--------|
| **Buyer** | Default (all users) | Green (#22C55E) | White bg, rounded buttons | v19 active |
| **Seller** | Approved sellers | Orange (#F97316) | White bg, rounded buttons | v4 active |
| **Admin** | Officers/Managers | Dark Blue (#1E3A5F) | Old style | Pending redesign |

## Current Menu IDs

| Menu | Rich Menu ID |
|------|-------------|
| Buyer v19 | `richmenu-7a6e070685505e1468295a6f30f7698d` |
| Seller v4 | `richmenu-535463298053979e6737d61aeb8163b6` |
| Admin | `richmenu-0fe9475592e57ad478d183a030deb0a1` |

## Design Specification

- **Canvas**: 2500 x 843px (LINE standard)
- **Background**: White (#FFFFFF)
- **Buttons**: Colored rounded rectangles with FA5 icons + Thai labels
- **Font**: NotoSansThai-Bold (from Google Fonts CDN)
- **Icons**: Font Awesome 5 Solid (`fa-solid-900.ttf`)
- **selected**: `true` (menus expanded by default)

### Buyer Menu Layout (4 buttons)
```
[ ร้านค้า (shop) | ตะกร้า (cart) | คำสั่งซื้อ (orders) | โปรไฟล์ (profile) ]
```

### Seller Menu Layout (4 buttons)
```
[ แดชบอร์ด (dashboard) | โพสต์สินค้า (quick post) | สินค้า (products) | กระเป๋าเงิน (wallet) ]
```

## Auto-Assignment Flow

```
res_partner.write(seller_status='approved')
    ↓
sync_member_type_from_partner()
    ↓
member.member_type = 'seller'
    ↓
assign_role_rich_menu(member)
    ↓
LineApiService.set_user_rich_menu(user_id, seller_menu_id)
```

Key method: `line.channel.member.assign_role_rich_menu()`

## Deployment Workflow

1. Generate menu image (2500x843px) with buttons
2. Upload via LINE Messaging API: `POST /v2/bot/richmenu`
3. Upload image: `POST /v2/bot/richmenu/{richMenuId}/content`
4. Set as default (optional): `POST /v2/bot/user/all/richmenu/{richMenuId}`
5. Store menu ID in `line.rich.menu` model
6. Assign to users: `POST /v2/bot/user/{userId}/richmenu/{richMenuId}`

## Design Asset Paths

| Asset | Path |
|-------|------|
| FA5 Solid font | `/tmp/fa-solid-900.ttf` |
| NotoSansThai-Bold | `/tmp/NotoSansThai-Bold.ttf` |

## Owned Files

| File | Purpose |
|------|---------|
| `core_line_integration/models/line_rich_menu.py` | Rich menu model + assignment logic |
| `core_line_integration/services/line_api.py` | set_user_rich_menu() API call |
| `core_line_integration/models/line_channel_member.py` | assign_role_rich_menu() method |

## Anti-Patterns

| Don't | Do Instead |
|-------|-----------|
| Assign seller menu to non-approved sellers | Check `seller_status == 'approved'` first |
| Hard-code rich menu IDs | Store in `line.rich.menu` model records |
| Skip menu on follow event | Always assign buyer menu on new follow |
| Use text-only menus | Design with icons + Thai labels for usability |
| Create menus larger than 2500x843 | Follow LINE's exact dimension requirements |

## Cross-References

| Direction | Skill | Interaction |
|-----------|-------|-------------|
| ← | [channel-management](../channel-management/SKILL.md) | Channel token for menu API |
| ← | [user-identity](../user-identity/SKILL.md) | Member role change → menu reassignment |
| ← | [webhook-handling](../webhook-handling/SKILL.md) | Follow event → assign default menu |
| ← | [seller-lifecycle](../../../seller-engine/skills/seller-lifecycle/SKILL.md) | Seller approved → seller menu |
| → | [messaging-api](../messaging-api/SKILL.md) | Menu assignment via LINE API |
