# -*- coding: utf-8 -*-
"""
Seller Profile, Shop & Earnings API endpoints
"""
import json
import logging

from odoo import http
from odoo.http import request

from .main import success_response, error_response
from .seller_main import require_seller, owner_only

_logger = logging.getLogger(__name__)


class SellerProfileController(http.Controller):
    """Seller Profile, Shop & Earnings API"""

    # ==================== Profile ====================

    @http.route('/api/line-seller/profile', type='http', auth='none',
                methods=['GET', 'OPTIONS'], csrf=False)
    @require_seller
    def get_profile(self, **kwargs):
        """Get seller profile with stats"""
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            seller = request.seller_partner
            base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')

            # Product counts
            Product = request.env['product.template'].sudo()
            product_domain = [('marketplace_seller_id', '=', seller.id)]
            total_products = Product.search_count(product_domain)
            approved_products = Product.search_count(product_domain + [('status', '=', 'approved')])
            pending_products = Product.search_count(product_domain + [('status', '=', 'pending')])

            # Order count
            SOL = request.env['sale.order.line'].sudo()
            total_orders = SOL.search_count([
                ('marketplace_seller_id', '=', seller.id),
                ('order_id.state', 'not in', ('draft', 'sent', 'cancel')),
                ('marketplace_state', '!=', 'new'),
            ])

            # Financial data from computed fields
            currency = seller.seller_currency_id.symbol if hasattr(seller, 'seller_currency_id') and seller.seller_currency_id else '฿'

            profile_image_url = None
            if seller.image_128:
                profile_image_url = f"{base_url}/web/image/res.partner/{seller.id}/image_128"

            # Shop info
            shop = seller.seller_shop_id if hasattr(seller, 'seller_shop_id') else None

            # Staff context
            is_shop_owner = getattr(request, 'is_shop_owner', True)
            is_shop_staff = getattr(request, 'is_shop_staff', False)
            staff_record = getattr(request, 'staff_record', None)

            staff_context = None
            if is_shop_staff and staff_record:
                staff_context = {
                    'staff_id': staff_record.id,
                    'role': staff_record.role,
                    'shop_name': staff_record.shop_id.name if staff_record.shop_id else '',
                    'owner_name': seller.name,
                }

            return success_response({
                'id': seller.id,
                'name': seller.name,
                'email': seller.email or '',
                'phone': seller.phone or seller.mobile or '',
                'state': seller.state,
                'is_shop_owner': is_shop_owner,
                'is_shop_staff': is_shop_staff,
                'staff_context': staff_context,
                'commission_rate': seller.commission if hasattr(seller, 'commission') else 0,
                'average_rating': seller.average_rating if hasattr(seller, 'average_rating') else 0,
                'profile_image_url': profile_image_url,
                'profile_msg': seller.profile_msg if hasattr(seller, 'profile_msg') else '',
                'return_policy': seller.return_policy if hasattr(seller, 'return_policy') else '',
                'shipping_policy': seller.shipping_policy if hasattr(seller, 'shipping_policy') else '',
                'stats': {
                    'total_products': total_products,
                    'approved_products': approved_products,
                    'pending_products': pending_products,
                    'total_orders': total_orders,
                    'total_sales': seller.sol_count if hasattr(seller, 'sol_count') else 0,
                    'total_earnings': seller.total_mp_payment if hasattr(seller, 'total_mp_payment') else 0,
                    'paid_amount': seller.paid_mp_payment if hasattr(seller, 'paid_mp_payment') else 0,
                    'balance_amount': seller.balance_mp_payment if hasattr(seller, 'balance_mp_payment') else 0,
                    'available_amount': seller.available_amount if hasattr(seller, 'available_amount') else 0,
                    'currency': currency,
                },
                'shop': {
                    'id': shop.id,
                    'name': shop.name,
                } if shop else None,
            })

        except Exception as e:
            _logger.error(f'Error in get_profile: {str(e)}')
            return error_response(str(e), 500)

    @http.route('/api/line-seller/profile', type='http', auth='none',
                methods=['PUT', 'OPTIONS'], csrf=False)
    @require_seller
    @owner_only
    def update_profile(self, **kwargs):
        """Update seller profile info"""
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            body = json.loads(request.httprequest.data or '{}')
            seller = request.seller_partner

            ctx = dict(
                tracking_disable=True,
                mail_create_nosubscribe=True,
                mail_auto_subscribe_no_notify=True,
            )

            allowed_fields = ['name', 'email', 'phone', 'mobile',
                              'profile_msg', 'return_policy', 'shipping_policy']
            vals = {}
            for field in allowed_fields:
                if field in body and body[field] is not None:
                    vals[field] = body[field]

            if 'profile_image' in body and body['profile_image']:
                vals['image_1920'] = body['profile_image']

            if vals:
                seller.sudo().with_context(**ctx).write(vals)

            return success_response(message='Profile updated successfully')

        except json.JSONDecodeError:
            return error_response('Invalid JSON body', 400, 'INVALID_JSON')
        except Exception as e:
            _logger.error(f'Error updating profile: {str(e)}')
            return error_response(str(e), 500)

    # ==================== Shop ====================

    @http.route('/api/line-seller/shop', type='http', auth='none',
                methods=['GET', 'OPTIONS'], csrf=False)
    @require_seller
    def get_shop(self, **kwargs):
        """Get seller's shop details"""
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            seller = request.seller_partner
            shop = seller.seller_shop_id if hasattr(seller, 'seller_shop_id') and seller.seller_shop_id else None

            if not shop:
                return error_response('Shop not found', 404, 'SHOP_NOT_FOUND')

            base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')

            shop_logo_url = None
            if shop.shop_logo:
                shop_logo_url = f"{base_url}/web/image/seller.shop/{shop.id}/shop_logo"

            shop_banner_url = None
            if shop.shop_banner:
                shop_banner_url = f"{base_url}/web/image/seller.shop/{shop.id}/shop_banner"

            return success_response({
                'id': shop.id,
                'name': shop.name,
                'description': shop.description or '',
                'shop_tag_line': shop.shop_tag_line or '',
                'email': shop.email or '',
                'phone': shop.phone or '',
                'shop_logo_url': shop_logo_url,
                'shop_banner_url': shop_banner_url,
                'url_handler': shop.url_handler or '',
                'state': shop.state,
                'total_product': shop.total_product if hasattr(shop, 'total_product') else 0,
                'street': shop.street or '',
                'street2': shop.street2 or '',
                'city': shop.city or '',
                'zip': shop.zip or '',
                'state_name': shop.state_id.name if shop.state_id else '',
                'country_name': shop.country_id.name if shop.country_id else '',
            })

        except Exception as e:
            _logger.error(f'Error in get_shop: {str(e)}')
            return error_response(str(e), 500)

    @http.route('/api/line-seller/shop', type='http', auth='none',
                methods=['PUT', 'OPTIONS'], csrf=False)
    @require_seller
    @owner_only
    def update_shop(self, **kwargs):
        """Update seller's shop details"""
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            seller = request.seller_partner
            shop = seller.seller_shop_id if hasattr(seller, 'seller_shop_id') and seller.seller_shop_id else None

            if not shop:
                return error_response('Shop not found', 404, 'SHOP_NOT_FOUND')

            body = json.loads(request.httprequest.data or '{}')

            ctx = dict(
                tracking_disable=True,
                mail_create_nosubscribe=True,
                mail_auto_subscribe_no_notify=True,
            )

            allowed_fields = ['description', 'shop_tag_line', 'email', 'phone',
                              'street', 'street2', 'city', 'zip']
            vals = {}
            for field in allowed_fields:
                if field in body and body[field] is not None:
                    vals[field] = body[field]

            if 'shop_logo' in body and body['shop_logo']:
                vals['shop_logo'] = body['shop_logo']

            if 'shop_banner' in body and body['shop_banner']:
                vals['shop_banner'] = body['shop_banner']

            if vals:
                shop.sudo().with_context(**ctx).write(vals)

            return success_response(message='Shop updated successfully')

        except json.JSONDecodeError:
            return error_response('Invalid JSON body', 400, 'INVALID_JSON')
        except Exception as e:
            _logger.error(f'Error updating shop: {str(e)}')
            return error_response(str(e), 500)

    # ==================== Earnings ====================

    @http.route('/api/line-seller/earnings', type='http', auth='none',
                methods=['GET', 'OPTIONS'], csrf=False)
    @require_seller
    def get_earnings(self, **kwargs):
        """
        Get seller earnings/commission payment history.

        Query params:
        - page, limit: Pagination
        """
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            seller = request.seller_partner
            page = int(kwargs.get('page', 1))
            limit = min(int(kwargs.get('limit', 20)), 100)
            offset = (page - 1) * limit

            Payment = request.env['seller.payment'].sudo()
            domain = [('seller_id', '=', seller.id)]

            total = Payment.search_count(domain)
            payments = Payment.search(domain, limit=limit, offset=offset, order='date desc, id desc')

            currency = seller.seller_currency_id.symbol if hasattr(seller, 'seller_currency_id') and seller.seller_currency_id else '฿'

            payment_list = []
            for p in payments:
                payment_list.append({
                    'id': p.id,
                    'name': p.name or '',
                    'date': p.date.isoformat() if p.date else None,
                    'amount': p.payable_amount,
                    'state': p.state,
                    'state_display': dict(p._fields['state'].selection).get(p.state, ''),
                    'payment_mode': p.payment_mode if hasattr(p, 'payment_mode') else '',
                    'memo': p.memo or '',
                    'description': p.description or '',
                    'is_cashable': p.is_cashable if hasattr(p, 'is_cashable') else False,
                })

            return success_response({
                'summary': {
                    'total_earned': seller.total_mp_payment if hasattr(seller, 'total_mp_payment') else 0,
                    'total_paid': seller.paid_mp_payment if hasattr(seller, 'paid_mp_payment') else 0,
                    'balance': seller.balance_mp_payment if hasattr(seller, 'balance_mp_payment') else 0,
                    'available_for_withdrawal': seller.available_amount if hasattr(seller, 'available_amount') else 0,
                    'currency': currency,
                },
                'payments': payment_list,
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': total,
                    'pages': (total + limit - 1) // limit if limit > 0 else 0,
                },
            })

        except Exception as e:
            _logger.error(f'Error in get_earnings: {str(e)}')
            return error_response(str(e), 500)
