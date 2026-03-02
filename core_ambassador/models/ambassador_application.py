# -*- coding: utf-8 -*-
import logging
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class AmbassadorApplication(models.Model):
    _name = 'ambassador.application'
    _description = 'Ambassador Application'
    _inherit = ['mail.thread']
    _order = 'create_date desc'

    name = fields.Char(
        string='Application Reference',
        default='NEW',
        readonly=True,
        copy=False,
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Applicant',
        required=True,
        ondelete='cascade',
        index=True,
    )

    # Application data
    full_name = fields.Char(string='Full Name', required=True)
    phone = fields.Char(string='Phone')
    email = fields.Char(string='Email')
    specialty_ids = fields.Many2many(
        'ambassador.specialty',
        'application_specialty_rel',
        'application_id', 'specialty_id',
        string='Expertise Areas',
    )
    bio = fields.Text(string='Bio / Introduction')
    experience = fields.Text(string='Relevant Experience')
    motivation = fields.Text(string='Why do you want to be an ambassador?')

    # Social media
    social_youtube = fields.Char(string='YouTube Channel URL')
    social_facebook = fields.Char(string='Facebook Page URL')
    social_tiktok = fields.Char(string='TikTok Profile URL')
    social_instagram = fields.Char(string='Instagram URL')

    # Portfolio
    portfolio_url = fields.Char(string='Portfolio URL')

    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], string='Status', default='draft', tracking=True, required=True, index=True)

    submitted_date = fields.Datetime(string='Submitted Date', readonly=True)
    reviewed_date = fields.Datetime(string='Reviewed Date', readonly=True)
    reviewed_by = fields.Many2one('res.users', string='Reviewed By', readonly=True)
    rejection_reason = fields.Text(string='Rejection Reason')

    # Tier
    requested_tier = fields.Selection([
        ('bronze', 'Bronze'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
    ], string='Requested Tier', default='bronze')
    approved_tier = fields.Selection([
        ('bronze', 'Bronze'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
    ], string='Approved Tier')

    _sql_constraints = [
        ('partner_uniq', 'unique(partner_id)',
         'An applicant can only have one application.'),
    ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'NEW') == 'NEW':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'ambassador.application'
                ) or 'AMB-APP/NEW'
        return super().create(vals_list)

    def action_submit(self):
        """draft → submitted"""
        for rec in self:
            if rec.state != 'draft':
                raise ValidationError(_('Only draft applications can be submitted.'))
            rec.write({
                'state': 'submitted',
                'submitted_date': fields.Datetime.now(),
            })
            # Mark partner as draft ambassador
            rec.partner_id.write({
                'is_ambassador': True,
                'ambassador_state': 'draft',
            })

    def action_review(self):
        """submitted → under_review"""
        for rec in self:
            if rec.state != 'submitted':
                raise ValidationError(_('Only submitted applications can be put under review.'))
            rec.state = 'under_review'

    def action_approve(self):
        """submitted/under_review → approved, creates ambassador on partner"""
        for rec in self:
            if rec.state not in ('submitted', 'under_review'):
                raise ValidationError(_('Only submitted or under-review applications can be approved.'))
            tier = rec.approved_tier or rec.requested_tier or 'bronze'
            rec.write({
                'state': 'approved',
                'reviewed_date': fields.Datetime.now(),
                'reviewed_by': self.env.uid,
                'approved_tier': tier,
            })
            # Update partner with ambassador data
            rec.partner_id.write({
                'is_ambassador': True,
                'ambassador_state': 'pending',
                'ambassador_tier': tier,
                'ambassador_bio': rec.bio,
                'ambassador_specialty_ids': [(6, 0, rec.specialty_ids.ids)],
                'ambassador_social_youtube': rec.social_youtube,
                'ambassador_social_facebook': rec.social_facebook,
                'ambassador_social_tiktok': rec.social_tiktok,
                'ambassador_social_instagram': rec.social_instagram,
                'ambassador_application_id': rec.id,
            })
            # Trigger ambassador approval on partner
            rec.partner_id.action_ambassador_approve()

    def action_reject(self):
        """submitted/under_review → rejected"""
        for rec in self:
            if rec.state not in ('submitted', 'under_review'):
                raise ValidationError(_('Only submitted or under-review applications can be rejected.'))
            rec.write({
                'state': 'rejected',
                'reviewed_date': fields.Datetime.now(),
                'reviewed_by': self.env.uid,
            })
            rec.partner_id.write({
                'ambassador_state': 'rejected',
            })
