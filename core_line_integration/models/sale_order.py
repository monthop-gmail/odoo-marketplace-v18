# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    """
    Extend sale.order with LINE-related fields and notification triggers
    """
    _inherit = 'sale.order'

    # LINE Source Tracking
    source_channel = fields.Selection([
        ('website', 'Website'),
        ('line', 'LINE'),
        ('pos', 'POS'),
        ('manual', 'Manual'),
    ], string='Source Channel', default='website',
       help='Channel through which this order was placed')

    source_line_channel_id = fields.Many2one(
        'line.channel',
        string='Source LINE Channel',
        help='The LINE channel through which this order was placed',
    )

    # LINE Notification Status
    line_notify_sent = fields.Boolean(
        string='LINE Notification Sent',
        default=False,
    )
    line_shipping_notify_sent = fields.Boolean(
        string='Shipping Notification Sent',
        default=False,
    )

    # LINE Session (for API tracking)
    line_session_id = fields.Char(
        string='LINE Session ID',
        help='Session ID from LINE buyer app',
    )

    # ===========================================
    # Shipping / Fulfillment Fields
    # ===========================================
    shipping_status = fields.Selection([
        ('pending', 'รอดำเนินการ'),
        ('label_printed', 'พิมพ์ใบปะหน้าแล้ว'),
        ('packed', 'แพ็คสินค้าแล้ว'),
        ('shipped', 'จัดส่งแล้ว'),
        ('delivered', 'ส่งถึงแล้ว'),
    ], string='Shipping Status', default='pending', tracking=True)

    label_printed = fields.Boolean(
        string='Label Printed',
        default=False,
        tracking=True,
    )
    label_printed_date = fields.Datetime(
        string='Label Printed Date',
    )
    label_printed_by = fields.Many2one(
        'res.users',
        string='Printed By',
    )

    packed_date = fields.Datetime(
        string='Packed Date',
    )
    packed_by = fields.Many2one(
        'res.users',
        string='Packed By',
    )

    shipped_date = fields.Datetime(
        string='Shipped Date',
        tracking=True,
    )
    shipped_by = fields.Many2one(
        'res.users',
        string='Shipped By',
    )

    tracking_number = fields.Char(
        string='Tracking Number',
        tracking=True,
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
    ], string='Shipping Carrier', tracking=True)

    shipping_notes = fields.Text(
        string='Shipping Notes',
        help='Notes for the shipping team',
    )

    estimated_delivery = fields.Date(
        string='Estimated Delivery',
    )

    # Computed fields for dashboard
    shipping_address_text = fields.Text(
        string='Shipping Address',
        compute='_compute_shipping_address_text',
        store=True,
    )

    order_items_summary = fields.Char(
        string='Items Summary',
        compute='_compute_order_items_summary',
    )

    @api.depends('partner_shipping_id', 'partner_shipping_id.street',
                 'partner_shipping_id.street2', 'partner_shipping_id.city',
                 'partner_shipping_id.state_id', 'partner_shipping_id.zip',
                 'partner_shipping_id.phone', 'partner_shipping_id.mobile')
    def _compute_shipping_address_text(self):
        for order in self:
            addr = order.partner_shipping_id
            if addr:
                parts = [
                    addr.name,
                    addr.phone or addr.mobile or '',
                    addr.street or '',
                    addr.street2 or '',
                    addr.city or '',
                    addr.state_id.name if addr.state_id else '',
                    addr.zip or '',
                ]
                order.shipping_address_text = '\n'.join(p for p in parts if p)
            else:
                order.shipping_address_text = ''

    @api.depends('order_line', 'order_line.product_id', 'order_line.product_uom_qty')
    def _compute_order_items_summary(self):
        for order in self:
            items = []
            for line in order.order_line[:3]:  # First 3 items
                items.append(f"{line.product_id.name[:20]} x{int(line.product_uom_qty)}")
            total = len(order.order_line)
            if total > 3:
                items.append(f"...+{total - 3} รายการ")
            order.order_items_summary = ', '.join(items) if items else ''

    # ===========================================
    # Shipping Actions
    # ===========================================
    def action_print_label(self):
        """Mark label as printed and return print action"""
        self.ensure_one()
        if not self.partner_shipping_id:
            raise UserError(_('No shipping address specified.'))

        self.write({
            'label_printed': True,
            'label_printed_date': fields.Datetime.now(),
            'label_printed_by': self.env.user.id,
            'shipping_status': 'label_printed',
        })

        return self.env.ref('core_line_integration.action_report_shipping_label').report_action(self)

    def action_mark_packed(self):
        """Mark order as packed"""
        self.write({
            'packed_date': fields.Datetime.now(),
            'packed_by': self.env.user.id,
            'shipping_status': 'packed',
        })

    def action_mark_shipped(self):
        """Open wizard to mark as shipped with tracking"""
        self.ensure_one()
        return {
            'name': _('Mark as Shipped'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order.ship.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_order_id': self.id,
                'default_shipping_carrier': self.shipping_carrier,
            },
        }

    def action_mark_delivered(self):
        """Mark order as delivered"""
        self.write({
            'shipping_status': 'delivered',
        })

    def action_batch_print_labels(self):
        """Print labels for multiple orders"""
        if not self:
            raise UserError(_('No orders selected.'))

        for order in self:
            if not order.partner_shipping_id:
                continue
            order.write({
                'label_printed': True,
                'label_printed_date': fields.Datetime.now(),
                'label_printed_by': self.env.user.id,
                'shipping_status': 'label_printed' if order.shipping_status == 'pending' else order.shipping_status,
            })

        return self.env.ref('core_line_integration.action_report_shipping_label').report_action(self)

    def action_confirm(self):
        """Override to send LINE notification on order confirmation"""
        res = super().action_confirm()

        for order in self:
            if order.source_channel == 'line' and order.source_line_channel_id:
                order._send_line_order_notification()

        return res

    def _send_line_order_notification(self):
        """
        Send order confirmation notification via LINE.
        This is a placeholder - actual implementation requires server deployment.
        """
        self.ensure_one()

        if not self.partner_id.line_user_id:
            _logger.warning(f'Cannot send LINE notification: No LINE user ID for partner {self.partner_id.name}')
            return False

        if not self.partner_id.line_notify_orders:
            _logger.info(f'LINE notification disabled for partner {self.partner_id.name}')
            return False

        # Log the notification attempt (use sudo for API access)
        self.env['line.notify.log'].sudo().create({
            'channel_id': self.source_line_channel_id.id,
            'partner_id': self.partner_id.id,
            'line_user_id': self.partner_id.line_user_id,
            'notify_type': 'order_confirm',
            'message': f'Order {self.name} confirmed. Total: {self.amount_total}',
            'reference_model': 'sale.order',
            'reference_id': self.id,
            'state': 'pending',
        })

        self.line_notify_sent = True
        _logger.info(f'LINE notification queued for order {self.name}')

        return True

    def _send_line_shipping_notification(self, tracking_number=None, carrier=None):
        """
        Send shipping notification via LINE.
        Called when order is shipped (delivery state changes).
        """
        self.ensure_one()

        if not self.partner_id.line_user_id:
            return False

        if not self.partner_id.line_notify_orders:
            return False

        # Build shipping message
        carrier_names = dict(self._fields['shipping_carrier'].selection)
        carrier_display = carrier_names.get(carrier, carrier) if carrier else ''

        message = f'📦 คำสั่งซื้อ {self.name} จัดส่งแล้ว!'
        if carrier_display:
            message += f'\n🚚 ขนส่ง: {carrier_display}'
        if tracking_number:
            message += f'\n📋 Tracking: {tracking_number}'

        self.env['line.notify.log'].sudo().create({
            'channel_id': self.source_line_channel_id.id if self.source_line_channel_id else False,
            'partner_id': self.partner_id.id,
            'line_user_id': self.partner_id.line_user_id,
            'notify_type': 'shipping',
            'message': message,
            'reference_model': 'sale.order',
            'reference_id': self.id,
            'state': 'pending',
        })

        self.line_shipping_notify_sent = True
        return True

    def confirm_shipping(self, tracking_number=None, carrier=None, send_notification=True):
        """
        Confirm that order has been shipped.
        Called from wizard or API.

        Args:
            tracking_number: str - Tracking number from carrier
            carrier: str - Carrier selection key
            send_notification: bool - Whether to send LINE notification
        """
        self.ensure_one()

        vals = {
            'shipping_status': 'shipped',
            'shipped_date': fields.Datetime.now(),
            'shipped_by': self.env.user.id,
        }

        if tracking_number:
            vals['tracking_number'] = tracking_number
        if carrier:
            vals['shipping_carrier'] = carrier

        self.write(vals)

        if send_notification and self.source_channel == 'line':
            self._send_line_shipping_notification(tracking_number, carrier)

    def get_line_order_summary(self):
        """
        Get order summary formatted for LINE Flex Message.
        Returns dict suitable for building LINE Flex Message.
        """
        self.ensure_one()

        lines_data = []
        for line in self.order_line:
            lines_data.append({
                'product_name': line.product_id.name,
                'quantity': line.product_uom_qty,
                'unit_price': line.price_unit,
                'subtotal': line.price_subtotal,
            })

        return {
            'order_name': self.name,
            'date': self.date_order.strftime('%Y-%m-%d %H:%M') if self.date_order else '',
            'customer': self.partner_id.name,
            'lines': lines_data,
            'subtotal': self.amount_untaxed,
            'tax': self.amount_tax,
            'total': self.amount_total,
            'state': self.state,
            'state_display': dict(self._fields['state'].selection).get(self.state, ''),
        }
