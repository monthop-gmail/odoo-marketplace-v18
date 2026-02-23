# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import logging
import json

_logger = logging.getLogger(__name__)


class LineNotifyLog(models.Model):
    """
    LINE Notification Log - tracks all LINE push/reply messages sent
    """
    _name = 'line.notify.log'
    _description = 'LINE Notification Log'
    _order = 'create_date desc'

    # Target Info
    channel_id = fields.Many2one(
        'line.channel',
        string='LINE Channel',
        ondelete='set null',
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        ondelete='set null',
    )
    line_user_id = fields.Char(
        string='LINE User ID',
        required=True,
        index=True,
    )

    # Message Info
    notify_type = fields.Selection([
        ('welcome', 'Welcome Message'),
        ('order_confirm', 'Order Confirmation'),
        ('shipping', 'Shipping Update'),
        ('delivery', 'Delivery Confirmation'),
        ('payment_reminder', 'Payment Reminder'),
        ('promotion', 'Promotion'),
        ('seller_status', 'Seller Status Change'),
        ('broadcast', 'Broadcast'),
        ('custom', 'Custom Message'),
        ('admin_team', 'Admin Team Change'),
    ], string='Notification Type', required=True)

    message = fields.Text(
        string='Message',
        required=True,
    )
    message_type = fields.Selection([
        ('text', 'Text'),
        ('flex', 'Flex Message'),
        ('template', 'Template'),
        ('image', 'Image'),
        ('video', 'Video'),
    ], string='Message Type', default='text')

    flex_json = fields.Text(
        string='Flex Message JSON',
        help='JSON content for Flex Message',
    )

    # Reference (linked document)
    reference_model = fields.Char(
        string='Reference Model',
    )
    reference_id = fields.Integer(
        string='Reference ID',
    )
    reference_name = fields.Char(
        string='Reference Name',
        compute='_compute_reference_name',
    )

    # Status
    state = fields.Selection([
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
    ], string='State', default='pending', index=True)

    sent_date = fields.Datetime(
        string='Sent Date',
    )
    error_message = fields.Text(
        string='Error Message',
    )

    # LINE API Response
    line_message_id = fields.Char(
        string='LINE Message ID',
        help='Message ID from LINE API response',
    )
    api_response = fields.Text(
        string='API Response',
        help='Full response from LINE API',
    )

    # Retry Info
    retry_count = fields.Integer(
        string='Retry Count',
        default=0,
    )
    max_retries = fields.Integer(
        string='Max Retries',
        default=3,
    )
    next_retry = fields.Datetime(
        string='Next Retry',
    )

    @api.depends('reference_model', 'reference_id')
    def _compute_reference_name(self):
        for record in self:
            if record.reference_model and record.reference_id:
                try:
                    ref_record = self.env[record.reference_model].browse(record.reference_id)
                    if ref_record.exists():
                        record.reference_name = ref_record.display_name
                    else:
                        record.reference_name = f'{record.reference_model},{record.reference_id}'
                except Exception:
                    record.reference_name = f'{record.reference_model},{record.reference_id}'
            else:
                record.reference_name = False

    def action_send(self):
        """
        Send the notification via LINE API.
        Uses LINE Messaging API push message.
        """
        from odoo import fields as odoo_fields

        for record in self:
            if record.state == 'sent':
                continue

            _logger.info(f'Sending LINE notification {record.id}')

            try:
                # Check if mock mode
                mock_mode = self.env['ir.config_parameter'].sudo().get_param(
                    'core_line_integration.mock_auth', 'True'
                ) == 'True'

                # Get LINE service
                if mock_mode:
                    from ..services.line_api import MockLineApiService
                    line_service = MockLineApiService()
                else:
                    from ..services.line_api import LineApiService
                    if not record.channel_id or not record.channel_id.channel_access_token:
                        raise ValueError('Channel access token not configured')

                    line_service = LineApiService(
                        record.channel_id.channel_access_token,
                        record.channel_id.channel_secret
                    )

                # Build message
                if record.message_type == 'flex' and record.flex_json:
                    # Send Flex Message
                    message = {
                        'type': 'flex',
                        'altText': record.message[:400] if record.message else 'Notification',
                        'contents': json.loads(record.flex_json),
                    }
                else:
                    # Send text message
                    message = {
                        'type': 'text',
                        'text': record.message,
                    }

                # Send via LINE API
                result = line_service.push_message(record.line_user_id, [message])

                # Update record
                record.write({
                    'state': 'sent',
                    'sent_date': odoo_fields.Datetime.now(),
                    'api_response': json.dumps(result) if result else None,
                    'error_message': False,
                })

                _logger.info(f'LINE notification {record.id} sent successfully')

            except Exception as e:
                _logger.error(f'Failed to send LINE notification {record.id}: {str(e)}')
                record.write({
                    'state': 'failed',
                    'error_message': str(e),
                    'retry_count': record.retry_count + 1,
                })

        return True

    def action_retry(self):
        """Retry failed notifications"""
        failed = self.filtered(lambda r: r.state == 'failed' and r.retry_count < r.max_retries)
        for record in failed:
            record.retry_count += 1
            record.state = 'pending'
            record.action_send()

    def action_view_reference(self):
        """Open the referenced document"""
        self.ensure_one()
        if not self.reference_model or not self.reference_id:
            return

        return {
            'type': 'ir.actions.act_window',
            'res_model': self.reference_model,
            'res_id': self.reference_id,
            'view_mode': 'form',
        }

    @api.model
    def process_pending_notifications(self, limit=100):
        """
        Cron job to process pending notifications.
        Called by scheduled action.

        Args:
            limit: Maximum number of notifications to process per run
        """
        from odoo import fields as odoo_fields
        from datetime import timedelta

        _logger.info('Starting LINE notification cron job')

        # Process pending notifications
        pending = self.search([
            ('state', '=', 'pending'),
        ], limit=limit, order='create_date asc')

        sent_count = 0
        failed_count = 0

        for notification in pending:
            try:
                notification.action_send()
                if notification.state == 'sent':
                    sent_count += 1
                else:
                    failed_count += 1
            except Exception as e:
                _logger.error(f'Failed to process notification {notification.id}: {str(e)}')
                notification.write({
                    'state': 'failed',
                    'error_message': str(e),
                })
                failed_count += 1

        # Also retry failed notifications that are due
        retry_threshold = odoo_fields.Datetime.now() - timedelta(minutes=5)
        failed_retryable = self.search([
            ('state', '=', 'failed'),
            ('retry_count', '<', 3),
            ('write_date', '<', retry_threshold),
        ], limit=20)

        for notification in failed_retryable:
            try:
                notification.write({
                    'state': 'pending',
                    'retry_count': notification.retry_count + 1,
                })
                notification.action_send()
                if notification.state == 'sent':
                    sent_count += 1
            except Exception as e:
                _logger.error(f'Retry failed for notification {notification.id}: {str(e)}')

        _logger.info(f'LINE notification cron completed: {sent_count} sent, {failed_count} failed')

        return {
            'sent': sent_count,
            'failed': failed_count,
            'pending_remaining': self.search_count([('state', '=', 'pending')]),
        }

    @api.model
    def create_flex_order_message(self, order):
        """
        Create a Flex Message for order confirmation.
        Returns JSON string for LINE Flex Message.

        Args:
            order: sale.order record

        Returns:
            str: JSON string for Flex Message
        """
        # Build Flex Message container
        flex_content = {
            "type": "bubble",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "Order Confirmation",
                        "weight": "bold",
                        "size": "xl"
                    }
                ]
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": f"Order: {order.name}",
                        "weight": "bold"
                    },
                    {
                        "type": "separator",
                        "margin": "md"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "margin": "md",
                        "contents": []
                    },
                    {
                        "type": "separator",
                        "margin": "md"
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "margin": "md",
                        "contents": [
                            {"type": "text", "text": "Total", "weight": "bold"},
                            {"type": "text", "text": f"฿{order.amount_total:,.2f}", "align": "end", "weight": "bold"}
                        ]
                    }
                ]
            }
        }

        # Add order lines
        lines_container = flex_content["body"]["contents"][2]
        for line in order.order_line[:5]:  # Limit to 5 items
            lines_container["contents"].append({
                "type": "box",
                "layout": "horizontal",
                "contents": [
                    {"type": "text", "text": line.product_id.name[:20], "flex": 3, "size": "sm"},
                    {"type": "text", "text": f"x{int(line.product_uom_qty)}", "flex": 1, "align": "center", "size": "sm"},
                    {"type": "text", "text": f"฿{line.price_subtotal:,.0f}", "flex": 2, "align": "end", "size": "sm"}
                ]
            })

        if len(order.order_line) > 5:
            lines_container["contents"].append({
                "type": "text",
                "text": f"... and {len(order.order_line) - 5} more items",
                "size": "xs",
                "color": "#888888"
            })

        return json.dumps(flex_content)
