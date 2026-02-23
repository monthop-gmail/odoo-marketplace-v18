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
from odoo import api, models
from odoo.http import request
import logging
_logger = logging.getLogger(__name__)

class Http(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        """Update Session value for draft seller and seller.

        Note: In Odoo 18, most session info is already included by default.
        HomeStaticTemplateHelpers was deprecated and removed in Odoo 18.
        """
        session_info = super(Http, self).session_info()
        user = request.env.user

        # Add seller-specific info if user is a seller
        if hasattr(user, 'check_user_is_draft_seller') and hasattr(user, 'check_user_is_seller'):
            if user.check_user_is_draft_seller() or user.check_user_is_seller():
                session_info.update({
                    "show_effect": True,
                    "display_switch_company_menu": user.has_group('base.group_multi_company') and len(user.company_ids) > 1,
                })
        return session_info
