# -*- coding: utf-8 -*-
"""
LINE Group Model - tracks LINE groups/rooms the bot has joined
"""
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class LineGroup(models.Model):
    _name = 'line.group'
    _description = 'LINE Group Chat'
    _order = 'joined_date desc'
    _rec_name = 'display_name'

    # LINE Group Info
    line_group_id = fields.Char(
        string='LINE Group/Room ID',
        required=True,
        index=True,
    )
    group_type = fields.Selection([
        ('group', 'Group'),
        ('room', 'Room'),
    ], string='Type', default='group', required=True)

    display_name = fields.Char(
        string='Group Name',
        compute='_compute_display_name',
        store=True,
    )
    name = fields.Char(string='Name')
    picture_url = fields.Char(string='Picture URL')

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
        string='Channel Code',
        store=True,
    )

    # Status
    is_active = fields.Boolean(string='Bot Active in Group', default=True, index=True)
    member_count = fields.Integer(string='Member Count', default=0)

    # Dates
    joined_date = fields.Datetime(string='Bot Joined Date')
    left_date = fields.Datetime(string='Bot Left Date')

    # Group Members (LINE users in this group that we know about)
    group_member_ids = fields.One2many(
        'line.group.member',
        'group_id',
        string='Known Members',
    )
    known_member_count = fields.Integer(
        string='Known Members',
        compute='_compute_known_member_count',
    )

    # Notes
    notes = fields.Text(string='Notes')

    _sql_constraints = [
        ('unique_group_channel', 'unique(channel_id, line_group_id)',
         'This group is already registered for this channel.'),
    ]

    @api.depends('name', 'line_group_id', 'group_type')
    def _compute_display_name(self):
        for rec in self:
            if rec.name:
                rec.display_name = rec.name
            else:
                prefix = 'Group' if rec.group_type == 'group' else 'Room'
                short_id = rec.line_group_id[:12] if rec.line_group_id else '?'
                rec.display_name = f'{prefix} {short_id}...'

    def _compute_known_member_count(self):
        for rec in self:
            rec.known_member_count = len(rec.group_member_ids)

    def get_or_create_group(self, channel_id, line_group_id, group_type='group', vals=None):
        """
        Get existing group or create a new one.

        Args:
            channel_id: line.channel ID
            line_group_id: LINE group/room ID string
            group_type: 'group' or 'room'
            vals: Optional dict of extra values to write

        Returns:
            line.group record
        """
        group = self.search([
            ('channel_id', '=', channel_id),
            ('line_group_id', '=', line_group_id),
        ], limit=1)

        if group:
            # Reactivate if bot rejoined
            write_vals = {'is_active': True}
            if vals:
                write_vals.update(vals)
            group.write(write_vals)
            return group

        create_vals = {
            'channel_id': channel_id,
            'line_group_id': line_group_id,
            'group_type': group_type,
            'is_active': True,
            'joined_date': fields.Datetime.now(),
        }
        if vals:
            create_vals.update(vals)

        return self.create(create_vals)

    def action_leave_group(self):
        """Leave this LINE group via API"""
        self.ensure_one()
        from ..services.line_api import get_line_api_service
        try:
            service = get_line_api_service(self.channel_id)
            service.leave_group(self.line_group_id, self.group_type)
            self.write({
                'is_active': False,
                'left_date': fields.Datetime.now(),
            })
            _logger.info(f'Bot left {self.group_type} {self.line_group_id}')
        except Exception as e:
            _logger.error(f'Failed to leave group {self.line_group_id}: {e}')
            raise

    def action_fetch_group_info(self):
        """Fetch group summary from LINE API and update record"""
        self.ensure_one()
        if self.group_type != 'group':
            return  # Room API doesn't have summary endpoint
        from ..services.line_api import get_line_api_service
        try:
            service = get_line_api_service(self.channel_id)
            summary = service.get_group_summary(self.line_group_id)
            count = service.get_group_member_count(self.line_group_id)
            self.write({
                'name': summary.get('groupName', ''),
                'picture_url': summary.get('pictureUrl', ''),
                'member_count': count.get('count', 0) if isinstance(count, dict) else count,
            })
        except Exception as e:
            _logger.error(f'Failed to fetch group info {self.line_group_id}: {e}')

    def action_send_message(self):
        """Open wizard to send message to this group (placeholder)"""
        self.ensure_one()
        # Can be extended with a wizard
        return True


class LineGroupMember(models.Model):
    _name = 'line.group.member'
    _description = 'LINE Group Member'
    _order = 'joined_date desc'
    _rec_name = 'display_name'

    group_id = fields.Many2one(
        'line.group',
        string='Group',
        required=True,
        ondelete='cascade',
        index=True,
    )
    line_user_id = fields.Char(
        string='LINE User ID',
        required=True,
        index=True,
    )
    display_name = fields.Char(string='Display Name')
    picture_url = fields.Char(string='Picture URL')

    # Link to channel member (if exists)
    channel_member_id = fields.Many2one(
        'line.channel.member',
        string='Channel Member',
        ondelete='set null',
    )
    # Link to partner (if exists)
    partner_id = fields.Many2one(
        'res.partner',
        string='Contact',
        ondelete='set null',
    )

    # Status
    is_in_group = fields.Boolean(string='In Group', default=True, index=True)
    joined_date = fields.Datetime(string='Joined Date')
    left_date = fields.Datetime(string='Left Date')

    _sql_constraints = [
        ('unique_member_group', 'unique(group_id, line_user_id)',
         'This member is already registered in this group.'),
    ]
