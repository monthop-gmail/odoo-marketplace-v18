/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : https://store.webkul.com/license.html/ */

/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { rpc } from "@web/core/network/rpc";

publicWidget.registry.wkMarketplaceSnippets = publicWidget.Widget.extend({
    selector: '#open_store_button',

    start: function () {
        var self = this;
        this._fetch().then(function(result){
            self.$el.html(result);
        });
        return this._super.apply(this, arguments);
    },
    _fetch: function () {
        return rpc('/add/header/button', {}).then(function(res) {
            if (res.route === false){
                return '';
            }
            var store_btn_el = '<a href="' + res.route + '" class="btn" style="font-weight:600;background:#3BD3F4;border-radius: 2px;color:#fff;text-transform: uppercase;">' + res.btn_content + '</a>';
            return store_btn_el;
        });
    },
});

export default publicWidget.registry.wkMarketplaceSnippets;
