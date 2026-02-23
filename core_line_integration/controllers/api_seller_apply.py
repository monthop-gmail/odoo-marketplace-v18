# -*- coding: utf-8 -*-
"""
Seller Application API - allows buyers to apply as sellers via LINE LIFF

Mirrors the same flow as:
  - /my/marketplace/become_seller (existing portal user)
  - seller.resistration.wizard (admin registering a partner)
"""
import json
import logging
from ast import literal_eval

from odoo import http, _, SUPERUSER_ID
from odoo.http import request

from .main import success_response, error_response, require_auth

_logger = logging.getLogger(__name__)


class SellerApplyController(http.Controller):
    """Seller registration/application API for buyers"""

    @http.route('/api/line-buyer/seller/status', type='http', auth='none',
                methods=['GET', 'OPTIONS'], csrf=False)
    @require_auth
    def get_seller_status(self, **kwargs):
        """
        Get current user's seller status.

        Returns seller application status and info.
        """
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            partner = request.line_partner

            if not partner:
                return success_response({
                    'is_seller': False,
                    'seller_status': None,
                    'can_apply': True,
                    'message': 'ยังไม่ได้สมัครเป็นผู้ขาย',
                })

            if not partner.seller:
                return success_response({
                    'is_seller': False,
                    'seller_status': None,
                    'can_apply': True,
                    'message': 'ยังไม่ได้สมัครเป็นผู้ขาย',
                })

            result = {
                'is_seller': True,
                'seller_status': partner.state,
                'can_apply': False,
            }

            if partner.state == 'new':
                result['message'] = 'ใบสมัครยังไม่ได้ส่ง'
                result['can_apply'] = True
            elif partner.state == 'pending':
                result['message'] = 'รอการอนุมัติจากผู้ดูแลระบบ'
            elif partner.state == 'approved':
                result['message'] = 'คุณเป็นผู้ขายแล้ว'
                if partner.seller_shop_id:
                    result['shop'] = {
                        'id': partner.seller_shop_id.id,
                        'name': partner.seller_shop_id.name,
                    }
                # Include seller LIFF URL
                liff = request.env['line.liff'].sudo().search([
                    ('channel_id', '=', request.line_channel.id),
                    ('liff_type', '=', 'seller'),
                    ('active', '=', True),
                ], limit=1)
                if liff and liff.liff_url:
                    result['seller_liff'] = liff.liff_url
            elif partner.state == 'denied':
                result['message'] = 'ใบสมัครถูกปฏิเสธ กรุณาติดต่อผู้ดูแลระบบ'

            return success_response(result)

        except Exception as e:
            _logger.error(f'Error in get_seller_status: {str(e)}')
            return error_response(str(e), 500)

    @http.route('/api/line-buyer/seller/apply', type='http', auth='none',
                methods=['POST', 'OPTIONS'], csrf=False)
    @require_auth
    def apply_as_seller(self, **kwargs):
        """
        Apply to become a seller.

        POST body (JSON):
        - shop_name: Name for the seller shop (optional, defaults to user name)

        Mirrors the same logic as:
        - /my/marketplace/seller (submit_as_seller) for existing users
        - seller.resistration.wizard.confirm_customer_as_seller() for new users

        Flow:
        1. Validate profile completeness (name + phone required)
        2. Ensure res.users exists (create from portal template if needed)
        3. Set seller=True + url_handler on partner
           (same as submit_as_seller line 152-155)
        4. Move user: portal group → internal group
           (same as submit_as_seller line 157-161)
        5. Add to marketplace_draft_seller_group
           (same as submit_as_seller line 162-166)
        6. Call update_groups_for_mp_user() for config-wise groups
           (same as submit_as_seller line 167)
        7. Create seller shop
        8. Call set_to_pending() → auto-approve if configured
        9. Send notifications (same as wizard line 116)
        10. Sync LINE member type
        """
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            data = {}
            if request.httprequest.data:
                data = json.loads(request.httprequest.data.decode('utf-8'))

            member = request.line_member
            partner = request.line_partner

            # ── Validate ──

            if not partner:
                return error_response(
                    'กรุณากรอกข้อมูลโปรไฟล์ (ชื่อ, เบอร์โทร) ก่อนสมัครเป็นผู้ขาย',
                    400, 'PROFILE_REQUIRED'
                )

            if not partner.name or partner.name.startswith('LINE User'):
                return error_response(
                    'กรุณากรอกชื่อ-นามสกุล ก่อนสมัครเป็นผู้ขาย',
                    400, 'NAME_REQUIRED'
                )

            if not partner.phone and not partner.mobile:
                return error_response(
                    'กรุณากรอกเบอร์โทรศัพท์ ก่อนสมัครเป็นผู้ขาย',
                    400, 'PHONE_REQUIRED'
                )

            if partner.seller and partner.state in ('pending', 'approved'):
                status_msg = {
                    'pending': 'คุณสมัครเป็นผู้ขายแล้ว กำลังรอการอนุมัติ',
                    'approved': 'คุณเป็นผู้ขายอยู่แล้ว',
                }
                return error_response(
                    status_msg.get(partner.state, 'คุณสมัครแล้ว'),
                    400, 'ALREADY_APPLIED'
                )

            ctx = dict(
                tracking_disable=True,
                mail_create_nosubscribe=True,
                mail_auto_subscribe_no_notify=True,
            )

            # Use admin env for all operations (auth='none' has no user)
            sudo = lambda model: request.env[model].with_user(SUPERUSER_ID)
            partner_su = partner.with_user(SUPERUSER_ID)

            # ── Step 1: Ensure res.users exists ──

            user = sudo('res.users').search([
                ('partner_id', '=', partner.id)
            ], limit=1)

            if not user:
                # Ensure email exists (required for login)
                if not partner.email:
                    partner_su.with_context(**ctx).write({
                        'email': f'{member.line_user_id}@line.marketplace.local'
                    })

                # Create user from portal template
                IrConfigParam = sudo('ir.config_parameter')
                template_user_id = literal_eval(
                    IrConfigParam.get_param('base.template_portal_user_id', 'False')
                )
                if template_user_id:
                    template_user = sudo('res.users').browse(template_user_id)
                    if template_user.exists():
                        user = template_user.with_context(
                            no_reset_password=True, **ctx
                        ).copy({
                            'name': partner.name,
                            'login': partner.email,
                            'partner_id': partner.id,
                            'active': True,
                        })

                if not user:
                    # Fallback: create directly
                    user = sudo('res.users').with_context(**ctx).create({
                        'name': partner.name,
                        'login': partner.email or f'{member.line_user_id}@line.local',
                        'partner_id': partner.id,
                        'active': True,
                        'groups_id': [(4, request.env.ref('base.group_user').id)],
                    })

            # ── Step 2: Set seller=True + url_handler on partner ──

            url_handler = str(partner.id)
            partner_su.with_context(**ctx).write({
                'seller': True,
                'url_handler': url_handler,
            })

            # ── Step 3: Move portal → internal group ──

            portal_group = request.env.ref('base.group_portal', raise_if_not_found=False)
            internal_group = request.env.ref('base.group_user', raise_if_not_found=False)
            if portal_group and internal_group:
                portal_group.with_user(SUPERUSER_ID).write({"users": [(3, user.id, 0)]})
                internal_group.with_user(SUPERUSER_ID).write({"users": [(4, user.id, 0)]})

            # ── Step 4: Add to draft seller group ──

            draft_seller_group_id = sudo('ir.model.data')._xmlid_to_res_id(
                'core_marketplace.marketplace_draft_seller_group'
            )
            if draft_seller_group_id:
                groups_obj = sudo('res.groups').browse(draft_seller_group_id)
                for group_obj in groups_obj:
                    group_obj.write({"users": [(4, user.id, 0)]})

            # ── Step 5: Update config-wise groups ──

            user.with_user(SUPERUSER_ID).update_groups_for_mp_user(user)

            # ── Step 6: Set marketplace default values on partner ──

            seller_defaults = {
                'payment_method': [(6, 0, partner_su._set_payment_method())],
                'commission': sudo('ir.default')._get(
                    'res.config.settings', 'mp_commission') or 0,
                'location_id': sudo('ir.default')._get(
                    'res.config.settings', 'mp_location_id', company_id=True) or False,
                'warehouse_id': sudo('ir.default')._get(
                    'res.config.settings', 'mp_warehouse_id', company_id=True) or False,
                'auto_product_approve': sudo('ir.default')._get(
                    'res.config.settings', 'mp_auto_product_approve') or False,
                'seller_payment_limit': sudo('ir.default')._get(
                    'res.config.settings', 'mp_seller_payment_limit') or 0,
                'next_payment_request': sudo('ir.default')._get(
                    'res.config.settings', 'mp_next_payment_request') or 0,
                'auto_approve_qty': sudo('ir.default')._get(
                    'res.config.settings', 'mp_auto_approve_qty') or False,
            }
            partner_su.with_context(**ctx).write(seller_defaults)

            # ── Step 7: Create seller shop if not exists ──

            shop_name = data.get('shop_name') or f"ร้านของ {partner.name}"
            if not partner.seller_shop_id:
                # url_handler: use partner's url_handler or generate from partner id
                shop_url = f"shop-{partner.id}"

                shop = sudo('seller.shop').with_context(**ctx).create({
                    'name': shop_name,
                    'seller_id': partner.id,
                    'url_handler': shop_url,
                    'state': 'new',
                })
                partner_su.with_context(**ctx).write({
                    'seller_shop_id': shop.id,
                })

            # ── Step 8: Set to pending (auto-approves if mp config allows) ──

            partner_su.with_context(**ctx).set_to_pending()

            # ── Step 9: Send notifications ──

            try:
                user.with_user(SUPERUSER_ID).notification_on_partner_as_a_seller()
            except Exception as e:
                _logger.warning(f'Notification error (non-fatal): {e}')

            # ── Step 10: Sync LINE member type ──

            if hasattr(member, 'sync_member_type_from_partner'):
                member.with_user(SUPERUSER_ID).sync_member_type_from_partner()

            # ── Build response ──

            result = {
                'seller_status': partner.state,
                'is_seller': True,
                'shop_name': partner.seller_shop_id.name if partner.seller_shop_id else shop_name,
            }

            if partner.state == 'approved':
                result['message'] = 'ยินดีด้วย! คุณได้รับการอนุมัติเป็นผู้ขายแล้ว'
                result['seller_liff'] = None
                liff = request.env['line.liff'].sudo().search([
                    ('channel_id', '=', request.line_channel.id),
                    ('liff_type', '=', 'seller'),
                    ('active', '=', True),
                ], limit=1)
                if liff and liff.liff_url:
                    result['seller_liff'] = liff.liff_url
            else:
                result['message'] = 'สมัครเป็นผู้ขายเรียบร้อย! กรุณารอการอนุมัติจากผู้ดูแลระบบ'

            return success_response(result, message=result['message'])

        except Exception as e:
            _logger.error(f'Error in apply_as_seller: {str(e)}', exc_info=True)
            return error_response(str(e), 500)
