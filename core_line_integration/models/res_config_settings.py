# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    """
    LINE Marketplace configuration settings
    """
    _inherit = 'res.config.settings'

    # Default LINE Channel
    line_buyer_default_channel_id = fields.Many2one(
        'line.channel',
        string='Default LINE Channel',
        config_parameter='core_line_integration.default_channel_id',
        help='Default LINE channel for new buyers',
    )

    # API Settings
    line_buyer_api_enabled = fields.Boolean(
        string='Enable Marketplace API',
        config_parameter='core_line_integration.api_enabled',
        default=True,
        help='Enable REST API endpoints for LINE marketplace apps',
    )
    line_buyer_api_debug = fields.Boolean(
        string='API Debug Mode',
        config_parameter='core_line_integration.api_debug',
        default=False,
        help='Enable debug logging for API requests',
    )

    # Mock Authentication (for local testing)
    line_buyer_mock_auth = fields.Boolean(
        string='Mock Authentication',
        config_parameter='core_line_integration.mock_auth',
        default=True,
        help='Enable mock authentication for local testing without LINE',
    )

    # Notification Settings
    line_auto_notify_order = fields.Boolean(
        string='Auto Notify on Order',
        config_parameter='core_line_integration.auto_notify_order',
        default=True,
        help='Automatically send LINE notification when order is confirmed',
    )
    line_auto_notify_shipping = fields.Boolean(
        string='Auto Notify on Shipping',
        config_parameter='core_line_integration.auto_notify_shipping',
        default=True,
        help='Automatically send LINE notification when order is shipped',
    )

    # Cross-Channel Shopping
    allow_cross_channel_purchase = fields.Boolean(
        string='Allow Cross-Channel Purchase',
        config_parameter='core_line_integration.cross_channel_purchase',
        default=True,
        help='Allow buyers from one LINE channel to purchase from sellers of another channel',
    )
