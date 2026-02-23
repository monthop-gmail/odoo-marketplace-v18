# -*- coding: utf-8 -*-
"""
Checkout and Orders API endpoints for LINE Marketplace
"""
import json
import logging

from odoo import http
from odoo.http import request

from .main import (
    success_response, error_response, require_auth,
    format_order, format_order_line
)

_logger = logging.getLogger(__name__)


class CheckoutApiController(http.Controller):
    """Checkout and Orders API"""

    @http.route('/api/line-buyer/checkout/shipping-addresses', type='http', auth='none',
                methods=['GET', 'OPTIONS'], csrf=False)
    @require_auth
    def get_shipping_addresses(self, **kwargs):
        """Get saved shipping addresses for current user"""
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            if not request.line_partner:
                return success_response({'addresses': []})

            # Get partner's child addresses (delivery addresses)
            addresses = request.env['res.partner'].sudo().search([
                '|',
                ('id', '=', request.line_partner.id),
                ('parent_id', '=', request.line_partner.id),
                ('type', 'in', ['delivery', 'contact']),
            ])

            result = []
            for addr in addresses:
                result.append({
                    'id': addr.id,
                    'name': addr.name,
                    'street': addr.street or '',
                    'street2': addr.street2 or '',
                    'city': addr.city or '',
                    'state': addr.state_id.name if addr.state_id else '',
                    'zip': addr.zip or '',
                    'country': addr.country_id.name if addr.country_id else '',
                    'phone': addr.phone or addr.mobile or '',
                    'is_default': addr.id == request.line_partner.id,
                })

            return success_response({'addresses': result})

        except Exception as e:
            _logger.error(f'Error in get_shipping_addresses: {str(e)}')
            return error_response(str(e), 500)

    @http.route('/api/line-buyer/checkout/shipping-address', type='http', auth='none',
                methods=['POST', 'OPTIONS'], csrf=False)
    @require_auth
    def save_shipping_address(self, **kwargs):
        """
        Save a new shipping address.

        POST body (JSON):
        - name: Recipient name
        - street: Address line 1
        - street2: Address line 2 (optional)
        - city: City
        - state_id: State/Province ID (optional)
        - zip: Postal code
        - country_id: Country ID (optional, default Thailand)
        - phone: Phone number
        """
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            data = json.loads(request.httprequest.data.decode('utf-8'))

            if not request.line_partner:
                return error_response('User not found', 404)

            # Validate required fields
            required = ['name', 'street', 'phone']
            for field in required:
                if not data.get(field):
                    return error_response(f'{field} is required', 400)

            # Get Thailand as default country
            thailand = request.env['res.country'].sudo().search([('code', '=', 'TH')], limit=1)

            # Get default company
            default_company = request.env['res.company'].sudo().search([], limit=1)

            # Get admin user for write operation
            admin_user = request.env.ref('base.user_admin', raise_if_not_found=False)
            if not admin_user:
                admin_user = request.env['res.users'].sudo().search([
                    ('active', '=', True),
                    ('share', '=', False),
                ], limit=1)

            # Use tracking_disable context for API creates
            ctx = dict(
                tracking_disable=True,
                mail_create_nosubscribe=True,
                mail_auto_subscribe_no_notify=True,
            )
            if admin_user:
                Partner = request.env['res.partner'].with_user(admin_user).with_context(**ctx)
            else:
                Partner = request.env['res.partner'].sudo().with_context(**ctx)

            address = Partner.create({
                'parent_id': request.line_partner.id,
                'type': 'delivery',
                'name': data['name'],
                'street': data['street'],
                'street2': data.get('street2', ''),
                'city': data.get('city', ''),
                'state_id': data.get('state_id'),
                'zip': data.get('zip', ''),
                'country_id': data.get('country_id') or thailand.id,
                'phone': data['phone'],
                'company_id': default_company.id if default_company else False,
            })

            return success_response({
                'id': address.id,
                'name': address.name,
            }, message='Address saved')

        except Exception as e:
            _logger.error(f'Error in save_shipping_address: {str(e)}')
            return error_response(str(e), 500)

    @http.route('/api/line-buyer/checkout/confirm', type='http', auth='none',
                methods=['POST', 'OPTIONS'], csrf=False)
    @require_auth
    def confirm_order(self, **kwargs):
        """
        Confirm order (checkout).

        POST body (JSON):
        - shipping_address_id: Delivery address ID (optional, use default if not provided)
        - note: Order note (optional)
        """
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            data = json.loads(request.httprequest.data.decode('utf-8'))

            if not request.line_partner:
                return error_response('User not found', 404)

            # Use tracking_disable context for API operations
            ctx = dict(
                tracking_disable=True,
                mail_create_nosubscribe=True,
                mail_auto_subscribe_no_notify=True,
            )

            # Get cart
            SaleOrder = request.env['sale.order'].sudo().with_context(**ctx)
            cart = SaleOrder.search([
                ('partner_id', '=', request.line_partner.id),
                ('state', '=', 'draft'),
                ('source_channel', '=', 'line'),
            ], limit=1, order='create_date desc')

            if not cart or not cart.order_line:
                return error_response('Cart is empty', 400, 'EMPTY_CART')

            # Update shipping address if provided
            shipping_address_id = data.get('shipping_address_id')
            if shipping_address_id:
                cart.with_context(**ctx).partner_shipping_id = int(shipping_address_id)

            # Add note
            if data.get('note'):
                cart.with_context(**ctx).note = data['note']

            # Get admin user for confirmation (action_confirm needs proper user context)
            admin_user = request.env.ref('base.user_admin', raise_if_not_found=False)
            if not admin_user:
                admin_user = request.env['res.users'].sudo().search([
                    ('active', '=', True),
                    ('share', '=', False),
                ], limit=1)

            # Confirm order with admin context
            if admin_user:
                cart_with_user = cart.with_user(admin_user).with_context(**ctx)
            else:
                cart_with_user = cart.with_context(**ctx)
            cart_with_user.action_confirm()

            return success_response({
                'order': format_order(cart),
            }, message='Order confirmed')

        except Exception as e:
            _logger.error(f'Error in confirm_order: {str(e)}')
            return error_response(str(e), 500)

    @http.route('/api/line-buyer/orders', type='http', auth='none', methods=['GET', 'OPTIONS'], csrf=False)
    @require_auth
    def get_orders(self, **kwargs):
        """
        Get order history.

        Query params:
        - page: Page number (default 1)
        - limit: Items per page (default 10)
        - state: Filter by state (optional)
        """
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            if not request.line_partner:
                return success_response({'orders': [], 'pagination': {'total': 0}})

            page = int(kwargs.get('page', 1))
            limit = min(int(kwargs.get('limit', 10)), 50)
            offset = (page - 1) * limit

            domain = [
                ('partner_id', '=', request.line_partner.id),
                ('state', '!=', 'draft'),  # Exclude draft orders (carts)
            ]

            state = kwargs.get('state')
            if state:
                domain.append(('state', '=', state))

            SaleOrder = request.env['sale.order'].sudo()
            total = SaleOrder.search_count(domain)
            orders = SaleOrder.search(domain, limit=limit, offset=offset, order='date_order desc')

            return success_response({
                'orders': [format_order(o, include_lines=False) for o in orders],
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': total,
                    'pages': (total + limit - 1) // limit,
                }
            })

        except Exception as e:
            _logger.error(f'Error in get_orders: {str(e)}')
            return error_response(str(e), 500)

    @http.route('/api/line-buyer/orders/<int:order_id>', type='http', auth='none',
                methods=['GET', 'OPTIONS'], csrf=False)
    @require_auth
    def get_order_detail(self, order_id, **kwargs):
        """Get order details by ID"""
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            if not request.line_partner:
                return error_response('User not found', 404)

            order = request.env['sale.order'].sudo().browse(order_id)

            if not order.exists():
                return error_response('Order not found', 404)

            if order.partner_id.id != request.line_partner.id:
                return error_response('Unauthorized', 403)

            result = format_order(order, include_lines=True)

            # Add shipping info
            if order.partner_shipping_id:
                result['shipping_address'] = {
                    'name': order.partner_shipping_id.name,
                    'street': order.partner_shipping_id.street or '',
                    'city': order.partner_shipping_id.city or '',
                    'phone': order.partner_shipping_id.phone or '',
                }

            return success_response(result)

        except Exception as e:
            _logger.error(f'Error in get_order_detail: {str(e)}')
            return error_response(str(e), 500)

    @http.route('/api/line-buyer/orders/<int:order_id>/cancel', type='http', auth='none',
                methods=['POST', 'OPTIONS'], csrf=False)
    @require_auth
    def cancel_order(self, order_id, **kwargs):
        """
        Request order cancellation.
        Only allowed for orders in 'sale' state.
        """
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            if not request.line_partner:
                return error_response('User not found', 404)

            order = request.env['sale.order'].sudo().browse(order_id)

            if not order.exists():
                return error_response('Order not found', 404)

            if order.partner_id.id != request.line_partner.id:
                return error_response('Unauthorized', 403)

            if order.state != 'sale':
                return error_response(
                    f'Cannot cancel order in {order.state} state',
                    400, 'CANNOT_CANCEL'
                )

            # Cancel the order
            order.action_cancel()

            return success_response(format_order(order), message='Order cancelled')

        except Exception as e:
            _logger.error(f'Error in cancel_order: {str(e)}')
            return error_response(str(e), 500)

    @http.route('/api/line-buyer/orders/<int:order_id>/reorder', type='http', auth='none',
                methods=['POST', 'OPTIONS'], csrf=False)
    @require_auth
    def reorder(self, order_id, **kwargs):
        """
        Add all items from a previous order to cart.
        """
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            if not request.line_partner:
                return error_response('User not found', 404)

            order = request.env['sale.order'].sudo().browse(order_id)

            if not order.exists():
                return error_response('Order not found', 404)

            if order.partner_id.id != request.line_partner.id:
                return error_response('Unauthorized', 403)

            # Use tracking_disable context for API operations
            ctx = dict(
                tracking_disable=True,
                mail_create_nosubscribe=True,
                mail_auto_subscribe_no_notify=True,
            )

            # Get or create cart
            SaleOrder = request.env['sale.order'].sudo().with_context(**ctx)
            cart = SaleOrder.search([
                ('partner_id', '=', request.line_partner.id),
                ('state', '=', 'draft'),
                ('source_channel', '=', 'line'),
            ], limit=1)

            if not cart:
                # Get a default user for sales
                default_user = request.env.ref('base.user_admin', raise_if_not_found=False)
                if not default_user:
                    default_user = request.env['res.users'].sudo().search([
                        ('active', '=', True),
                        ('share', '=', False),
                    ], limit=1)

                # Get default company
                default_company = request.env['res.company'].sudo().search([], limit=1)

                cart = SaleOrder.create({
                    'partner_id': request.line_partner.id,
                    'user_id': default_user.id if default_user else False,
                    'company_id': default_company.id if default_company else False,
                    'source_channel': 'line',
                    'source_line_channel_id': request.line_channel.id if hasattr(request, 'line_channel') else False,
                })

            # Add items from previous order
            OrderLine = request.env['sale.order.line'].sudo().with_context(**ctx)
            for line in order.order_line:
                if line.product_id.active and line.product_id.sale_ok:
                    existing_line = cart.order_line.filtered(
                        lambda l: l.product_id.id == line.product_id.id
                    )
                    if existing_line:
                        existing_line.with_context(**ctx).product_uom_qty += line.product_uom_qty
                    else:
                        OrderLine.create({
                            'order_id': cart.id,
                            'product_id': line.product_id.id,
                            'product_uom_qty': line.product_uom_qty,
                        })

            return success_response({
                'cart_id': cart.id,
                'item_count': len(cart.order_line),
            }, message='Items added to cart')

        except Exception as e:
            _logger.error(f'Error in reorder: {str(e)}')
            return error_response(str(e), 500)
