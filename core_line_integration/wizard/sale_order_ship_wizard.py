# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class SaleOrderShipWizard(models.TransientModel):
    """Wizard to mark sale order as shipped with tracking info"""
    _name = 'sale.order.ship.wizard'
    _description = 'Mark Order as Shipped'

    order_id = fields.Many2one(
        'sale.order',
        string='Order',
        required=True,
    )

    shipping_carrier = fields.Selection([
        ('thai_post', 'ไปรษณีย์ไทย'),
        ('kerry', 'Kerry Express'),
        ('flash', 'Flash Express'),
        ('jt', 'J&T Express'),
        ('grab', 'Grab Express'),
        ('lalamove', 'Lalamove'),
        ('self', 'จัดส่งเอง'),
        ('pickup', 'รับเอง'),
    ], string='Shipping Carrier', required=True)

    tracking_number = fields.Char(
        string='Tracking Number',
        help='Tracking number from the carrier',
    )

    send_notification = fields.Boolean(
        string='Send LINE Notification',
        default=True,
        help='Send shipping notification to customer via LINE',
    )

    notes = fields.Text(
        string='Notes',
    )

    def action_confirm_shipping(self):
        """Confirm shipping and send notification"""
        self.ensure_one()

        # Update order
        self.order_id.confirm_shipping(
            tracking_number=self.tracking_number,
            carrier=self.shipping_carrier,
            send_notification=self.send_notification,
        )

        if self.notes:
            self.order_id.shipping_notes = self.notes

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Shipping Confirmed'),
                'message': _('Order %s has been marked as shipped.') % self.order_id.name,
                'type': 'success',
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'},
            }
        }


class SaleOrderBatchShipWizard(models.TransientModel):
    """Wizard to mark multiple orders as shipped"""
    _name = 'sale.order.batch.ship.wizard'
    _description = 'Batch Mark as Shipped'

    order_ids = fields.Many2many(
        'sale.order',
        string='Orders',
    )

    order_count = fields.Integer(
        string='Number of Orders',
        compute='_compute_order_count',
    )

    shipping_carrier = fields.Selection([
        ('thai_post', 'ไปรษณีย์ไทย'),
        ('kerry', 'Kerry Express'),
        ('flash', 'Flash Express'),
        ('jt', 'J&T Express'),
        ('grab', 'Grab Express'),
        ('lalamove', 'Lalamove'),
        ('self', 'จัดส่งเอง'),
        ('pickup', 'รับเอง'),
    ], string='Shipping Carrier', required=True)

    send_notification = fields.Boolean(
        string='Send LINE Notifications',
        default=True,
    )

    @api.depends('order_ids')
    def _compute_order_count(self):
        for wizard in self:
            wizard.order_count = len(wizard.order_ids)

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if 'order_ids' in fields_list:
            active_ids = self.env.context.get('active_ids', [])
            res['order_ids'] = [(6, 0, active_ids)]
        return res

    def action_confirm_batch_shipping(self):
        """Confirm shipping for all selected orders"""
        self.ensure_one()

        for order in self.order_ids:
            order.confirm_shipping(
                carrier=self.shipping_carrier,
                send_notification=self.send_notification,
            )

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Batch Shipping Confirmed'),
                'message': _('%d orders have been marked as shipped.') % len(self.order_ids),
                'type': 'success',
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'},
            }
        }
