# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class LineChannelMember(models.Model):
    """
    LINE Channel Member - represents a LINE user following a channel
    Links LINE users to Odoo partners (buyers)
    """
    _name = 'line.channel.member'
    _description = 'LINE Channel Member'
    _order = 'create_date desc'
    _rec_name = 'display_name'

    # LINE User Info
    line_user_id = fields.Char(
        string='LINE User ID',
        required=True,
        index=True,
        help='LINE user ID (from webhook or LIFF)',
    )
    display_name = fields.Char(
        string='Display Name',
        help='LINE display name',
    )
    picture_url = fields.Char(
        string='Picture URL',
        help='LINE profile picture URL',
    )
    status_message = fields.Char(
        string='Status Message',
        help='LINE status message',
    )

    # Channel Link
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

    # Partner Link (Odoo Contact)
    partner_id = fields.Many2one(
        'res.partner',
        string='Contact',
        help='Linked Odoo contact (buyer)',
    )

    # Follow Status
    is_following = fields.Boolean(
        string='Is Following',
        default=True,
        index=True,
        help='False if user has blocked or unfollowed',
    )
    follow_date = fields.Datetime(
        string='Follow Date',
        default=fields.Datetime.now,
    )
    unfollow_date = fields.Datetime(
        string='Unfollow Date',
    )

    # Member Type
    member_type = fields.Selection([
        ('buyer', 'Buyer'),
        ('seller', 'Seller'),
        ('admin', 'Admin'),
    ], string='Member Type', default='buyer')

    # Registration Status
    registration_state = fields.Selection([
        ('new', 'New'),
        ('profile_pending', 'Profile Pending'),
        ('verified', 'Verified'),
    ], string='Registration State', default='new')

    # Last Activity
    last_message_date = fields.Datetime(
        string='Last Message',
    )
    last_activity_date = fields.Datetime(
        string='Last Activity',
    )

    # Statistics
    order_count = fields.Integer(
        string='Order Count',
        compute='_compute_order_stats',
    )
    total_spent = fields.Float(
        string='Total Spent',
        compute='_compute_order_stats',
    )

    # Notes
    notes = fields.Text(
        string='Notes',
    )

    _sql_constraints = [
        ('channel_user_uniq', 'unique(channel_id, line_user_id)',
         'A LINE user can only have one membership per channel!'),
    ]

    @api.depends('partner_id')
    def _compute_order_stats(self):
        for record in self:
            if record.partner_id:
                orders = self.env['sale.order'].search([
                    ('partner_id', '=', record.partner_id.id),
                    ('state', 'in', ['sale', 'done']),
                ])
                record.order_count = len(orders)
                record.total_spent = sum(orders.mapped('amount_total'))
            else:
                record.order_count = 0
                record.total_spent = 0.0

    @api.model
    def get_or_create_member(self, channel_id, line_user_id, profile_data=None):
        """
        Get existing member or create new one.
        Called when user follows or interacts with LINE OA.

        Args:
            channel_id: int - ID of line.channel
            line_user_id: str - LINE user ID
            profile_data: dict - optional profile data from LINE API
                {display_name, picture_url, status_message}

        Returns:
            line.channel.member record
        """
        # Use tracking_disable context for API calls without login session
        ctx = dict(
            tracking_disable=True,
            mail_create_nosubscribe=True,
            mail_auto_subscribe_no_notify=True,
        )
        Member = self.with_context(**ctx)

        member = Member.search([
            ('channel_id', '=', channel_id),
            ('line_user_id', '=', line_user_id),
        ], limit=1)

        if member:
            # Update profile if provided
            if profile_data:
                update_vals = {}
                if profile_data.get('display_name'):
                    update_vals['display_name'] = profile_data['display_name']
                if profile_data.get('picture_url'):
                    update_vals['picture_url'] = profile_data['picture_url']
                if profile_data.get('status_message'):
                    update_vals['status_message'] = profile_data['status_message']
                if update_vals:
                    member.with_context(**ctx).write(update_vals)

            # Reactivate if was unfollowed
            if not member.is_following:
                member.with_context(**ctx).write({
                    'is_following': True,
                    'follow_date': fields.Datetime.now(),
                    'unfollow_date': False,
                })
        else:
            # Create new member
            vals = {
                'channel_id': channel_id,
                'line_user_id': line_user_id,
                'is_following': True,
                'follow_date': fields.Datetime.now(),
            }
            if profile_data:
                vals.update({
                    'display_name': profile_data.get('display_name'),
                    'picture_url': profile_data.get('picture_url'),
                    'status_message': profile_data.get('status_message'),
                })
            member = Member.create(vals)

        return member

    def action_create_partner(self):
        """Create or link partner for this member"""
        self.ensure_one()
        if self.partner_id:
            raise ValidationError(_('This member already has a linked contact.'))

        # Check if partner exists with same LINE user ID
        existing_partner = self.env['res.partner'].search([
            ('line_user_id', '=', self.line_user_id),
        ], limit=1)

        if existing_partner:
            self.partner_id = existing_partner
        else:
            # Create new partner
            partner = self.env['res.partner'].create({
                'name': self.display_name or f'LINE User {self.line_user_id[:8]}',
                'line_user_id': self.line_user_id,
                'image_1920': False,  # Could fetch from picture_url
                'customer_rank': 1,
            })
            self.partner_id = partner

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'res.partner',
            'res_id': self.partner_id.id,
            'view_mode': 'form',
        }

    def action_unfollow(self):
        """Mark member as unfollowed (called from webhook)"""
        self.write({
            'is_following': False,
            'unfollow_date': fields.Datetime.now(),
        })

    def action_view_orders(self):
        """View orders from this member"""
        self.ensure_one()
        if not self.partner_id:
            raise ValidationError(_('No linked contact found.'))

        return {
            'name': _('Orders'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'list,form',
            'domain': [('partner_id', '=', self.partner_id.id)],
        }

    # ==================== Dynamic Role Methods ====================

    def sync_member_type_from_partner(self):
        """
        Sync member_type based on partner's current role.
        Called when seller status changes or on follow event.

        Logic:
        - Partner is admin (officer/manager group) → 'admin'
        - Partner is approved seller → 'seller'
        - Otherwise → 'buyer'
        """
        for member in self:
            if not member.partner_id:
                continue

            partner = member.partner_id
            new_type = 'buyer'  # default

            # Check admin first (admin takes priority)
            user = self.env['res.users'].sudo().search([
                ('partner_id', '=', partner.id),
            ], limit=1)
            if user:
                officer_group = self.env.ref(
                    'core_marketplace.marketplace_officer_group',
                    raise_if_not_found=False,
                )
                manager_group = self.env.ref(
                    'core_marketplace.marketplace_manager_group',
                    raise_if_not_found=False,
                )
                if (manager_group and manager_group in user.groups_id) or \
                   (officer_group and officer_group in user.groups_id):
                    new_type = 'admin'

            # Check seller (only if not admin)
            if new_type == 'buyer' and hasattr(partner, 'seller') and partner.seller:
                if partner.state == 'approved':
                    new_type = 'seller'

            # Check shop staff (only if still buyer — not admin, not seller)
            if new_type == 'buyer':
                staff = self.env['seller.shop.staff'].sudo().search([
                    ('staff_partner_id', '=', partner.id),
                    ('is_active', '=', True),
                ], limit=1)
                if staff and staff.seller_id and staff.seller_id.seller and staff.seller_id.state == 'approved':
                    new_type = 'seller'

            if member.member_type != new_type:
                old_type = member.member_type
                member.write({'member_type': new_type})
                _logger.info(
                    'Member %s type changed: %s → %s',
                    member.line_user_id, old_type, new_type,
                )

    def assign_role_rich_menu(self):
        """
        Assign role-specific rich menu to this member via LINE API.
        Finds the active rich menu matching member's role and channel,
        then calls LINE API to set it for the user.

        Silently skips if no role-specific rich menu is configured.
        """
        RichMenu = self.env['line.rich.menu'].sudo()

        # Check if menu_type field exists in the database
        if 'menu_type' not in RichMenu._fields:
            return

        for member in self:
            if not member.line_user_id or not member.channel_id:
                continue

            try:
                # Find rich menu for this role
                role_menu = RichMenu.search([
                    ('channel_id', '=', member.channel_id.id),
                    ('menu_type', '=', member.member_type),
                    ('state', 'in', ['uploaded', 'active']),
                    ('rich_menu_id', '!=', False),
                ], limit=1, order='sequence')
            except Exception:
                # menu_type column may not exist yet
                _logger.debug('Rich menu search failed, column may not exist')
                return

            if not role_menu:
                _logger.debug(
                    'No rich menu found for role %s on channel %s',
                    member.member_type, member.channel_id.code,
                )
                continue

            try:
                role_menu.action_link_to_user(member.line_user_id)
                _logger.info(
                    'Rich menu %s assigned to %s (role: %s)',
                    role_menu.name, member.line_user_id, member.member_type,
                )
            except Exception as e:
                _logger.error(
                    'Failed to assign rich menu to %s: %s',
                    member.line_user_id, e,
                )

    def send_role_change_notification(self, old_type, new_type, seller_state=None):
        """
        Send LINE push message when member role changes.

        Args:
            old_type: previous member_type
            new_type: new member_type
            seller_state: seller state that triggered the change (approved/denied)
        """
        self.ensure_one()
        if not self.line_user_id or not self.channel_id:
            return

        channel = self.channel_id
        mock_mode = self.env['ir.config_parameter'].sudo().get_param(
            'core_line_integration.mock_auth', 'True'
        ) == 'True'

        try:
            if mock_mode:
                from ..services.line_api import MockLineApiService
                service = MockLineApiService()
            else:
                from ..services.line_api import LineApiService
                service = LineApiService(
                    channel.channel_access_token,
                    channel.channel_secret,
                )

            from ..services.line_messaging import LineMessageBuilder

            # Build message based on state change
            if seller_state == 'approved':
                # Get seller LIFF URL
                seller_liff = self.env['line.liff'].sudo().search([
                    ('channel_id', '=', channel.id),
                    ('liff_type', '=', 'seller'),
                    ('active', '=', True),
                ], limit=1)
                liff_url = seller_liff.liff_url if seller_liff else ''

                text = (
                    '🎉 ยินดีด้วย! คุณได้รับการอนุมัติเป็นผู้ขายแล้ว\n\n'
                    'คุณสามารถเริ่มเพิ่มสินค้าและจัดการร้านค้าได้ทันที'
                )
                if liff_url:
                    text += f'\n\n👉 เปิดร้านค้า: {liff_url}'

                message = LineMessageBuilder.text(text)

            elif seller_state == 'denied':
                text = (
                    '📋 แจ้งผลการสมัครผู้ขาย\n\n'
                    'คำขอสมัครเป็นผู้ขายของคุณยังไม่ได้รับการอนุมัติในขณะนี้ '
                    'กรุณาตรวจสอบข้อมูลและลองสมัครใหม่อีกครั้ง'
                )
                message = LineMessageBuilder.text(text)

            elif seller_state == 'pending':
                text = (
                    '📝 ได้รับคำขอสมัครผู้ขายของคุณแล้ว\n\n'
                    'ทีมงานกำลังตรวจสอบข้อมูล กรุณารอการอนุมัติ'
                )
                message = LineMessageBuilder.text(text)

            elif seller_state == 'admin_promoted':
                admin_liff = self.env['line.liff'].sudo().search([
                    ('channel_id', '=', channel.id),
                    ('liff_type', '=', 'admin'),
                    ('active', '=', True),
                ], limit=1)
                liff_url = admin_liff.liff_url if admin_liff else ''

                text = (
                    '🛡️ ยินดีต้อนรับสู่ทีมแอดมิน!\n\n'
                    'คุณได้รับเชิญเป็น Officer ของแพลตฟอร์ม '
                    'สามารถเข้าใช้งาน Admin Panel ได้ทันที'
                )
                if liff_url:
                    text += f'\n\n👉 เปิด Admin Panel: {liff_url}'

                message = LineMessageBuilder.text(text)

            elif seller_state == 'admin_revoked':
                text = (
                    '📋 สิทธิ์แอดมินถูกเพิกถอนแล้ว\n\n'
                    'สิทธิ์ Officer ของคุณถูกเพิกถอนจากทีมแอดมิน '
                    'หากมีข้อสงสัยกรุณาติดต่อผู้ดูแลระบบ'
                )
                message = LineMessageBuilder.text(text)

            else:
                return

            service.push_message(self.line_user_id, [message])

            # Log the notification
            ctx = dict(
                tracking_disable=True,
                mail_create_nosubscribe=True,
                mail_auto_subscribe_no_notify=True,
            )
            notify_type = 'admin_team' if seller_state in ('admin_promoted', 'admin_revoked') else 'seller_status'
            self.env['line.notify.log'].sudo().with_context(**ctx).create({
                'channel_id': channel.id,
                'line_user_id': self.line_user_id,
                'partner_id': self.partner_id.id if self.partner_id else False,
                'notify_type': notify_type,
                'message': f'Role change: {seller_state}',
                'state': 'sent',
                'sent_date': fields.Datetime.now(),
            })

            _logger.info(
                'Role change notification sent to %s: %s',
                self.line_user_id, seller_state,
            )
        except Exception as e:
            _logger.error(
                'Failed to send role change notification to %s: %s',
                self.line_user_id, e,
            )

    @api.model
    def cleanup_inactive_members(self, days_threshold=180):
        """
        Cleanup inactive members who have unfollowed and have no orders.
        Called by scheduled action.

        Args:
            days_threshold: Number of days after unfollow to consider for cleanup
        """
        from datetime import timedelta
        import logging

        _logger = logging.getLogger(__name__)

        threshold_date = fields.Datetime.now() - timedelta(days=days_threshold)

        # Find members who:
        # 1. Have unfollowed
        # 2. Unfollowed more than threshold days ago
        # 3. Have no linked partner OR partner has no orders
        inactive_members = self.search([
            ('is_following', '=', False),
            ('unfollow_date', '<', threshold_date),
        ])

        to_delete = self.env['line.channel.member']

        for member in inactive_members:
            if not member.partner_id:
                to_delete |= member
            elif member.order_count == 0:
                to_delete |= member

        count = len(to_delete)
        if to_delete:
            _logger.info(f'Cleaning up {count} inactive LINE members')
            to_delete.unlink()

        return {'deleted': count}
