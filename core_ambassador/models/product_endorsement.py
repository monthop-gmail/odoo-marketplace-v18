# -*- coding: utf-8 -*-
import logging
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class ProductEndorsement(models.Model):
    _name = 'product.endorsement'
    _description = 'Product Endorsement'
    _inherit = ['mail.thread']
    _order = 'create_date desc'
    _rec_name = 'display_name'

    ambassador_id = fields.Many2one(
        'res.partner',
        string='Ambassador',
        required=True,
        domain=[('is_ambassador', '=', True), ('ambassador_state', '=', 'approved')],
        ondelete='restrict',
        index=True,
    )
    product_id = fields.Many2one(
        'product.template',
        string='Product',
        required=True,
        ondelete='cascade',
        index=True,
    )
    seller_id = fields.Many2one(
        'res.partner',
        related='product_id.marketplace_seller_id',
        string='Seller',
        store=True,
        index=True,
    )
    request_id = fields.Many2one(
        'endorsement.request',
        string='Originating Request',
        readonly=True,
    )

    state = fields.Selection([
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('revoked', 'Revoked'),
    ], string='Status', default='active', tracking=True, required=True, index=True)

    # Endorsement content
    endorsement_text = fields.Text(string='Endorsement Review')
    endorsement_video_url = fields.Char(string='Review Video URL')
    rating = fields.Float(string='Ambassador Rating', default=0.0)

    # Dates
    endorsed_date = fields.Datetime(
        string='Endorsed Date',
        default=fields.Datetime.now,
    )
    expiry_date = fields.Date(string='Expiry Date')

    # Analytics placeholders (Sprint 2)
    click_count = fields.Integer(string='Click Count', default=0)
    order_count = fields.Integer(string='Orders from Endorsement', default=0)
    total_sales = fields.Monetary(
        string='Total Sales',
        currency_field='currency_id',
        default=0.0,
    )
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id.id,
    )

    display_name = fields.Char(compute='_compute_display_name', store=True)

    _sql_constraints = [
        ('ambassador_product_uniq', 'unique(ambassador_id, product_id)',
         'An ambassador can only endorse a product once.'),
    ]

    @api.depends('ambassador_id.name', 'product_id.name')
    def _compute_display_name(self):
        for rec in self:
            amb_name = rec.ambassador_id.name or ''
            prod_name = rec.product_id.name or ''
            rec.display_name = f"{amb_name} → {prod_name}"

    def action_revoke(self):
        """Revoke endorsement"""
        for rec in self:
            if rec.state != 'active':
                raise ValidationError(_('Only active endorsements can be revoked.'))
            rec.state = 'revoked'

    def action_reactivate(self):
        """Reactivate revoked endorsement"""
        for rec in self:
            if rec.state != 'revoked':
                raise ValidationError(_('Only revoked endorsements can be reactivated.'))
            rec.state = 'active'
