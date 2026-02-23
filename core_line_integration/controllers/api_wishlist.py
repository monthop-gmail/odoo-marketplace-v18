# -*- coding: utf-8 -*-
"""
Wishlist API endpoints for LINE Marketplace
"""
import json
import logging

from odoo import http
from odoo.http import request

from .main import (
    success_response, error_response, require_auth,
    format_product, get_product_image_url
)

_logger = logging.getLogger(__name__)


class WishlistApiController(http.Controller):
    """Wishlist API"""

    def _format_wishlist_item(self, item):
        """Format wishlist item for API response"""
        return {
            'id': item.id,
            'product': {
                'id': item.product_id.id,
                'name': item.product_id.name,
                'price': item.current_price,
                'original_price': item.product_price,
                'price_dropped': item.price_dropped,
                'image_url': get_product_image_url(item.product_id),
                'is_published': item.product_id.is_published,
                'available': item.product_id.sale_ok,
            },
            'added_date': item.create_date.isoformat() if item.create_date else None,
            'notes': item.notes,
        }

    @http.route('/api/line-buyer/wishlist', type='http', auth='none',
                methods=['GET', 'OPTIONS'], csrf=False)
    @require_auth
    def get_wishlist(self, **kwargs):
        """
        Get user's wishlist.

        Query params:
        - page: Page number (default 1)
        - limit: Items per page (default 20, max 100)
        """
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            if not request.line_partner:
                return success_response({'items': [], 'total': 0})

            # Pagination
            page = int(kwargs.get('page', 1))
            limit = min(int(kwargs.get('limit', 20)), 100)
            offset = (page - 1) * limit

            Wishlist = request.env['line.wishlist'].sudo()
            domain = [('partner_id', '=', request.line_partner.id)]

            total = Wishlist.search_count(domain)
            items = Wishlist.search(domain, limit=limit, offset=offset, order='create_date desc')

            return success_response({
                'items': [self._format_wishlist_item(item) for item in items],
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': total,
                    'pages': (total + limit - 1) // limit if limit else 0,
                }
            })

        except Exception as e:
            _logger.error(f'Error in get_wishlist: {str(e)}')
            return error_response(str(e), 500)

    @http.route('/api/line-buyer/wishlist/add', type='http', auth='none',
                methods=['POST', 'OPTIONS'], csrf=False)
    @require_auth
    def add_to_wishlist(self, **kwargs):
        """
        Add product to wishlist.

        POST body (JSON):
        - product_id: Product template ID (required)
        - notes: Optional notes
        """
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            data = json.loads(request.httprequest.data.decode('utf-8'))
            product_id = data.get('product_id')
            notes = data.get('notes', '')

            if not product_id:
                return error_response('product_id is required', 400)

            # Verify product exists and is published
            product = request.env['product.template'].sudo().browse(int(product_id))
            if not product.exists():
                return error_response('Product not found', 404, 'PRODUCT_NOT_FOUND')

            if not product.is_published:
                return error_response('Product not available', 400, 'PRODUCT_NOT_AVAILABLE')

            # Ensure partner exists
            if not request.line_partner:
                request.line_partner = request.env['res.partner'].sudo().get_or_create_from_line(
                    request.line_user_id,
                    request.line_channel.id,
                    {'display_name': request.line_member.display_name}
                )
                request.line_member.sudo().with_context(tracking_disable=True).partner_id = request.line_partner

            # Check if already in wishlist
            Wishlist = request.env['line.wishlist'].sudo()
            existing = Wishlist.search([
                ('partner_id', '=', request.line_partner.id),
                ('product_id', '=', product.id),
            ], limit=1)

            if existing:
                return error_response('Product already in wishlist', 400, 'ALREADY_IN_WISHLIST')

            # Add to wishlist
            item = Wishlist.create({
                'partner_id': request.line_partner.id,
                'product_id': product.id,
                'channel_id': request.line_channel.id if hasattr(request, 'line_channel') else False,
                'notes': notes,
            })

            return success_response(
                self._format_wishlist_item(item),
                message='Product added to wishlist'
            )

        except Exception as e:
            _logger.error(f'Error in add_to_wishlist: {str(e)}')
            return error_response(str(e), 500)

    @http.route('/api/line-buyer/wishlist/remove', type='http', auth='none',
                methods=['POST', 'OPTIONS'], csrf=False)
    @require_auth
    def remove_from_wishlist(self, **kwargs):
        """
        Remove product from wishlist.

        POST body (JSON):
        - product_id: Product template ID (required)
        OR
        - item_id: Wishlist item ID
        """
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            data = json.loads(request.httprequest.data.decode('utf-8'))
            product_id = data.get('product_id')
            item_id = data.get('item_id')

            if not product_id and not item_id:
                return error_response('product_id or item_id is required', 400)

            if not request.line_partner:
                return error_response('Wishlist is empty', 404)

            Wishlist = request.env['line.wishlist'].sudo()

            if item_id:
                item = Wishlist.browse(int(item_id))
                if not item.exists():
                    return error_response('Item not found', 404)
                if item.partner_id.id != request.line_partner.id:
                    return error_response('Unauthorized', 403)
            else:
                item = Wishlist.search([
                    ('partner_id', '=', request.line_partner.id),
                    ('product_id', '=', int(product_id)),
                ], limit=1)

                if not item:
                    return error_response('Product not in wishlist', 404, 'NOT_IN_WISHLIST')

            item.unlink()

            return success_response(message='Product removed from wishlist')

        except Exception as e:
            _logger.error(f'Error in remove_from_wishlist: {str(e)}')
            return error_response(str(e), 500)

    @http.route('/api/line-buyer/wishlist/check/<int:product_id>', type='http', auth='none',
                methods=['GET', 'OPTIONS'], csrf=False)
    @require_auth
    def check_in_wishlist(self, product_id, **kwargs):
        """Check if product is in user's wishlist"""
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            if not request.line_partner:
                return success_response({'in_wishlist': False})

            exists = request.env['line.wishlist'].sudo().search_count([
                ('partner_id', '=', request.line_partner.id),
                ('product_id', '=', product_id),
            ]) > 0

            return success_response({'in_wishlist': exists})

        except Exception as e:
            _logger.error(f'Error in check_in_wishlist: {str(e)}')
            return error_response(str(e), 500)

    @http.route('/api/line-buyer/wishlist/clear', type='http', auth='none',
                methods=['POST', 'OPTIONS'], csrf=False)
    @require_auth
    def clear_wishlist(self, **kwargs):
        """Clear entire wishlist"""
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            if not request.line_partner:
                return success_response(message='Wishlist cleared')

            request.env['line.wishlist'].sudo().search([
                ('partner_id', '=', request.line_partner.id)
            ]).unlink()

            return success_response(message='Wishlist cleared')

        except Exception as e:
            _logger.error(f'Error in clear_wishlist: {str(e)}')
            return error_response(str(e), 500)

    @http.route('/api/line-buyer/wishlist/move-to-cart', type='http', auth='none',
                methods=['POST', 'OPTIONS'], csrf=False)
    @require_auth
    def move_to_cart(self, **kwargs):
        """
        Move wishlist item to cart.

        POST body (JSON):
        - product_id: Product template ID (required)
        - quantity: Quantity to add (default 1)
        - remove_from_wishlist: Remove from wishlist after adding (default true)
        """
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            data = json.loads(request.httprequest.data.decode('utf-8'))
            product_id = data.get('product_id')
            quantity = float(data.get('quantity', 1))
            remove_from_wishlist = data.get('remove_from_wishlist', True)

            if not product_id:
                return error_response('product_id is required', 400)

            # Get product variant
            product_tmpl = request.env['product.template'].sudo().browse(int(product_id))
            if not product_tmpl.exists():
                return error_response('Product not found', 404)

            # Get the first variant
            product = product_tmpl.product_variant_id
            if not product:
                return error_response('Product variant not found', 404)

            if not product.sale_ok:
                return error_response('Product not available for sale', 400)

            # Ensure partner exists
            if not request.line_partner:
                request.line_partner = request.env['res.partner'].sudo().get_or_create_from_line(
                    request.line_user_id,
                    request.line_channel.id,
                    {'display_name': request.line_member.display_name}
                )
                request.line_member.sudo().with_context(tracking_disable=True).partner_id = request.line_partner

            # Import cart controller to reuse cart logic
            from .api_cart import CartApiController
            cart_controller = CartApiController()
            cart = cart_controller._get_or_create_cart(request.line_partner)

            # Add to cart
            ctx = dict(
                tracking_disable=True,
                mail_create_nosubscribe=True,
                mail_auto_subscribe_no_notify=True,
            )

            existing_line = cart.order_line.filtered(lambda l: l.product_id.id == product.id)
            if existing_line:
                existing_line.with_context(**ctx).product_uom_qty += quantity
            else:
                request.env['sale.order.line'].sudo().with_context(**ctx).create({
                    'order_id': cart.id,
                    'product_id': product.id,
                    'product_uom_qty': quantity,
                })

            # Remove from wishlist if requested
            if remove_from_wishlist and request.line_partner:
                request.env['line.wishlist'].sudo().search([
                    ('partner_id', '=', request.line_partner.id),
                    ('product_id', '=', product_tmpl.id),
                ]).unlink()

            return success_response(message='Product moved to cart')

        except Exception as e:
            _logger.error(f'Error in move_to_cart: {str(e)}')
            return error_response(str(e), 500)
