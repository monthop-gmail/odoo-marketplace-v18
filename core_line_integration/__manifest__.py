# -*- coding: utf-8 -*-
{
    'name': 'Core LINE Integration',
    'version': '18.0.1.0.0',
    'category': 'Sales',
    'summary': 'LINE OA Marketplace Integration - ระบบเชื่อมต่อ LINE สำหรับ Marketplace',
    'description': """
Core LINE Integration
=====================
This module provides LINE OA integration for marketplace (buyers, sellers, admins):

Features:
---------
* Multiple LINE OA (Channel) support
* Buyer registration and shopping via LINE
* Seller dashboard and product management via LINE
* Admin management via LINE
* Order notifications via LINE
* Product browsing API for LIFF
* Cart and Checkout API
* Seller and Admin REST APIs
* Wallet and Withdrawal system
* Order history via LINE
* Webhook handling
* Rich Menu management (role-based)
* Flex Message templates
* Dynamic role switching (buyer/seller/admin)

Supports multiple business types through a single LINE Official Account.
    """,
    'author': 'Core Development Team',
    'website': '',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'sale',
        'website_sale',
        'core_marketplace',
    ],
    'data': [
        # Security
        'security/line_buyer_security.xml',
        'security/ir.model.access.csv',
        # Data
        'data/line_channel_data.xml',
        'data/cron_data.xml',
        'data/thai_province_data.xml',
        # Reports
        'report/shipping_label_report.xml',
        # Wizard
        'wizard/sale_order_ship_wizard_views.xml',
        'wizard/line_message_wizard_views.xml',
        # Views
        'views/line_channel_views.xml',
        'views/line_liff_views.xml',
        'views/line_channel_member_views.xml',
        'views/res_partner_views.xml',
        'views/sale_order_views.xml',
        'views/shipping_dashboard_views.xml',
        'views/res_config_settings_views.xml',
        'views/menu_views.xml',
        'views/line_rich_menu_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            # Backend assets if needed
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
