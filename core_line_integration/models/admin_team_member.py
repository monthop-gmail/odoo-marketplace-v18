# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class AdminTeamMember(models.Model):
    """
    Admin Team Member - tracks invitation and revocation of admin team members.
    Manager can invite LINE members as Officers via LIFF Admin App.
    """
    _name = 'admin.team.member'
    _description = 'Admin Team Member'
    _order = 'invite_date desc'
    _rec_name = 'partner_id'

    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        required=True,
        ondelete='cascade',
        index=True,
    )
    user_id = fields.Many2one(
        'res.users',
        string='User Account',
        ondelete='set null',
    )
    role = fields.Selection([
        ('officer', 'Officer'),
    ], string='Role', required=True, default='officer')

    state = fields.Selection([
        ('active', 'Active'),
        ('revoked', 'Revoked'),
    ], string='State', required=True, default='active', index=True)

    # Invitation info
    invited_by = fields.Many2one(
        'res.partner',
        string='Invited By',
        ondelete='set null',
    )
    invite_date = fields.Datetime(
        string='Invite Date',
        default=fields.Datetime.now,
    )
    invite_notes = fields.Text(
        string='Invite Notes',
    )

    # Revocation info
    revoked_by = fields.Many2one(
        'res.partner',
        string='Revoked By',
        ondelete='set null',
    )
    revoke_date = fields.Datetime(
        string='Revoke Date',
    )
    revoke_reason = fields.Text(
        string='Revoke Reason',
    )

    # LINE reference
    line_member_id = fields.Many2one(
        'line.channel.member',
        string='LINE Member',
        ondelete='set null',
    )

    @api.constrains('partner_id', 'state')
    def _check_unique_active_member(self):
        for record in self:
            if record.state == 'active':
                existing = self.search([
                    ('partner_id', '=', record.partner_id.id),
                    ('state', '=', 'active'),
                    ('id', '!=', record.id),
                ])
                if existing:
                    raise ValidationError(
                        _('Partner %s already has an active admin team membership.') % record.partner_id.name
                    )
