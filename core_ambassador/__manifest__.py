# -*- coding: utf-8 -*-
{
    'name': 'Core Ambassador',
    'version': '18.0.1.0.0',
    'category': 'Website',
    'summary': 'Brand Ambassador (สภา shop) - Guru Endorsement System',
    'description': """
Brand Ambassador / Guru system for marketplace product endorsement.
Ambassadors review and endorse products to build buyer trust.
Includes application workflow, endorsement management, and tiered commission structure.
    """,
    'author': 'EV Marketplace Team',
    'license': 'LGPL-3',
    'depends': [
        'core_marketplace',
        'core_line_integration',
    ],
    'data': [
        # Security (load first)
        'security/ambassador_security.xml',
        'security/ir.model.access.csv',

        # Data
        'data/ambassador_sequence_data.xml',
        'data/ambassador_specialty_data.xml',
        'data/ir_config_parameter_data.xml',

        # Views
        'views/ambassador_specialty_views.xml',
        'views/ambassador_application_views.xml',
        'views/ambassador_views.xml',
        'views/product_endorsement_views.xml',
        'views/endorsement_request_views.xml',
        'views/ambassador_menu_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
