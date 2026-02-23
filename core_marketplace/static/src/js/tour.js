/** @odoo-module **/

/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : https://store.webkul.com/license.html/ */

import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";

registry.category("web_tour.tours").add("marketplace_tour", {
    url: "/web",
    steps: () => [{
        trigger: '.o_app[data-menu-xmlid="core_marketplace.wk_seller_dashboard"], .oe_menu_toggler[data-menu-xmlid="core_marketplace.wk_seller_dashboard"]',
        content: _t('Manage your marketplace activities from here.'),
        position: 'bottom',
    },
    {
        trigger: '.pending_seller_tooltip',
        content: _t('Visit pending sellers from here.'),
        position: 'left',
    }],
});

registry.category("web_tour.tours").add("marketplace_tour2", {
    url: "/web",
    steps: () => [{
        trigger: 'li a[data-menu-xmlid="core_marketplace.wk_seller_dashboard_menu2_sub_menu0"], div[data-menu-xmlid="core_marketplace.wk_seller_dashboard_menu2_sub_menu0"]',
        content: _t('Seller can create new product from here.'),
        position: 'bottom',
    }],
});

registry.category("web_tour.tours").add("marketplace_tour3", {
    url: "/web",
    steps: () => [{
        trigger: '.pending_product_tooltip',
        content: _t('Visit marketplace pending products from here.'),
        position: 'left',
    }],
});

registry.category("web_tour.tours").add("marketplace_tour4", {
    url: "/web",
    steps: () => [{
        trigger: 'li a[data-menu-xmlid="core_marketplace.wk_seller_dashboard_menu1_sub_menu1"], div[data-menu-xmlid="core_marketplace.wk_seller_dashboard_menu1_sub_menu1"]',
        content: _t('Visit all marketplace seller profiles from here.'),
        position: 'bottom',
    }],
});
