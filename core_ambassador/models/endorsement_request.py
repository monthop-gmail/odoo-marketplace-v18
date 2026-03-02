# -*- coding: utf-8 -*-
import logging
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class EndorsementRequest(models.Model):
    _name = 'endorsement.request'
    _description = 'Endorsement Request'
    _inherit = ['mail.thread']
    _order = 'create_date desc'

    name = fields.Char(
        string='Request Reference',
        default='NEW',
        readonly=True,
        copy=False,
    )

    seller_id = fields.Many2one(
        'res.partner',
        string='Seller (Requester)',
        required=True,
        domain=[('seller', '=', True), ('state', '=', 'approved')],
        index=True,
    )
    ambassador_id = fields.Many2one(
        'res.partner',
        string='Ambassador',
        required=True,
        domain=[('is_ambassador', '=', True), ('ambassador_state', '=', 'approved')],
        index=True,
    )
    product_id = fields.Many2one(
        'product.template',
        string='Product',
        required=True,
        index=True,
    )

    # Request details
    message = fields.Text(string='Message to Ambassador')
    response_message = fields.Text(string='Ambassador Response')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True, required=True, index=True)

    requested_date = fields.Datetime(string='Requested Date', readonly=True)
    responded_date = fields.Datetime(string='Responded Date', readonly=True)
    endorsement_id = fields.Many2one(
        'product.endorsement',
        string='Created Endorsement',
        readonly=True,
    )

    _sql_constraints = [
        ('seller_ambassador_product_uniq',
         'unique(seller_id, ambassador_id, product_id)',
         'A request for this product to this ambassador already exists.'),
    ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'NEW') == 'NEW':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'endorsement.request'
                ) or 'END-REQ/NEW'
        return super().create(vals_list)

    def action_submit(self):
        """draft → pending"""
        for rec in self:
            if rec.state != 'draft':
                raise ValidationError(_('Only draft requests can be submitted.'))
            # Validate product belongs to seller
            if rec.product_id.marketplace_seller_id != rec.seller_id:
                raise ValidationError(_('You can only request endorsement for your own products.'))
            rec.write({
                'state': 'pending',
                'requested_date': fields.Datetime.now(),
            })

    def action_approve(self):
        """pending → approved, creates product.endorsement"""
        for rec in self:
            if rec.state != 'pending':
                raise ValidationError(_('Only pending requests can be approved.'))
            # Create endorsement record
            endorsement = self.env['product.endorsement'].create({
                'ambassador_id': rec.ambassador_id.id,
                'product_id': rec.product_id.id,
                'request_id': rec.id,
                'endorsement_text': rec.response_message,
                'state': 'active',
            })
            rec.write({
                'state': 'approved',
                'responded_date': fields.Datetime.now(),
                'endorsement_id': endorsement.id,
            })

    def action_reject(self):
        """pending → rejected"""
        for rec in self:
            if rec.state != 'pending':
                raise ValidationError(_('Only pending requests can be rejected.'))
            rec.write({
                'state': 'rejected',
                'responded_date': fields.Datetime.now(),
            })

    def action_cancel(self):
        """draft/pending → cancelled"""
        for rec in self:
            if rec.state not in ('draft', 'pending'):
                raise ValidationError(_('Only draft or pending requests can be cancelled.'))
            rec.state = 'cancelled'
