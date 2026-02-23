# -*- coding: utf-8 -*-
"""
LINE Marketplace Wishlist Model
"""
from odoo import models, fields, api


class LineWishlist(models.Model):
    _name = 'line.wishlist'
    _description = 'LINE Marketplace Wishlist'
    _order = 'create_date desc'

    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        required=True,
        ondelete='cascade',
        index=True,
    )
    product_id = fields.Many2one(
        'product.template',
        string='Product',
        required=True,
        ondelete='cascade',
        index=True,
    )
    channel_id = fields.Many2one(
        'line.channel',
        string='LINE Channel',
        ondelete='set null',
    )

    # Product info snapshot (for display even if product changes)
    product_name = fields.Char(
        string='Product Name',
        related='product_id.name',
    )
    product_price = fields.Float(
        string='Price at Addition',
        digits='Product Price',
    )
    current_price = fields.Float(
        string='Current Price',
        related='product_id.list_price',
    )
    price_dropped = fields.Boolean(
        string='Price Dropped',
        compute='_compute_price_dropped',
        store=True,
    )

    notes = fields.Text(string='Notes')

    _sql_constraints = [
        ('unique_partner_product',
         'UNIQUE(partner_id, product_id)',
         'Product already in wishlist!'),
    ]

    @api.depends('product_price', 'current_price')
    def _compute_price_dropped(self):
        for record in self:
            if record.product_price and record.current_price:
                record.price_dropped = record.current_price < record.product_price
            else:
                record.price_dropped = False

    @api.model_create_multi
    def create(self, vals_list):
        """Store product price at time of addition"""
        for vals in vals_list:
            if 'product_id' in vals and 'product_price' not in vals:
                product = self.env['product.template'].browse(vals['product_id'])
                vals['product_price'] = product.list_price
        return super().create(vals_list)

    def action_add_to_cart(self):
        """Add wishlist item to cart"""
        self.ensure_one()
        # This would be called from the UI, actual cart logic is in API
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Add to Cart',
                'message': f'{self.product_name} - Use LINE app to add to cart',
                'type': 'info',
            }
        }
