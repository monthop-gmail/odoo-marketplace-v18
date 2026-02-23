# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class LineLiff(models.Model):
    """
    LINE LIFF (LINE Front-end Framework) App
    Each LINE OA can have up to 30 LIFF apps
    Different LIFF apps can serve different purposes (buyer, seller, admin, etc.)
    """
    _name = 'line.liff'
    _description = 'LINE LIFF App'
    _order = 'sequence, name'
    _rec_name = 'name'

    name = fields.Char(
        string='LIFF Name',
        required=True,
        help='Display name for this LIFF app (e.g., Buyer App, Seller Dashboard)',
    )
    liff_id = fields.Char(
        string='LIFF ID',
        required=True,
        index=True,
        help='LIFF ID from LINE Developers Console (e.g., 1234567890-abcdefgh)',
    )
    liff_url = fields.Char(
        string='LIFF URL',
        compute='_compute_liff_url',
        store=True,
        help='Full LIFF URL for opening this app',
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10,
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )

    # Link to Channel
    channel_id = fields.Many2one(
        'line.channel',
        string='LINE Channel',
        required=True,
        ondelete='cascade',
        index=True,
    )
    channel_code = fields.Char(
        related='channel_id.code',
        store=True,
        string='Channel Code',
    )

    # LIFF Type - role-based LIFF apps for dynamic single LINE OA
    liff_type = fields.Selection([
        ('general', 'General'),
        ('buyer', 'Buyer'),
        ('seller', 'Seller'),
        ('admin', 'Admin'),
        ('promotion', 'Promotion'),
        ('support', 'Support'),
    ], string='LIFF Type', required=True, default='general',
       help='Purpose of this LIFF app. Determines which role sees this app.')

    # LIFF Size (as configured in LINE Developers Console)
    liff_size = fields.Selection([
        ('full', 'Full'),
        ('tall', 'Tall'),
        ('compact', 'Compact'),
    ], string='LIFF Size', default='full',
       help='LIFF display size. Full=100%, Tall=~80%, Compact=50%')

    # Endpoint Configuration
    endpoint_url = fields.Char(
        string='Endpoint URL',
        help='Your app endpoint URL (hosted on your server)',
    )

    # Features enabled for this LIFF
    feature_browse_products = fields.Boolean(
        string='Browse Products',
        default=True,
        help='Enable product browsing feature',
    )
    feature_cart = fields.Boolean(
        string='Shopping Cart',
        default=True,
        help='Enable shopping cart feature',
    )
    feature_checkout = fields.Boolean(
        string='Checkout',
        default=True,
        help='Enable checkout feature',
    )
    feature_order_history = fields.Boolean(
        string='Order History',
        default=True,
        help='Enable order history feature',
    )
    feature_profile = fields.Boolean(
        string='Profile Management',
        default=True,
        help='Enable profile and address management',
    )

    # Description and Notes
    description = fields.Text(
        string='Description',
        help='Description of this LIFF app purpose',
    )
    notes = fields.Text(
        string='Internal Notes',
    )

    # Statistics
    access_count = fields.Integer(
        string='Access Count',
        default=0,
        help='Number of times this LIFF has been accessed',
    )
    last_access_date = fields.Datetime(
        string='Last Access',
    )

    _sql_constraints = [
        ('liff_id_uniq', 'unique(liff_id)', 'LIFF ID must be unique!'),
        # Note: Removed channel_type_uniq to allow multiple LIFFs of same type
        # Business modules can enforce their own constraints if needed
    ]

    @api.depends('liff_id')
    def _compute_liff_url(self):
        for record in self:
            if record.liff_id:
                record.liff_url = f'https://liff.line.me/{record.liff_id}'
            else:
                record.liff_url = False

    @api.constrains('liff_id')
    def _check_liff_id(self):
        for record in self:
            if record.liff_id:
                # LIFF ID format: numbers-alphanumeric (e.g., 1234567890-AbCdEfGh)
                parts = record.liff_id.split('-')
                if len(parts) != 2:
                    raise ValidationError(
                        _('LIFF ID should be in format: 1234567890-AbCdEfGh')
                    )

    def action_open_liff(self):
        """Open LIFF URL in browser (for testing)"""
        self.ensure_one()
        if not self.liff_url:
            raise ValidationError(_('LIFF URL is not configured.'))
        return {
            'type': 'ir.actions.act_url',
            'url': self.liff_url,
            'target': 'new',
        }

    def action_copy_url(self):
        """Copy LIFF URL to clipboard (handled by JS)"""
        self.ensure_one()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('LIFF URL'),
                'message': self.liff_url,
                'type': 'info',
                'sticky': False,
            }
        }

    @api.model
    def get_liff_by_type(self, channel_id, liff_type):
        """
        Get LIFF app by channel and type.
        Useful for API to get the correct LIFF for a specific purpose.

        Args:
            channel_id: int - ID of line.channel
            liff_type: str - Type of LIFF (buyer, seller, admin, etc.)

        Returns:
            line.liff record or False
        """
        return self.search([
            ('channel_id', '=', channel_id),
            ('liff_type', '=', liff_type),
            ('active', '=', True),
        ], limit=1)

    @api.model
    def get_liff_config(self, liff_id):
        """
        Get LIFF configuration by LIFF ID.
        Called from LIFF app to get enabled features.

        Args:
            liff_id: str - LIFF ID

        Returns:
            dict with LIFF configuration
        """
        liff = self.search([('liff_id', '=', liff_id)], limit=1)
        if not liff:
            return {'error': 'LIFF not found'}

        return {
            'liff_id': liff.liff_id,
            'liff_type': liff.liff_type,
            'liff_size': liff.liff_size,
            'channel_code': liff.channel_code,
            'features': {
                'browse_products': liff.feature_browse_products,
                'cart': liff.feature_cart,
                'checkout': liff.feature_checkout,
                'order_history': liff.feature_order_history,
                'profile': liff.feature_profile,
            },
        }

    def log_access(self):
        """Log LIFF access (called from API)"""
        self.ensure_one()
        self.sudo().write({
            'access_count': self.access_count + 1,
            'last_access_date': fields.Datetime.now(),
        })
