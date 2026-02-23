# -*- coding: utf-8 -*-
"""
Seller Order Management API endpoints
"""
import logging

from odoo import http
from odoo.http import request

from .main import success_response, error_response
from .seller_main import (
    require_seller, format_seller_order_line, format_seller_order_detail
)

_logger = logging.getLogger(__name__)


class SellerOrdersController(http.Controller):
    """Seller Order Management API"""

    @http.route('/api/line-seller/orders', type='http', auth='none',
                methods=['GET', 'OPTIONS'], csrf=False)
    @require_seller
    def get_orders(self, **kwargs):
        """
        List seller's order lines with filtering and pagination.

        Query params:
        - page: Page number (default 1)
        - limit: Items per page (default 20, max 100)
        - status: Filter by marketplace_state (all, pending, approved, shipped, done, cancel)
        """
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            seller_id = request.seller_partner.id
            page = int(kwargs.get('page', 1))
            limit = min(int(kwargs.get('limit', 20)), 100)
            offset = (page - 1) * limit
            status = kwargs.get('status', 'all')

            # Base domain
            domain = [
                ('marketplace_seller_id', '=', seller_id),
                ('order_id.state', 'not in', ('draft', 'sent')),
                ('marketplace_state', '!=', 'new'),
            ]

            # Status filter
            if status and status != 'all':
                domain.append(('marketplace_state', '=', status))

            SOL = request.env['sale.order.line'].sudo()
            total = SOL.search_count(domain)
            lines = SOL.search(domain, limit=limit, offset=offset, order='create_date desc')

            return success_response({
                'orders': [format_seller_order_line(l) for l in lines],
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': total,
                    'pages': (total + limit - 1) // limit if limit > 0 else 0,
                },
            })

        except Exception as e:
            _logger.error(f'Error in get_orders: {str(e)}')
            return error_response(str(e), 500)

    @http.route('/api/line-seller/orders/<int:line_id>', type='http', auth='none',
                methods=['GET', 'OPTIONS'], csrf=False)
    @require_seller
    def get_order_detail(self, line_id, **kwargs):
        """Get order line detail with customer, shipping, and all seller lines."""
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            line = request.env['sale.order.line'].sudo().browse(line_id)
            if not line.exists():
                return error_response('Order line not found', 404, 'ORDER_NOT_FOUND')

            # Verify ownership
            if line.marketplace_seller_id.id != request.seller_partner.id:
                return error_response('Unauthorized', 403, 'UNAUTHORIZED')

            return success_response(format_seller_order_detail(line))

        except Exception as e:
            _logger.error(f'Error in get_order_detail: {str(e)}')
            return error_response(str(e), 500)

    @http.route('/api/line-seller/orders/<int:line_id>/approve', type='http', auth='none',
                methods=['POST', 'OPTIONS'], csrf=False)
    @require_seller
    def approve_order(self, line_id, **kwargs):
        """Approve an order line: pending → approved"""
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            line = request.env['sale.order.line'].sudo().browse(line_id)
            if not line.exists():
                return error_response('Order line not found', 404, 'ORDER_NOT_FOUND')

            if line.marketplace_seller_id.id != request.seller_partner.id:
                return error_response('Unauthorized', 403, 'UNAUTHORIZED')

            if line.marketplace_state != 'pending':
                return error_response(
                    f'Cannot approve order in state: {line.marketplace_state}',
                    400, 'INVALID_STATE'
                )

            line.button_approve_ol()

            return success_response(
                format_seller_order_line(line),
                message='Order approved successfully'
            )

        except Exception as e:
            _logger.error(f'Error approving order: {str(e)}')
            return error_response(str(e), 500)

    @http.route('/api/line-seller/orders/<int:line_id>/ship', type='http', auth='none',
                methods=['POST', 'OPTIONS'], csrf=False)
    @require_seller
    def ship_order(self, line_id, **kwargs):
        """Mark order as shipped: approved → shipped"""
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            line = request.env['sale.order.line'].sudo().browse(line_id)
            if not line.exists():
                return error_response('Order line not found', 404, 'ORDER_NOT_FOUND')

            if line.marketplace_seller_id.id != request.seller_partner.id:
                return error_response('Unauthorized', 403, 'UNAUTHORIZED')

            if line.marketplace_state != 'approved':
                return error_response(
                    f'Cannot ship order in state: {line.marketplace_state}',
                    400, 'INVALID_STATE'
                )

            line.sudo().marketplace_state = 'shipped'

            return success_response(
                format_seller_order_line(line),
                message='Order marked as shipped'
            )

        except Exception as e:
            _logger.error(f'Error shipping order: {str(e)}')
            return error_response(str(e), 500)

    @http.route('/api/line-seller/orders/<int:line_id>/done', type='http', auth='none',
                methods=['POST', 'OPTIONS'], csrf=False)
    @require_seller
    def mark_done(self, line_id, **kwargs):
        """Mark order as done: shipped → done"""
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            line = request.env['sale.order.line'].sudo().browse(line_id)
            if not line.exists():
                return error_response('Order line not found', 404, 'ORDER_NOT_FOUND')

            if line.marketplace_seller_id.id != request.seller_partner.id:
                return error_response('Unauthorized', 403, 'UNAUTHORIZED')

            if line.marketplace_state not in ('shipped', 'approved'):
                return error_response(
                    f'Cannot mark done in state: {line.marketplace_state}',
                    400, 'INVALID_STATE'
                )

            line.action_mark_done()

            return success_response(
                format_seller_order_line(line),
                message='Order marked as done'
            )

        except Exception as e:
            _logger.error(f'Error marking done: {str(e)}')
            return error_response(str(e), 500)

    @http.route('/api/line-seller/orders/<int:line_id>/cancel', type='http', auth='none',
                methods=['POST', 'OPTIONS'], csrf=False)
    @require_seller
    def cancel_order(self, line_id, **kwargs):
        """Cancel an order line: pending/approved → cancel"""
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            line = request.env['sale.order.line'].sudo().browse(line_id)
            if not line.exists():
                return error_response('Order line not found', 404, 'ORDER_NOT_FOUND')

            if line.marketplace_seller_id.id != request.seller_partner.id:
                return error_response('Unauthorized', 403, 'UNAUTHORIZED')

            if line.marketplace_state not in ('pending', 'approved'):
                return error_response(
                    f'Cannot cancel order in state: {line.marketplace_state}',
                    400, 'INVALID_STATE'
                )

            line.button_cancel()

            return success_response(
                format_seller_order_line(line),
                message='Order cancelled'
            )

        except Exception as e:
            _logger.error(f'Error cancelling order: {str(e)}')
            return error_response(str(e), 500)
