# -*- coding: utf-8 -*-
"""
LINE Marketplace Compare Model - For product comparison feature
"""
from odoo import models, fields, api


class LineCompareList(models.Model):
    _name = 'line.compare.list'
    _description = 'LINE Marketplace Compare List'
    _order = 'create_date desc'

    name = fields.Char(
        string='Name',
        compute='_compute_name',
        store=True,
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        required=True,
        ondelete='cascade',
        index=True,
    )
    channel_id = fields.Many2one(
        'line.channel',
        string='LINE Channel',
        ondelete='set null',
    )
    item_ids = fields.One2many(
        'line.compare.item',
        'compare_list_id',
        string='Items',
    )
    item_count = fields.Integer(
        string='Item Count',
        compute='_compute_item_count',
        store=True,
    )

    # Maximum items per compare list
    MAX_ITEMS = 4

    @api.depends('partner_id', 'create_date')
    def _compute_name(self):
        for record in self:
            if record.partner_id:
                record.name = f"Compare - {record.partner_id.name}"
            else:
                record.name = "Compare List"

    @api.depends('item_ids')
    def _compute_item_count(self):
        for record in self:
            record.item_count = len(record.item_ids)

    def add_product(self, product_id):
        """Add product to compare list"""
        self.ensure_one()

        if self.item_count >= self.MAX_ITEMS:
            return {'error': f'Maximum {self.MAX_ITEMS} items allowed'}

        # Check if already in list
        existing = self.item_ids.filtered(lambda i: i.product_id.id == product_id)
        if existing:
            return {'error': 'Product already in compare list'}

        self.env['line.compare.item'].create({
            'compare_list_id': self.id,
            'product_id': product_id,
        })
        return {'success': True}

    def remove_product(self, product_id):
        """Remove product from compare list"""
        self.ensure_one()
        item = self.item_ids.filtered(lambda i: i.product_id.id == product_id)
        if item:
            item.unlink()
            return {'success': True}
        return {'error': 'Product not in compare list'}

    def clear(self):
        """Clear all items from compare list"""
        self.ensure_one()
        self.item_ids.unlink()
        return {'success': True}


class LineCompareItem(models.Model):
    _name = 'line.compare.item'
    _description = 'LINE Marketplace Compare Item'
    _order = 'sequence, id'

    compare_list_id = fields.Many2one(
        'line.compare.list',
        string='Compare List',
        required=True,
        ondelete='cascade',
    )
    product_id = fields.Many2one(
        'product.template',
        string='Product',
        required=True,
        ondelete='cascade',
    )
    sequence = fields.Integer(string='Sequence', default=10)

    # Related fields for easy access
    product_name = fields.Char(
        related='product_id.name',
        string='Product Name',
    )
    product_price = fields.Float(
        related='product_id.list_price',
        string='Price',
    )
    product_image = fields.Binary(
        related='product_id.image_256',
        string='Image',
    )
    category_id = fields.Many2one(
        related='product_id.categ_id',
        string='Category',
    )

    _sql_constraints = [
        ('unique_list_product',
         'UNIQUE(compare_list_id, product_id)',
         'Product already in this compare list!'),
    ]
