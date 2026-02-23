/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : https://store.webkul.com/license.html/ */

/** @odoo-module **/

import { rpc } from "@web/core/network/rpc";
import { _t } from "@web/core/l10n/translation";

function validateProfileUrl(inputEl, model) {
    const profileUrl = inputEl.value.trim();
    const profileSpan = document.querySelector('.url_validation');
    const profileOrShopIdEl = document.querySelector('.profile_or_shop_id');
    const profileOrShopId = profileOrShopIdEl ? parseInt(profileOrShopIdEl.textContent, 10) : 0;
    const errorEl = document.getElementById('profile_url_error');

    if (!profileSpan || !errorEl) return;

    // Remove previous classes
    profileSpan.classList.remove('fa-pencil', 'fa-times', 'fa-check', 'fa-spinner', 'fa-pulse');

    if (profileUrl !== '' && /^[0-9]+$/.test(profileUrl)) {
        inputEl.classList.add('url-error');
        errorEl.innerHTML = _t('URL handler must contain at least 1 letter (a-z). Only alphanumeric ([0-9],[a-z]) and some special characters (-,_) are allowed.');
        errorEl.style.display = 'block';
    } else if (profileUrl !== '' && !/^[a-zA-Z0-9-_]+$/.test(profileUrl)) {
        inputEl.classList.add('url-error');
        errorEl.innerHTML = _t('Only alphanumeric ([0-9],[a-z]) and some special characters (-,_) are allowed. Spaces are not allowed.');
        errorEl.style.display = 'block';
    } else if (profileUrl !== '' && (/^[-_]/.test(profileUrl) || /[-_]$/.test(profileUrl))) {
        inputEl.classList.add('url-error');
        errorEl.innerHTML = _t('Special characters are not allowed at the beginning or end of the string.');
        errorEl.style.display = 'block';
    } else {
        profileSpan.classList.add('fa-spinner', 'fa-pulse');
        rpc("/profile/url/handler/vaidation", {
            'url_handler': profileUrl,
            'model': model,
            'profile_or_shop_id': profileOrShopId
        }).then(function(vals) {
            profileSpan.classList.remove('fa-spinner', 'fa-pulse');
            if (vals && profileUrl !== '') {
                inputEl.classList.remove('url-error');
                inputEl.classList.add('url-success');
                profileSpan.classList.add('fa-check');
                errorEl.style.display = 'none';
            } else {
                inputEl.classList.remove('url-success');
                inputEl.classList.add('url-error');
                profileSpan.classList.add('fa-times');
                if (profileUrl !== '') {
                    errorEl.innerHTML = _t('Sorry, this profile URL is not available.');
                } else {
                    errorEl.innerHTML = _t('Please enter your profile URL.');
                }
                errorEl.style.display = 'block';
            }
        });
    }
}

// Use event delegation on document
document.addEventListener('input', function(e) {
    if (e.target.classList.contains('profile_url')) {
        validateProfileUrl(e.target, 'res.partner');
    } else if (e.target.classList.contains('seller_shop_url')) {
        validateProfileUrl(e.target, 'seller.shop');
    }
});
