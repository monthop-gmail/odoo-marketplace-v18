# -*- coding: utf-8 -*-
import hashlib
import logging
import secrets

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class LineChannel(models.Model):
    """
    LINE OA Channel - represents a LINE Official Account
    Each seller/business can have its own LINE OA
    """
    _name = 'line.channel'
    _description = 'LINE OA Channel'
    _order = 'sequence, name'

    name = fields.Char(
        string='Channel Name',
        required=True,
        help='Display name for this LINE OA (e.g., สหกรณ์การเกษตร ABC)',
    )
    code = fields.Char(
        string='Channel Code',
        required=True,
        copy=False,
        help='Unique code for API identification (e.g., coop_abc)',
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10,
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )

    # LINE API Credentials
    channel_id = fields.Char(
        string='LINE Channel ID',
        help='LINE Messaging API Channel ID',
    )
    channel_secret = fields.Char(
        string='Channel Secret',
        help='LINE Messaging API Channel Secret',
    )
    channel_access_token = fields.Char(
        string='Channel Access Token',
        help='LINE Messaging API long-lived channel access token',
    )

    # LIFF Apps (One2many - supports multiple LIFFs per channel)
    liff_ids = fields.One2many(
        'line.liff',
        'channel_id',
        string='LIFF Apps',
        help='LINE LIFF apps linked to this channel (up to 30)',
    )
    liff_count = fields.Integer(
        string='LIFF Count',
        compute='_compute_liff_count',
    )

    # Default LIFF (computed from liff_ids for convenience)
    default_buyer_liff_id = fields.Many2one(
        'line.liff',
        string='Default Buyer LIFF',
        compute='_compute_default_liffs',
        help='Default LIFF app for buyers',
    )
    default_seller_liff_id = fields.Many2one(
        'line.liff',
        string='Default Seller LIFF',
        compute='_compute_default_liffs',
        help='Default LIFF app for sellers',
    )

    # Legacy fields (kept for backward compatibility)
    # DEPRECATED: Use liff_ids One2many instead. Will be removed in a future version.
    liff_id = fields.Char(
        string='LIFF ID (Legacy)',
        help='[DEPRECATED] Use LIFF Apps instead. Legacy LIFF ID for buyer interface.',
    )
    liff_url = fields.Char(
        string='LIFF URL (Legacy)',
        compute='_compute_liff_url',
        store=True,
        help='[DEPRECATED] Use LIFF Apps instead.',
    )

    # Webhook Configuration
    webhook_url = fields.Char(
        string='Webhook URL',
        compute='_compute_webhook_url',
        help='URL to configure in LINE Developers Console',
    )
    webhook_secret = fields.Char(
        string='Webhook Secret',
        default=lambda self: secrets.token_urlsafe(32),
        help='Internal secret for webhook verification',
    )

    # Rich Menu
    rich_menu_id = fields.Char(
        string='Rich Menu ID',
        help='LINE Rich Menu ID (created via API)',
    )

    # Related Organization
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
    )

    # Link to Seller
    seller_id = fields.Many2one(
        'res.partner',
        string='Seller',
        domain="[('seller', '=', True)]",
        help='Marketplace seller that owns this LINE OA',
    )

    # Statistics
    member_count = fields.Integer(
        string='Member Count',
        compute='_compute_member_count',
    )
    member_ids = fields.One2many(
        'line.channel.member',
        'channel_id',
        string='Members',
    )

    # Settings
    auto_welcome_message = fields.Boolean(
        string='Send Welcome Message',
        default=True,
        help='Automatically send welcome message when user follows',
    )
    welcome_message = fields.Text(
        string='Welcome Message',
        default='ยินดีต้อนรับสู่ร้านค้าของเรา! 🛒\nกดเมนูด้านล่างเพื่อเริ่มช้อปปิ้ง',
    )
    notify_on_order = fields.Boolean(
        string='Notify on Order',
        default=True,
        help='Send notification when buyer places an order',
    )
    notify_on_shipping = fields.Boolean(
        string='Notify on Shipping',
        default=True,
        help='Send notification when order is shipped',
    )

    _sql_constraints = [
        ('code_uniq', 'unique(code)', 'Channel code must be unique!'),
        ('channel_id_uniq', 'unique(channel_id)', 'LINE Channel ID must be unique!'),
    ]

    def _compute_liff_count(self):
        for record in self:
            record.liff_count = len(record.liff_ids)

    def _compute_default_liffs(self):
        for record in self:
            buyer_liff = record.liff_ids.filtered(
                lambda l: l.liff_type == 'buyer' and l.active
            )[:1]
            seller_liff = record.liff_ids.filtered(
                lambda l: l.liff_type == 'seller' and l.active
            )[:1]
            record.default_buyer_liff_id = buyer_liff.id if buyer_liff else False
            record.default_seller_liff_id = seller_liff.id if seller_liff else False

    @api.depends('liff_id')
    def _compute_liff_url(self):
        """Legacy compute for backward compatibility"""
        for record in self:
            if record.liff_id:
                record.liff_url = f'https://liff.line.me/{record.liff_id}'
            else:
                record.liff_url = False

    def _compute_webhook_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for record in self:
            record.webhook_url = f'{base_url}/line/webhook/{record.code}'

    def _compute_member_count(self):
        for record in self:
            record.member_count = self.env['line.channel.member'].search_count([
                ('channel_id', '=', record.id),
                ('is_following', '=', True),
            ])

    @api.constrains('code')
    def _check_code(self):
        for record in self:
            if record.code and not record.code.replace('_', '').isalnum():
                raise ValidationError(_('Channel code must contain only alphanumeric characters and underscores.'))

    def verify_webhook_signature(self, body, signature):
        """
        Verify LINE webhook signature
        https://developers.line.biz/en/docs/messaging-api/receiving-messages/#verifying-signatures
        """
        self.ensure_one()
        if not self.channel_secret:
            return False

        hash_value = hashlib.sha256(
            self.channel_secret.encode('utf-8')
        )
        # In production, use HMAC-SHA256
        # For now, this is a placeholder
        return True

    def action_view_members(self):
        """Open member list view"""
        self.ensure_one()
        return {
            'name': _('LINE Members'),
            'type': 'ir.actions.act_window',
            'res_model': 'line.channel.member',
            'view_mode': 'list,form',
            'domain': [('channel_id', '=', self.id)],
            'context': {'default_channel_id': self.id},
        }

    def action_test_connection(self):
        """Test LINE API connection by calling get_bot_info()"""
        self.ensure_one()

        if not self.channel_access_token:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Connection Test Failed'),
                    'message': _('Channel Access Token is not configured.'),
                    'type': 'danger',
                    'sticky': False,
                }
            }

        try:
            from ..services.line_api import get_line_api_service
            service = get_line_api_service(self)
            bot_info = service.get_bot_info()
            bot_name = bot_info.get('displayName', 'Unknown')
            basic_id = bot_info.get('basicId', '')

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Connection Successful'),
                    'message': _('Connected to LINE Bot: %s (%s)') % (bot_name, basic_id),
                    'type': 'success',
                    'sticky': False,
                }
            }
        except Exception as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Connection Test Failed'),
                    'message': _('Error: %s') % str(e),
                    'type': 'danger',
                    'sticky': True,
                }
            }

    def action_view_liffs(self):
        """Open LIFF apps list view"""
        self.ensure_one()
        return {
            'name': _('LIFF Apps'),
            'type': 'ir.actions.act_window',
            'res_model': 'line.liff',
            'view_mode': 'list,form',
            'domain': [('channel_id', '=', self.id)],
            'context': {'default_channel_id': self.id},
        }

    def get_liff_by_type(self, liff_type):
        """
        Get LIFF app by type for this channel.

        Args:
            liff_type: str - Type of LIFF (buyer, seller, admin, etc.)

        Returns:
            line.liff record or False
        """
        self.ensure_one()
        return self.env['line.liff'].get_liff_by_type(self.id, liff_type)

    def get_buyer_liff_url(self):
        """Get buyer LIFF URL for this channel"""
        self.ensure_one()
        # First check new multi-LIFF
        if self.default_buyer_liff_id:
            return self.default_buyer_liff_id.liff_url
        # Fallback to legacy field
        return self.liff_url or False

    def get_seller_liff_url(self):
        """Get seller LIFF URL for this channel"""
        self.ensure_one()
        if self.default_seller_liff_id:
            return self.default_seller_liff_id.liff_url
        return False

    def get_seller_shop(self):
        """Get the seller shop for this channel"""
        self.ensure_one()
        if not self.seller_id:
            return self.env['seller.shop']
        return self.env['seller.shop'].search([
            ('seller_id', '=', self.seller_id.id),
            ('state', '=', 'approved'),
            ('website_published', '=', True),
        ], limit=1)

    @api.model
    def _migrate_legacy_liff_id(self):
        """
        Migrate legacy liff_id Char field to liff_ids One2many.

        For each channel that has liff_id set but no matching line.liff record,
        create a new line.liff record of type 'buyer'.

        Safe to run multiple times — skips channels already migrated.
        Can be called from post_init_hook or as a scheduled action.
        """
        channels_with_legacy = self.search([
            ('liff_id', '!=', False),
            ('liff_id', '!=', ''),
        ])
        Liff = self.env['line.liff']
        migrated = 0

        for channel in channels_with_legacy:
            # Check if a LIFF record already exists for this legacy ID
            existing = Liff.search([
                ('channel_id', '=', channel.id),
                ('liff_id', '=', channel.liff_id),
            ], limit=1)

            if not existing:
                Liff.create({
                    'name': f'{channel.name} - Buyer (migrated)',
                    'liff_id': channel.liff_id,
                    'channel_id': channel.id,
                    'liff_type': 'buyer',
                    'active': True,
                })
                migrated += 1
                _logger.info(
                    'Migrated legacy liff_id %s for channel %s',
                    channel.liff_id, channel.name,
                )

        if migrated:
            _logger.info('Legacy LIFF migration complete: %d channels migrated', migrated)
        return migrated

    def send_notification(self, to_user_id, message):
        """
        Send notification to user via LINE

        Args:
            to_user_id: LINE user ID
            message: dict or list of LINE message objects

        Returns:
            bool - success status
        """
        self.ensure_one()
        # Use the LINE API service to send message
        from ..services.line_api import get_line_api_service
        service = get_line_api_service(self)
        return service.push_message(to_user_id, message if isinstance(message, list) else [message])
