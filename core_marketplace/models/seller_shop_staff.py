# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class SellerShopStaff(models.Model):
    _name = 'seller.shop.staff'
    _description = 'Shop Staff Member'
    _order = 'join_date desc'
    _rec_name = 'staff_partner_id'

    shop_id = fields.Many2one(
        'seller.shop',
        string='Shop',
        required=True,
        ondelete='cascade',
        index=True,
    )
    staff_partner_id = fields.Many2one(
        'res.partner',
        string='Staff Member',
        required=True,
        ondelete='cascade',
        index=True,
    )
    role = fields.Selection([
        ('staff', 'Staff'),
        ('manager', 'Shop Manager'),
    ], string='Role', default='staff', required=True)
    is_active = fields.Boolean(
        string='Active',
        default=True,
        index=True,
    )
    invited_by = fields.Many2one(
        'res.partner',
        string='Invited By',
    )
    join_date = fields.Datetime(
        string='Join Date',
        default=fields.Datetime.now,
    )

    # Related fields
    seller_id = fields.Many2one(
        related='shop_id.seller_id',
        string='Shop Owner',
        store=True,
        readonly=True,
    )
    shop_name = fields.Char(
        related='shop_id.name',
        string='Shop Name',
        readonly=True,
    )
    staff_name = fields.Char(
        related='staff_partner_id.name',
        string='Staff Name',
        readonly=True,
    )

    _sql_constraints = [
        ('staff_partner_uniq', 'unique(staff_partner_id)',
         'A person can only be staff of one shop at a time!'),
    ]

    @api.constrains('staff_partner_id', 'shop_id')
    def _check_not_shop_owner(self):
        """Shop owner (approved seller) cannot be staff of another shop."""
        for record in self:
            partner = record.staff_partner_id
            if partner.seller and partner.state == 'approved':
                raise ValidationError(
                    _('An approved seller (%s) cannot be added as staff to another shop.') % partner.name
                )
            if record.shop_id.seller_id == partner:
                raise ValidationError(
                    _('The shop owner (%s) cannot be added as staff to their own shop.') % partner.name
                )
