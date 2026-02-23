# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    """
    Extend res.partner with LINE-related fields
    """
    _inherit = 'res.partner'

    # LINE User Info
    line_user_id = fields.Char(
        string='LINE User ID',
        index=True,
        help='Primary LINE user ID for this contact',
    )
    line_display_name = fields.Char(
        string='LINE Display Name',
        help='Display name from LINE profile',
    )
    line_picture_url = fields.Char(
        string='LINE Picture URL',
        help='Profile picture URL from LINE',
    )

    # LINE Channel Memberships
    line_member_ids = fields.One2many(
        'line.channel.member',
        'partner_id',
        string='LINE Memberships',
    )
    line_channel_count = fields.Integer(
        string='LINE Channels',
        compute='_compute_line_stats',
    )

    # Primary LINE Channel (for notifications)
    primary_line_channel_id = fields.Many2one(
        'line.channel',
        string='Primary LINE Channel',
        help='Default LINE channel for sending notifications',
    )

    # Notification Preferences
    line_notify_orders = fields.Boolean(
        string='Order Notifications',
        default=True,
        help='Receive order status updates via LINE',
    )
    line_notify_promotions = fields.Boolean(
        string='Promotion Notifications',
        default=True,
        help='Receive promotional messages via LINE',
    )

    # Source Tracking
    source_channel = fields.Selection([
        ('web', 'Website'),
        ('line', 'LINE'),
        ('pos', 'Point of Sale'),
        ('import', 'Import'),
        ('manual', 'Manual'),
    ], string='Source Channel', default='manual')

    source_line_channel_id = fields.Many2one(
        'line.channel',
        string='Source LINE Channel',
        help='The LINE channel where this customer was acquired',
    )

    @api.depends('line_member_ids')
    def _compute_line_stats(self):
        for record in self:
            record.line_channel_count = len(record.line_member_ids.filtered('is_following'))

    @api.model
    def get_or_create_from_line(self, line_user_id, channel_id, profile_data=None):
        """
        Get existing partner or create new one from LINE data.

        Args:
            line_user_id: str - LINE user ID
            channel_id: int - line.channel ID
            profile_data: dict - {display_name, picture_url, ...}

        Returns:
            res.partner record
        """
        # Use tracking_disable context for API calls without login session
        ctx = dict(
            tracking_disable=True,
            mail_create_nosubscribe=True,
            mail_auto_subscribe_no_notify=True,
        )
        Partner = self.with_context(**ctx)

        # Check if partner exists with this LINE user ID
        partner = Partner.search([
            ('line_user_id', '=', line_user_id),
        ], limit=1)

        if partner:
            # Update profile data if provided
            if profile_data:
                update_vals = {}
                if profile_data.get('display_name') and not partner.name.startswith('LINE User'):
                    pass  # Don't override if name was manually set
                elif profile_data.get('display_name'):
                    update_vals['name'] = profile_data['display_name']
                    update_vals['line_display_name'] = profile_data['display_name']
                if profile_data.get('picture_url'):
                    update_vals['line_picture_url'] = profile_data['picture_url']
                if update_vals:
                    partner.with_context(**ctx).write(update_vals)
        else:
            # Create new partner
            name = 'LINE User'
            if profile_data and profile_data.get('display_name'):
                name = profile_data['display_name']

            partner = Partner.create({
                'name': name,
                'line_user_id': line_user_id,
                'line_display_name': profile_data.get('display_name') if profile_data else None,
                'line_picture_url': profile_data.get('picture_url') if profile_data else None,
                'source_channel': 'line',
                'source_line_channel_id': channel_id,
                'primary_line_channel_id': channel_id,
                'customer_rank': 1,
            })

        return partner

    def action_view_line_memberships(self):
        """View LINE channel memberships"""
        self.ensure_one()
        return {
            'name': 'LINE Memberships',
            'type': 'ir.actions.act_window',
            'res_model': 'line.channel.member',
            'view_mode': 'list,form',
            'domain': [('partner_id', '=', self.id)],
            'context': {'default_partner_id': self.id},
        }

    def action_send_line_message(self):
        """Open wizard to send LINE message to this partner"""
        self.ensure_one()
        return {
            'name': 'Send LINE Message',
            'type': 'ir.actions.act_window',
            'res_model': 'line.message.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_partner_id': self.id,
            },
        }

    # ===========================================
    # Dynamic Role Switching (Single LINE OA)
    # ===========================================

    def write(self, vals):
        """
        Override write to detect seller state changes and sync LINE member role.

        When seller state changes:
        - approved → member_type='seller', assign seller rich menu, send LINE notification
        - denied → member_type='buyer', assign buyer rich menu, send LINE notification
        - pending → send LINE notification (role stays buyer)
        """
        # Capture old states before write
        state_changes = {}
        if vals.get('state') and any(
            hasattr(r, 'seller') and r.seller for r in self
        ):
            for partner in self.filtered(
                lambda p: hasattr(p, 'seller') and p.seller
            ):
                old_state = partner.state
                new_state = vals['state']
                if old_state != new_state:
                    state_changes[partner.id] = {
                        'old_state': old_state,
                        'new_state': new_state,
                    }

        res = super().write(vals)

        # Process state changes — sync LINE member role
        if state_changes:
            self._sync_line_roles_on_state_change(state_changes)

        return res

    def _sync_line_roles_on_state_change(self, state_changes):
        """
        Sync LINE channel member roles after seller state changes.

        Args:
            state_changes: dict {partner_id: {'old_state': str, 'new_state': str}}
        """
        Member = self.env['line.channel.member'].sudo()

        for partner_id, change in state_changes.items():
            partner = self.browse(partner_id)
            new_state = change['new_state']

            # Find all LINE members linked to this partner
            members = Member.search([
                ('partner_id', '=', partner_id),
                ('is_following', '=', True),
            ])

            if not members:
                _logger.debug(
                    'No LINE members found for partner %s, skipping role sync',
                    partner_id,
                )
                continue

            for member in members:
                old_type = member.member_type

                # Sync member_type from partner role
                member.sync_member_type_from_partner()

                # Assign role-specific rich menu
                member.assign_role_rich_menu()

                # Send notification via LINE
                member.send_role_change_notification(
                    old_type, member.member_type,
                    seller_state=new_state,
                )

            _logger.info(
                'Seller %s (ID: %s) state → %s, synced %d LINE members',
                partner.name, partner_id, new_state, len(members),
            )

    # ===========================================
    # Shipping Address Management
    # ===========================================

    is_default_shipping = fields.Boolean(
        string='Default Shipping Address',
        default=False,
        help='Use this as default shipping address',
    )

    def get_shipping_addresses(self):
        """
        Get all shipping addresses for this partner.

        Returns:
            recordset of delivery addresses (child partners with type='delivery')
        """
        self.ensure_one()

        # Get child delivery addresses
        addresses = self.child_ids.filtered(lambda p: p.type == 'delivery' and p.active)

        return addresses

    def get_default_shipping_address(self):
        """
        Get default shipping address for this partner.

        Returns:
            res.partner record or False
        """
        self.ensure_one()

        # First try to find marked default
        default = self.child_ids.filtered(
            lambda p: p.type == 'delivery' and p.active and p.is_default_shipping
        )
        if default:
            return default[0]

        # Otherwise return first shipping address
        addresses = self.get_shipping_addresses()
        return addresses[0] if addresses else False

    def create_shipping_address(self, address_data):
        """
        Create a new shipping address for this partner.

        Args:
            address_data: dict with address fields
                - name: Recipient name
                - phone: Phone number
                - street: Address line 1
                - street2: Address line 2 (optional)
                - city: District/City (อำเภอ)
                - state_id: Province ID (จังหวัด)
                - zip: Postal code
                - is_default: Set as default (optional)

        Returns:
            res.partner record (the new address)
        """
        self.ensure_one()

        # If setting as default, unset other defaults
        if address_data.get('is_default'):
            self.child_ids.filtered(
                lambda p: p.type == 'delivery' and p.is_default_shipping
            ).write({'is_default_shipping': False})

        # Create the shipping address
        vals = {
            'parent_id': self.id,
            'type': 'delivery',
            'name': address_data.get('name', self.name),
            'phone': address_data.get('phone') or address_data.get('mobile'),
            'mobile': address_data.get('mobile') or address_data.get('phone'),
            'street': address_data.get('street', ''),
            'street2': address_data.get('street2', ''),
            'city': address_data.get('city', ''),
            'zip': address_data.get('zip', ''),
            'country_id': self.env.ref('base.th').id,  # Thailand
            'is_default_shipping': address_data.get('is_default', False),
        }

        # Handle state/province
        if address_data.get('state_id'):
            vals['state_id'] = address_data['state_id']
        elif address_data.get('province'):
            # Try to find province by name
            state = self.env['res.country.state'].search([
                ('country_id', '=', self.env.ref('base.th').id),
                '|',
                ('name', 'ilike', address_data['province']),
                ('code', '=', address_data['province']),
            ], limit=1)
            if state:
                vals['state_id'] = state.id

        ctx = dict(tracking_disable=True)
        return self.with_context(**ctx).create(vals)

    def update_shipping_address(self, address_id, address_data):
        """
        Update an existing shipping address.

        Args:
            address_id: int - ID of the address to update
            address_data: dict with fields to update

        Returns:
            res.partner record or False if not found
        """
        self.ensure_one()

        address = self.child_ids.filtered(
            lambda p: p.id == address_id and p.type == 'delivery'
        )

        if not address:
            return False

        # If setting as default, unset other defaults
        if address_data.get('is_default'):
            self.child_ids.filtered(
                lambda p: p.type == 'delivery' and p.is_default_shipping and p.id != address_id
            ).write({'is_default_shipping': False})
            address_data['is_default_shipping'] = True

        # Map fields
        update_vals = {}
        field_map = {
            'name': 'name',
            'phone': 'phone',
            'mobile': 'mobile',
            'street': 'street',
            'street2': 'street2',
            'city': 'city',
            'zip': 'zip',
            'is_default': 'is_default_shipping',
        }

        for key, field in field_map.items():
            if key in address_data:
                update_vals[field] = address_data[key]

        # Handle state/province
        if address_data.get('state_id'):
            update_vals['state_id'] = address_data['state_id']
        elif address_data.get('province'):
            state = self.env['res.country.state'].search([
                ('country_id', '=', self.env.ref('base.th').id),
                '|',
                ('name', 'ilike', address_data['province']),
                ('code', '=', address_data['province']),
            ], limit=1)
            if state:
                update_vals['state_id'] = state.id

        if update_vals:
            address.with_context(tracking_disable=True).write(update_vals)

        return address

    def delete_shipping_address(self, address_id):
        """
        Delete a shipping address.

        Args:
            address_id: int - ID of the address to delete

        Returns:
            bool - True if deleted, False otherwise
        """
        self.ensure_one()

        address = self.child_ids.filtered(
            lambda p: p.id == address_id and p.type == 'delivery'
        )

        if not address:
            return False

        # Archive instead of delete to preserve history
        address.write({'active': False})
        return True

    def set_default_shipping_address(self, address_id):
        """
        Set a shipping address as the default.

        Args:
            address_id: int - ID of the address to set as default

        Returns:
            bool - True if set, False otherwise
        """
        self.ensure_one()

        address = self.child_ids.filtered(
            lambda p: p.id == address_id and p.type == 'delivery' and p.active
        )

        if not address:
            return False

        # Unset all defaults
        self.child_ids.filtered(
            lambda p: p.type == 'delivery' and p.is_default_shipping
        ).write({'is_default_shipping': False})

        # Set new default
        address.write({'is_default_shipping': True})
        return True

    def get_shipping_address_dict(self):
        """
        Get shipping address as dict for API response.

        Returns:
            dict with address fields
        """
        self.ensure_one()

        return {
            'id': self.id,
            'name': self.name or '',
            'phone': self.phone or self.mobile or '',
            'street': self.street or '',
            'street2': self.street2 or '',
            'city': self.city or '',
            'province': self.state_id.name if self.state_id else '',
            'province_id': self.state_id.id if self.state_id else None,
            'zip': self.zip or '',
            'is_default': self.is_default_shipping,
            'full_address': self._format_full_address(),
        }

    def _format_full_address(self):
        """Format full address as single string"""
        parts = [
            self.street or '',
            self.street2 or '',
            self.city or '',
            self.state_id.name if self.state_id else '',
            self.zip or '',
        ]
        return ' '.join(p for p in parts if p)
