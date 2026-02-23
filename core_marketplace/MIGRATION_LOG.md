# Migration Log: odoo_marketplace v15 → v18

**Date:** 2026-01-27
**Source:** `/opt/docker-test/odoo-market-v15/odoo-addons/odoo_marketplace`
**Target:** `/opt/docker-test/odoo-tarad-v18/odoo-addons/odoo_marketplace`
**Database:** `odoo_tarad`

---

## Overview

Successfully migrated the Odoo Multi Vendor Marketplace module from Odoo 15 to Odoo 18. The module contains 283 files including 20 Python models, 7 wizards, 13 JavaScript files, and 23 XML views.

---

## Changes Made

### 1. Manifest & Init Updates

| File | Change |
|------|--------|
| `__manifest__.py` | Version changed from `2.0.3` to `18.0.1.0.0` |
| `__init__.py` | `pre_init_check` updated to validate Odoo 18 |

### 2. Python Model Fixes

#### 2.1 Deprecated API Replacements

| File | Old Code | New Code |
|------|----------|----------|
| `models/seller_payment.py:342` | `signal_workflow("invoice_open")` | `action_post()` |
| Multiple files (9 locations) | `check_object_reference('module', 'xmlid')[1]` | `_xmlid_to_res_id('module.xmlid')` |
| `models/sale.py` (3 locations) | `product.type == 'service'` | `product.detailed_type == 'service'` |
| Multiple files | `ir.default.get()` | `ir.default._get()` |
| `models/marketplace_dashboard.py` | `self._uid` | `self.env.user.id` |
| `models/ir_attachment.py:39` | `flush(['field1', 'field2'])` | `flush_model()` |
| Multiple files (8 locations) | `_read_group_fill_results()` | Commented out (removed in Odoo 17+) |
| `models/seller_review.py` (3 locations) | Selection fields with `translate=True` | Removed `translate=True` |
| `models/stock.py:187` | `self.user_has_groups()` | `self.env.user.has_group()` |
| `models/sale.py`, `models/marketplace_product.py` | `product.detailed_type` | `product.type` (Odoo 18 merged fields) |
| `models/res_partner.py` | (missing field) | Added `color = fields.Integer()` for kanban coloring |

**Files with `_read_group_fill_results` removed:**
- `models/stock.py` (MarketplaceStock, StockPicking)
- `models/res_partner.py` (ResPartner)
- `models/sale.py` (SaleOrderLine)
- `models/seller_payment.py` (SellerPayment)
- `models/marketplace_product.py` (ProductTemplate)
- `models/seller_review.py` (SellerReview, SellerRecommendation)

#### 2.2 Import Fixes

| File | Change |
|------|--------|
| `models/res_partner.py` | Removed `Warning` from `odoo.exceptions` imports |
| `models/marketplace_product.py` | Changed `raise Warning()` to `raise UserError()` |
| `controllers/main.py` | Changed `ensure_db` import to `from odoo.addons.web.controllers.home import ensure_db` |
| `controllers/main.py` (4 locations) | `get_current_pricelist()` → `_get_current_pricelist()` |
| `controllers/main.py` (6 locations) | Removed `website_published` from `order` clause (not stored in Odoo 18) |

#### 2.3 Code Pattern Fixes

| File | Change |
|------|--------|
| `models/stock.py:214-217` | Fixed context assignment: `self = self.with_context(skip_sms=True)` |
| `models/ir_http.py` | Completely rewritten - removed `HomeStaticTemplateHelpers` dependency |
| `models/res_partner.py:66` | Fixed SQL injection - using ORM for `_default_website_sequence()` |
| `models/seller_shop.py:65` | Fixed SQL injection pattern |
| `models/ir_attachment.py:40-41` | Fixed SQL injection pattern |

### 3. XML View Fixes

#### 3.1 Attribute Syntax Migration (Odoo 17+ requirement)

Converted **215 instances** of deprecated `attrs` and `states` attributes:

```xml
<!-- OLD -->
<field name="field" attrs="{'invisible': [('other_field', '=', False)]}"/>
<button states="draft,confirmed"/>

<!-- NEW -->
<field name="field" invisible="not other_field"/>
<button invisible="state not in ('draft', 'confirmed')"/>
```

**Files modified:**
- `wizard/seller_payment_wizard_view.xml`
- `wizard/mark_done_stats.xml`
- `wizard/seller_registration_wizard_view.xml`
- `views/mp_dashboard_view.xml`
- `views/mp_product_view.xml`
- `views/mp_sol_view.xml`
- `views/mp_stock_view.xml`
- `views/res_config_view.xml`
- `views/res_partner_view.xml`
- `views/seller_payment_view.xml`
- `views/seller_review_view.xml`
- `views/seller_shop_view.xml`
- `views/seller_view.xml`
- `views/website_config_view.xml`

#### 3.2 Tree → List Migration

All `<tree>` elements changed to `<list>`:
- XML element tags: `<tree>` → `<list>`
- View mode attributes: `view_mode="tree"` → `view_mode="list"`
- XPath expressions: `expr="//tree"` → `expr="//list"`
- View type fields: `<field name="view_mode">tree</field>` → `<field name="view_mode">list</field>`

#### 3.3 Inherited View Fixes

Removed `groups_id` from inherited view records (not supported in Odoo 18):
- `views/seller_view.xml`
- `views/seller_payment_view.xml`
- `views/seller_shop_view.xml`
- `views/mp_product_view.xml`
- `views/mp_stock_view.xml`
- `views/seller_review_view.xml`
- `views/mp_sol_view.xml`

#### 3.4 Simplified/Commented Out Views

Due to significant model changes in Odoo 18:

| File | View | Reason |
|------|------|--------|
| `views/mp_stock_view.xml` | `marketplace_picking_stock_modified_form_view` | Simplified to inherited view - many stock.picking fields removed/renamed |
| `views/mp_stock_view.xml` | `view_stock_move_operations_seller_view` | Simplified - `quantity_done` → `quantity`, `reserved_availability` removed |
| `views/mp_stock_view.xml` | `view_stock_move_nosuggest_operations_seller_view` | Commented out - incompatible |
| `views/mp_stock_view.xml` | `make_carrier_writeable_to_manager` | Commented out - incompatible |
| `views/res_config_view.xml` | `mp_seller_product_public_category_tree_view` | Removed - groups_id on inherited views |
| `views/website_account_template.xml` | `inherit_portal_layout` | Commented out - portal structure changed |

#### 3.5 Field Removals/Fixes

| File | Field | Action |
|------|-------|--------|
| `views/mp_product_view.xml` | `pricelist_id` in search filters | Removed (doesn't exist in product.template) |
| `views/res_partner_view.xml` | `open_parent` button | Removed (method doesn't exist) |
| `views/res_partner_view.xml` | `active_id` in context | Changed to `id` |
| `views/mp_stock_view.xml` | `show_mark_as_todo`, `show_check_availability`, `show_validate` | Removed (fields don't exist) |
| `views/mp_stock_view.xml` | `immediate_transfer`, `show_lots_text`, `show_operations`, `show_reserved` | Removed |

#### 3.6 Embedded Tree View Fixes

Simplified embedded tree views in wizard forms to use `many2many_tags` widget:
- `wizard/server_action_wizard.xml` - product_ids, marketplace_stock_ids, seller_review_ids, seller_recommendation_ids
- `wizard/variant_approval_wizard_view.xml` - variant_ids
- `wizard/mark_done_stats.xml` - sale_order_line_ids

#### 3.7 Deprecated HTML Element Fixes

Replaced deprecated `<font color='xxx'>` HTML tags with `<span style="color: xxx;">` in kanban views:

| File | Change |
|------|--------|
| `views/seller_view.xml` | Replaced 4 instances of `<font color='blue/green/orange/red'>` |
| `views/mp_product_view.xml` | Replaced 8 instances of `<font color='blue/green/orange/red'>` |

```xml
<!-- OLD -->
<font color='blue'><field name="state"/></font>

<!-- NEW -->
<span style="color: blue;"><field name="state"/></span>
```

#### 3.8 Static Asset Path Fixes

Fixed icon image paths in dashboard view - added leading `/` for proper URL resolution:

| File | Change |
|------|--------|
| `views/mp_dashboard_view.xml` | Fixed 4 icon paths |

```xml
<!-- OLD -->
<img src="odoo_marketplace/static/img/icon-product.png"/>

<!-- NEW -->
<img src="/odoo_marketplace/static/img/icon-product.png"/>
```

**Icons fixed:**
- `icon-product.png` (Products)
- `icon-order.png` (Orders)
- `icon-payment.png` (Payments)
- `icon-stock.png` (Marketplace Stock)

### 4. Security File Fixes

Removed references to non-existent models in `security/ir.model.access.csv`:
- `base.model_ir_translation` (removed in Odoo 18)
- `mail.model_mail_channel` (renamed to discuss.channel)
- `stock.model_stock_location_route` (removed)
- `stock.model_stock_immediate_transfer` (removed)
- `stock.model_stock_immediate_transfer_line` (removed)

### 5. JavaScript Fixes

| File | Change |
|------|--------|
| `static/src/js/marketplace_shop_editor.js` | Replaced `web.Model` with custom `ormCall()` using `ajax.jsonRpc()` |
| `static/src/js/kanban_column.js` | Commented out entirely (KanbanColumn/KanbanRenderer are OWL components in v18) |

---

## Known Warnings (Non-blocking)

The following warnings appear during installation but don't prevent functionality:

1. ~~**Deprecated `states` parameter on fields:**~~ ✅ Fixed (2026-01-27)

2. ~~**Deprecated kanban-box template:**~~ ✅ Fixed (2026-01-27)

3. **Access rules without groups:**
   - `access_seller_review_public`
   - `access_review_help_public`
   - `access_review_recommend_public`
   - `access_seller_shop_style`
   - `access_social_media`
   - `access_social_media_link`
   - `account_tax_global`

4. **DeprecationWarning: create method in batch** (Low priority)
   - Several models use old `@api.model` create pattern
   - Will need migration to batch create in future versions

---

## Testing

Module successfully installed on database `odoo_tarad` with command:
```bash
docker exec tarad-web odoo -i odoo_marketplace -d odoo_tarad --stop-after-init
```

---

## Recommendations for Future Improvements

1. **Remove deprecated `states` parameter from field definitions** - Use `readonly` attribute with domain expressions instead

2. **Update kanban views** - Replace `kanban-box` templates with `card` templates

3. **Add groups to public access rules** - To avoid deprecation warnings

4. **Review commented-out views** - Some portal templates may need to be rewritten for Odoo 18's new portal structure

5. **Test all workflows thoroughly:**
   - Seller registration
   - Product approval
   - Order processing
   - Payment management
   - Stock operations

---

## Post-Migration Fixes

### Fix 1: Seller Profile Page 500 Error (2026-01-27)

**Issue:** Seller profile pages (`/seller/profile/<url_handler>`) returned HTTP 500 error.

**Root Cause:** The template `shop_recently_product` called `website_sale.products_item` which in Odoo 18 uses a new method `_get_suitable_image_size()`. This method returned `None` in some cases, causing:
```
TypeError: can only concatenate str (not "NoneType") to str
Template: website_sale.products_item
```

**Solution:** Modified `views/website_mp_product_template.xml`:

1. **Updated `shop_recently_product` template:**
   - Changed from calling `website_sale.products_item` to `odoo_marketplace.mp_products_item`
   - Added null-safe handling for `td_product` dictionary values using `.get()` method with defaults

2. **Created new `mp_products_item` template:**
   - Custom marketplace product item template that doesn't rely on `website_sale.products_item`
   - Simplified product card rendering compatible with Odoo 18

**Files Modified:**
- `views/website_mp_product_template.xml`

**URLs Fixed:**
- `/seller/profile/mae-boonmee-sweets`
- `/seller/profile/baanthai-craft`
- `/seller/profile/organic-garden`

---

## Files Modified Summary

- **Python files:** 15+ files
- **XML view files:** 25+ files
- **JavaScript files:** 2 files
- **Security files:** 1 file

**Total changes:** 300+ modifications across the module

---

*Migration performed by Claude Code on 2026-01-27*

---

## Fix 2: Odoo 18.0-20260119 Compatibility Update (2026-01-27)

**Context:** After upgrading Odoo from `18.0-20250401` to `18.0-20260119`, several deprecation warnings appeared that needed to be addressed.

### 2.1 Boolean Field Attributes

Fixed string-based boolean attributes that should be actual booleans:

| File | Line | Old | New |
|------|------|-----|-----|
| `models/seller_payment.py` | 86 | `required="1", readonly="1"` | `required=True, readonly=True` |
| `models/seller_payment.py` | 89 | `readonly="1"` | `readonly=True` |
| `wizard/seller_status_reason.py` | 30 | `required="1"` | `required=True` |

### 2.2 Deprecated `states` Parameter Removal

Removed deprecated `states` parameter from field definitions and moved readonly logic to XML views.

**Python Files Modified:**

| File | Fields Changed |
|------|----------------|
| `models/seller_payment.py` | `name`, `seller_id`, `date`, `payment_type`, `payment_mode`, `invoice_id`, `payable_amount` |
| `models/account_move.py` | `seller_invoice_number` |

**View File Modified:**
- `views/seller_payment_view.xml` - Added `readonly="state != 'draft'"` attributes to form fields

### 2.3 Kanban Template Migration

Replaced deprecated `kanban-box` template with `card` template in all kanban views:

| File | Changes |
|------|---------|
| `views/seller_payment_view.xml` | 1 instance |
| `views/seller_view.xml` | 1 instance |
| `views/seller_shop_view.xml` | 1 instance |
| `views/res_partner_view.xml` | 1 instance |
| `views/mp_product_view.xml` | 2 instances |
| `views/mp_stock_view.xml` | 3 instances |
| `views/seller_review_view.xml` | 2 instances |
| `views/mp_sol_view.xml` | 1 instance |
| `views/mp_dashboard_view.xml` | 1 instance |

**Total:** 13 instances of `t-name="kanban-box"` → `t-name="card"`

### 2.4 Verification

After fixes, module loads without the following warnings:
- ✅ No more `readonly should be a boolean` warnings
- ✅ No more `required should be a boolean` warnings
- ✅ No more `states` parameter warnings
- ✅ No more `kanban-box` deprecation warnings

**Remaining (non-critical) warnings:**
- `DeprecationWarning: create method in batch` - Future improvement needed
- `no translation language detected` - Translation-related, non-blocking

---

## Fix 3: Kanban Image Function Deprecation (2026-01-28)

**Issue:** Kanban views threw JavaScript error when loading:
```
OwlError: An error occured in the owl lifecycle
Caused by: TypeError: ctx.kanban_image is not a function
```

**Root Cause:** Odoo 18 removed the `kanban_image()` JavaScript helper function that was used in kanban templates to render images. This function was used in multiple kanban views across the marketplace module.

**Solution:** Replaced all `kanban_image()` function calls with direct URL pattern `/web/image/{model}/{id}/{field}`:

```xml
<!-- OLD (deprecated) -->
<img t-att-src="kanban_image('res.partner', 'image_128', record.id.raw_value)"/>

<!-- NEW (Odoo 18 compatible) -->
<img t-attf-src="/web/image/res.partner/#{record.id.raw_value}/image_128"/>
```

**Files Modified:**

| File | Changes |
|------|---------|
| `views/seller_view.xml` | 1 image (seller avatar) |
| `views/seller_shop_view.xml` | 2 images (shop logo, seller avatar) |
| `views/mp_product_view.xml` | 4 images (product images, seller avatars) |

**Views Fixed:**
- `seller.kanban` (res.partner) - Sellers list
- `seller.shop.kanban` (seller.shop) - Shops list
- `Seller.Product.template.kanban` (product.template) - Seller products
- `product.product.kanban` (product.product) - Product variants

**URLs Fixed:**
- `/odoo/action-990` (Sellers)
- `/odoo/action-982` (Shop)
- `/odoo/action-994` (Seller Products)
- `/odoo/action-997` (Product Variants)

---

## Fix 4: Product Page 500 Error - _get_combination_info (2026-01-28)

**Issue:** All marketplace product pages (`/shop/<product>`) returned HTTP 500 error:
```
TypeError: ProductTemplate._get_combination_info() got an unexpected keyword argument 'pricelist'
Template: website_sale.product
```

**Root Cause:** In Odoo 18, the `_get_combination_info()` method signature changed - the `pricelist` parameter was removed. The marketplace module was still using the old Odoo 17 signature.

**Odoo 17 signature (old):**
```python
def _get_combination_info(self, combination=False, product_id=False, add_qty=1, pricelist=False, parent_combination=False, only_template=False):
```

**Odoo 18 signature (new):**
```python
def _get_combination_info(self, combination=False, product_id=False, add_qty=1.0, parent_combination=False, only_template=False):
```

**Solution:** Updated `models/marketplace_product.py` to use the new Odoo 18 signature:

```python
# OLD (line 337-340)
def _get_combination_info(self, combination=False, product_id=False, add_qty=1, pricelist=False, parent_combination=False, only_template=False):
    combination_info = super(ProductTemplate, self)._get_combination_info(
        combination=combination, product_id=product_id, add_qty=add_qty, pricelist=pricelist,
        parent_combination=parent_combination, only_template=only_template)

# NEW
def _get_combination_info(self, combination=False, product_id=False, add_qty=1.0, parent_combination=False, only_template=False):
    combination_info = super(ProductTemplate, self)._get_combination_info(
        combination=combination, product_id=product_id, add_qty=add_qty,
        parent_combination=parent_combination, only_template=only_template)
```

**File Modified:**
- `models/marketplace_product.py` (lines 337-340)

**URLs Fixed:**
- `/shop/phakkaad-raeknikh-68`
- `/shop/phaaethxmuulaaithy-72`
- `/shop/khnmchnhwaanman-70`
- All other marketplace product detail pages

---

*Updated by Claude Code on 2026-01-28*

## Fix 5: JavaScript Module System for Odoo 18 (2026-01-28)

**Issue:** Frequent JavaScript errors on the website:
```
UncaughtClientError: Module dependencies should be a list of strings, got: function(require){...}
```

**Root Cause:** The JavaScript files were using the legacy `odoo.define()` pattern from Odoo 14-16, which is incompatible with Odoo 18's ES6 module system.

**Solution:** Converted all JavaScript files from `odoo.define()` to ES6 module syntax.

**Files Modified:**

| File | Changes |
|------|---------|
| `static/src/js/review_chatter.js` | Removed `odoo.define()` wrapper, using plain jQuery |
| `static/src/js/seller_ratting.js` | Converted to ES6 module with `rpc` and `_t` imports |
| `static/src/js/marketplace.js` | Converted to ES6 module with `rpc` and `_t` imports |
| `static/src/js/url_handler.js` | Converted to ES6 module with `rpc` and `_t` imports |
| `static/src/js/activity_icon_hide.js` | Removed `odoo.defineCalled` hack, converted to ES6 module |
| `static/src/js/marketplace_snippets.js` | Using `publicWidget` from `@web/legacy/js/public/public_widget` |
| `static/src/js/marketplace_shop_editor.js` | Converted to ES6 module, added safety check for `options.registry.website_sale` |
| `static/src/js/tour.js` | Converted from `tour.register()` to `registry.category("web_tour.tours").add()` |

**Migration Pattern:**

```javascript
// OLD (Odoo 14-16)
odoo.define('module.name', function (require) {
    var ajax = require('web.ajax');
    var core = require('web.core');
    var _t = core._t;
    ajax.jsonRpc('/route', 'call', {params}).then(...);
});

// NEW (Odoo 18)
/** @odoo-module **/
import { rpc } from "@web/core/network/rpc";
import { _t } from "@web/core/l10n/translation";
rpc('/route', {params}).then(...);
```

**Key Import Changes:**

| Old (Odoo 14-16) | New (Odoo 18) |
|------------------|---------------|
| `odoo.define('name', function(require){...})` | `/** @odoo-module **/` + ES6 imports |
| `require('web.ajax')` | `import { rpc } from "@web/core/network/rpc"` |
| `require('web.core')._t` | `import { _t } from "@web/core/l10n/translation"` |
| `require('web.public.widget')` | `import publicWidget from "@web/legacy/js/public/public_widget"` |
| `require('web_tour.tour').register()` | `registry.category("web_tour.tours").add()` |
| `ajax.jsonRpc(route, 'call', params)` | `rpc(route, params)` |

**Notes:**
- `kanban_column.js` was already disabled/commented out for Odoo 18 compatibility
- Some deprecation warnings remain for `check_access_rights()` and `check_access_rule()` in Python code (non-critical)

---

## Fix 6: jQuery Plugin AMD Compatibility & Backend Module Fixes (2026-01-28)

**Issue:** Multiple JavaScript errors preventing login and backend functionality:
```
TypeError: $(...).timeago is not a function
modules are needed but have not been defined: ['jquery']
ReferenceError: $ is not defined
```

**Root Cause:**
1. jQuery plugins (`jquery.timeago.js`, `star-rating.js`) used AMD/UMD module patterns with `define(['jquery'], factory)` which Odoo 18 doesn't support
2. Backend JS files used `$` (jQuery) directly in `@odoo-module` modules, but jQuery is not available as a global in Odoo 18 backend
3. Legacy OWL 1.x patterns and old mail component imports incompatible with Odoo 18

**Solution:**

### 6.1 jQuery Plugin AMD Wrapper Removal

Removed AMD/UMD wrappers from jQuery plugins to use simple IIFE pattern:

| File | Old Pattern | New Pattern |
|------|-------------|-------------|
| `jquery.timeago.js` | `define(['jquery'], factory)` | `(function ($) { ... })(jQuery);` |
| `star-rating.js` | `define(['jquery'], factory)` | `(function ($) { ... })(jQuery);` |

### 6.2 Frontend Module Fix

**File:** `seller_ratting.js`

Moved `$("abbr.timeago").timeago()` call from outside to inside `$(document).ready()` with safety check:

```javascript
// OLD (line 452, outside document.ready)
$("abbr.timeago").timeago();

// NEW (inside document.ready)
if (typeof $.fn.timeago === 'function') {
    $("abbr.timeago").timeago();
}
```

### 6.3 Backend Module Rewrite

**File:** `url_handler.js`

Completely rewritten to use native DOM APIs instead of jQuery (jQuery not available in Odoo 18 backend):

```javascript
// OLD
$(document).on("input",".profile_url", function() {
    validate_profile_url($(this),'res.partner');
});

// NEW
document.addEventListener('input', function(e) {
    if (e.target.classList.contains('profile_url')) {
        validateProfileUrl(e.target, 'res.partner');
    }
});
```

**Key changes:**
- `$('.selector')` → `document.querySelector('.selector')`
- `$(el).addClass()` → `el.classList.add()`
- `$(el).removeClass()` → `el.classList.remove()`
- `$(el).val()` → `el.value`
- `$(el).html()` → `el.innerHTML`
- `$(el).show()/hide()` → `el.style.display = 'block'/'none'`

### 6.4 Disabled Legacy Backend JS

The following files were disabled in `__manifest__.py` as they require complete rewrites for OWL 2.x:

| File | Reason |
|------|--------|
| `kanban_column.js` | Uses `web.KanbanColumn`, `web.KanbanRenderer` (removed in Odoo 18) |
| `clickable_off.js` | Uses OWL 1.x `owl.hooks`, old `@mail/components/*` paths |
| `icon_restriction.js` | Uses `require('web.ajax')` mixed with ES6 imports |
| `activity_icon_hide.js` | Uses jQuery `$` in `@odoo-module` context |

**Manifest changes:**
```python
"web.assets_backend": [
    'odoo_marketplace/static/src/css/mp_dashboard.css',
    # Odoo 18: Disabled legacy JS files that need rewrite for OWL 2.x
    # 'odoo_marketplace/static/src/js/kanban_column.js',
    'odoo_marketplace/static/src/js/url_handler.js',
    # 'odoo_marketplace/static/src/js/clickable_off.js',
    # 'odoo_marketplace/static/src/js/icon_restriction.js',
    # 'odoo_marketplace/static/src/js/activity_icon_hide.js',
],
```

### 6.5 Functionality Impact

**Disabled features (need future OWL 2.x rewrite):**
- Hiding mail systray for sellers
- Partner click restrictions for sellers
- Debug menu restrictions for sellers
- Kanban drag/drop restrictions

**Working features:**
- URL handler validation in seller/shop forms
- Star ratings on seller profiles
- Timeago timestamps
- All frontend marketplace features

---

## Fix 7: Sellers List Page Layout Fix (2026-01-28)

**Issue:** The sellers list page (`/sellers/list/`) displayed incorrectly on desktop - layout was broken with items stacking vertically instead of showing as a grid.

**Root Cause:** The template used HTML `<table>` for grid layout, but Odoo 18's CSS expected CSS Grid. The existing CSS only had mobile styling (`max-width: 768px`) but no proper desktop grid layout.

**Solution:** Converted table-based layout to CSS Grid using `display: grid` and `display: contents`:

**File Modified:** `static/src/css/marketplace.css`

**CSS Changes:**

```css
/* Force table to behave as CSS Grid */
#sellers_grid table#seller_table {
    display: grid !important;
    width: 100% !important;
    gap: 16px !important;
}

#sellers_grid table#seller_table tbody,
#sellers_grid table#seller_table tr {
    display: contents !important;
}

#sellers_grid table#seller_table td {
    display: block !important;
    width: 100% !important;
}

/* Desktop - 2 columns */
@media (min-width: 992px) {
    #sellers_grid table#seller_table {
        grid-template-columns: repeat(2, 1fr) !important;
    }
}

/* Tablet - 2 columns */
@media (min-width: 768px) and (max-width: 991px) {
    #sellers_grid table#seller_table {
        grid-template-columns: repeat(2, 1fr) !important;
    }
}

/* Mobile - 1 column */
@media (max-width: 767px) {
    #sellers_grid table#seller_table td {
        display: block !important;
        width: 100% !important;
    }
}
```

**Layout Results:**
- **Desktop (992px+)**: 2 columns
- **Tablet (768-991px)**: 2 columns
- **Mobile (< 768px)**: 1 column

**URL Fixed:**
- `/sellers/list/`

---

## Fix 8: QWeb Template Rendering API Change (2026-01-28)

**Issue:** Seller profile pages returned RPC_ERROR with:
```
AttributeError: 'ir.ui.view' object has no attribute '_render'
```

**Root Cause:** In Odoo 18, the `ir.ui.view._render()` method was removed. The correct way to render QWeb templates is now through `ir.qweb._render()`.

**Solution:** Changed all template rendering calls from:
```python
# OLD (Odoo 17 and earlier)
request.env.ref('template.xml_id')._render(values)

# NEW (Odoo 18)
request.env['ir.qweb']._render('template.xml_id', values)
```

**File Modified:** `controllers/main.py`

**Changes (6 locations):**

| Line | Template | Route |
|------|----------|-------|
| 112 | `mp_t_and_c_modal_template` | `/mp/terms/and/conditions` |
| 359 | `shop_recently_product` | `/seller/profile/recently/product` |
| 646 | `shop_recently_product` | `/marketplace/seller/profile/recently/product` |
| 851 | `wk_seller_review_template` | `/seller/load/review` |
| 933 | `marketplace_order_line_info` | `/seller/order/line/info` |
| 941 | `mp_chatter_mail_append` | `/seller/order/message/fetch` |

---

## Fix 9: Translation Error in Rating Widget (2026-01-28)

**Issue:** JavaScript error on seller profile page:
```
Uncaught Error: translation error
    at LazyTranslatedString.valueOf
    at LazyTranslatedString.toString
    at String (<anonymous>)
```

**Root Cause:** In Odoo 18, the `_t()` function from `@web/core/l10n/translation` returns a `LazyTranslatedString` object instead of a regular string. This object requires the translation system to be fully initialized before it can be converted to a string.

The rating widget initialization in `$(document).ready()` runs before Odoo's translation system is ready, causing the error when trying to convert `_t()` results to strings.

**Solution:** Replaced `_t()` calls with plain English strings for the rating widget initialization, since this runs too early for the translation system.

**File Modified:** `static/src/js/seller_ratting.js`

**Change:**
```javascript
// OLD (line 31-35)
$("#rating-star").rating({
    clearCaption: String(_t('Not Rated')),
    starCaptions: {1: String(_t("Poor")), 2: String(_t("Ok")), 3: String(_t("Good")), 4: String(_t("Very Good")), 5: String(_t("Excellent"))},
    ...
});

// NEW
$("#rating-star").rating({
    clearCaption: 'Not Rated',
    starCaptions: {1: "Poor", 2: "Ok", 3: "Good", 4: "Very Good", 5: "Excellent"},
    ...
});
```

**Note:** Other `_t()` calls in event handlers (like `$('#btn-create-review').on('click', ...)`) are fine because they execute later when the user interacts, after the translation system is initialized.

**URL Fixed:**
- `/seller/profile/mae-boonmee-sweets#contact_us_tab`
- All seller profile pages with rating/review functionality

---

## Fix 10: Bootstrap 5 Tab/Modal Navigation (2026-01-29)

**Issue:** Tab navigation links on seller profile page were not working. Clicking on tabs like "All Products", "Recently Added Products", "Rating & Reviews", "Return Policy", "Shipping Policy", and "Seller Contact" did nothing.

**Root Cause:** The template used Bootstrap 4 data attributes (`data-toggle`, `data-target`, `data-dismiss`) but Odoo 18 uses Bootstrap 5, which requires different attribute names (`data-bs-toggle`, `data-bs-target`, `data-bs-dismiss`).

**Solution:** Updated all Bootstrap data attributes to Bootstrap 5 syntax:

| Old (Bootstrap 4) | New (Bootstrap 5) |
|-------------------|-------------------|
| `data-toggle="tab"` | `data-bs-toggle="tab"` |
| `data-toggle="modal"` | `data-bs-toggle="modal"` |
| `data-toggle="dropdown"` | `data-bs-toggle="dropdown"` |
| `data-target="#id"` | `data-bs-target="#id"` |
| `data-dismiss="modal"` | `data-bs-dismiss="modal"` |
| `class="close"` | `class="btn-close"` |

**Files Modified:**

### 1. `views/website_seller_profile_template.xml`

**Tab Navigation (6 tabs):**
- All Products tab
- Recently Added Products tab
- Rating & Reviews tab
- Return Policy tab
- Shipping Policy tab
- Seller Contact tab

**Modals:**
- Login prompt modal (`#loginfeed`)
- Write review modal (`#exampleModal`)

**Dropdowns:**
- Sort By dropdown (Most Recent/Most Helpful)
- Filter By dropdown (All Stars/5-1 star)

### 2. `views/website_seller_shop_template.xml`

**Tab Navigation (3 tabs):**
- All Products tab
- Recently Added Products tab
- Store T&C tab

**Modal:**
- Login prompt modal (`#loginfeed`)

### 3. `views/website_account_template.xml`

**Modal:**
- Terms & Conditions modal (`#mp_t_and_c_modal`)

**Close Button Changes:**
Bootstrap 5 uses a dedicated `btn-close` class instead of `close` class with `&times;` content:

```html
<!-- OLD (Bootstrap 4) -->
<button type="button" class="close" data-dismiss="modal" aria-label="Close">
    <span aria-hidden="true">&times;</span>
</button>

<!-- NEW (Bootstrap 5) -->
<button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close">
</button>
```

**URLs Fixed:**
- `/seller/profile/<url_handler>` - All seller profile pages
- `/seller/shop/<url_handler>` - All shop pages
- `/my/marketplace` - Seller registration page

---

*Updated by Claude Code on 2026-01-29*
