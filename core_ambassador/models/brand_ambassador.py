# -*- coding: utf-8 -*-
import logging
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # ==================== Ambassador Fields ====================
    is_ambassador = fields.Boolean(
        string='Is Ambassador',
        default=False,
        copy=False,
        tracking=True,
    )
    ambassador_state = fields.Selection([
        ('none', 'None'),
        ('draft', 'Draft'),
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('suspended', 'Suspended'),
    ], string='Ambassador Status', default='none', copy=False, tracking=True)

    ambassador_tier = fields.Selection([
        ('bronze', 'Bronze'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
    ], string='Ambassador Tier', default='bronze', tracking=True)

    ambassador_commission_rate = fields.Float(
        string='Ambassador Commission Rate (%)',
        default=5.0,
        help='Commission percentage on endorsed product sales',
    )
    ambassador_bio = fields.Text(string='Ambassador Bio', translate=True)
    ambassador_specialty_ids = fields.Many2many(
        'ambassador.specialty',
        'partner_ambassador_specialty_rel',
        'partner_id', 'specialty_id',
        string='Specialties',
    )

    # Social media
    ambassador_social_youtube = fields.Char(string='YouTube Channel')
    ambassador_social_facebook = fields.Char(string='Facebook Page')
    ambassador_social_tiktok = fields.Char(string='TikTok Profile')
    ambassador_social_instagram = fields.Char(string='Instagram')

    # Relations
    ambassador_application_id = fields.Many2one(
        'ambassador.application',
        string='Ambassador Application',
        readonly=True,
        copy=False,
    )
    ambassador_approved_date = fields.Datetime(
        string='Ambassador Approved Date',
        readonly=True,
        copy=False,
    )

    # Computed
    endorsement_count = fields.Integer(
        string='Endorsement Count',
        compute='_compute_endorsement_count',
    )
    endorsement_ids = fields.One2many(
        'product.endorsement', 'ambassador_id',
        string='Endorsements',
    )

    # ==================== Computed ====================

    def _compute_endorsement_count(self):
        Endorsement = self.env['product.endorsement']
        for rec in self:
            if rec.is_ambassador:
                rec.endorsement_count = Endorsement.search_count([
                    ('ambassador_id', '=', rec.id),
                    ('state', '=', 'active'),
                ])
            else:
                rec.endorsement_count = 0

    # ==================== Status Transitions ====================

    def action_ambassador_approve(self):
        """Approve ambassador: pending → approved"""
        tier_rates = {'bronze': 5.0, 'silver': 7.0, 'gold': 10.0}
        for rec in self:
            if rec.ambassador_state != 'pending':
                raise ValidationError(_('Only pending ambassadors can be approved.'))
            rec.write({
                'ambassador_state': 'approved',
                'ambassador_approved_date': fields.Datetime.now(),
                'ambassador_commission_rate': tier_rates.get(rec.ambassador_tier, 5.0),
            })
            rec._sync_ambassador_line_role()

    def action_ambassador_reject(self):
        """Reject ambassador: pending → rejected"""
        for rec in self:
            if rec.ambassador_state != 'pending':
                raise ValidationError(_('Only pending ambassadors can be rejected.'))
            rec.ambassador_state = 'rejected'

    def action_ambassador_suspend(self):
        """Suspend ambassador: approved → suspended"""
        for rec in self:
            if rec.ambassador_state != 'approved':
                raise ValidationError(_('Only approved ambassadors can be suspended.'))
            rec.ambassador_state = 'suspended'

    def action_ambassador_reactivate(self):
        """Reactivate ambassador: suspended/rejected → approved"""
        for rec in self:
            if rec.ambassador_state not in ('suspended', 'rejected'):
                raise ValidationError(_('Only suspended or rejected ambassadors can be reactivated.'))
            rec.write({
                'ambassador_state': 'approved',
                'ambassador_approved_date': fields.Datetime.now(),
            })
            rec._sync_ambassador_line_role()

    def _sync_ambassador_line_role(self):
        """Sync LINE member type when ambassador status changes."""
        Member = self.env['line.channel.member'].sudo()
        for partner in self:
            members = Member.search([
                ('partner_id', '=', partner.id),
                ('is_following', '=', True),
            ])
            for member in members:
                member.sync_member_type_from_partner()
                if hasattr(member, 'assign_role_rich_menu'):
                    member.assign_role_rich_menu()
