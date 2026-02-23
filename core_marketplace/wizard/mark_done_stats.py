# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# License URL : https://store.webkul.com/license.html/
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################

from odoo import api, fields, models, _

class BulkActionDetails(models.TransientModel):
    _name = "bulk.action.details"
    _description = "Show Stats Details after bulk mark done "

    @api.model
    def _get_order(self):
        """ set default value for sale_order_line_ids """
        result = self.env['sale.order.line'].browse(
            self._context['active_ids'])
        return result.ids

    sale_order_line_ids = fields.Many2many(
        "sale.order.line", string="Sale order line", default=_get_order)

    def mark_done_all(self):
        """ change order line status to done"""
        success_order_line = self.sale_order_line_ids.filtered(lambda so : so.marketplace_state == 'shipped' or so.marketplace_state == 'approved' and so.product_type == 'service')
        success_order_line.action_mark_done()
        msg = "<p style='font-size: 15px'>" + _("Total number of orders marked done:") + "<strong>" + str(len(success_order_line)) + "</strong></p>"
        return self.env["mp.wizard.message"].generated_message(msg, _("Marked Done Status"))
