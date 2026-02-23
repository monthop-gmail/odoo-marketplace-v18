# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class LineMessageWizard(models.TransientModel):
    """Wizard to send a LINE message to a partner"""
    _name = 'line.message.wizard'
    _description = 'Send LINE Message Wizard'

    partner_id = fields.Many2one(
        'res.partner',
        string='Recipient',
        required=True,
        readonly=True,
    )
    channel_id = fields.Many2one(
        'line.channel',
        string='LINE Channel',
        compute='_compute_channel_id',
        store=True,
        readonly=True,
    )
    line_user_id = fields.Char(
        string='LINE User ID',
        related='partner_id.line_user_id',
        readonly=True,
    )
    message_text = fields.Text(
        string='Message',
        required=True,
        help='Text message to send via LINE',
    )

    @api.depends('partner_id')
    def _compute_channel_id(self):
        for rec in self:
            rec.channel_id = rec.partner_id.primary_line_channel_id

    def action_send_message(self):
        """Send push message via LINE API and log it"""
        self.ensure_one()

        if not self.partner_id.line_user_id:
            raise UserError(_('This partner does not have a LINE User ID.'))

        if not self.channel_id:
            raise UserError(_('No LINE channel configured for this partner.'))

        if not self.channel_id.channel_access_token:
            raise UserError(_('LINE channel access token is not configured.'))

        from ..services.line_api import get_line_api_service, LineApiError

        service = get_line_api_service(self.channel_id)

        messages = [{'type': 'text', 'text': self.message_text}]

        try:
            service.push_message(self.partner_id.line_user_id, messages)
        except LineApiError as e:
            raise UserError(_('Failed to send LINE message: %s') % str(e))

        # Log the notification
        self.env['line.notify.log'].sudo().create({
            'channel_id': self.channel_id.id,
            'partner_id': self.partner_id.id,
            'line_user_id': self.partner_id.line_user_id,
            'notify_type': 'custom',
            'message_type': 'text',
            'message': self.message_text,
            'state': 'sent',
            'sent_date': fields.Datetime.now(),
        })

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Message Sent'),
                'message': _('LINE message sent successfully to %s') % self.partner_id.name,
                'type': 'success',
                'sticky': False,
            }
        }
