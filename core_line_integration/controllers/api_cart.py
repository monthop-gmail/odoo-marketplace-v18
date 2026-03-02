# -*- coding: utf-8 -*-
"""
Cart API endpoints for LINE Marketplace
"""
import json
import logging

from odoo import http
from odoo.http import request

from .main import (
    success_response, error_response, require_auth,
    format_order, format_order_line, get_product_image_url,
    _get_stock_status
)

_logger = logging.getLogger(__name__)


class CartApiController(http.Controller):
    """Shopping Cart API"""

    def _get_or_create_cart(self, partner):
        """Get existing cart or create new one"""
        # Use sudo with tracking_disable for API calls without login session
        SaleOrder = request.env['sale.order'].sudo().with_context(
            tracking_disable=True,
            mail_create_nosubscribe=True,
            mail_auto_subscribe_no_notify=True,
        )

        # Look for existing draft order (cart)
        cart = SaleOrder.search([
            ('partner_id', '=', partner.id),
            ('state', '=', 'draft'),
            ('source_channel', '=', 'line'),
        ], limit=1, order='create_date desc')

        if not cart:
            # Get a default user for sales (admin or first available salesperson)
            default_user = request.env.ref('base.user_admin', raise_if_not_found=False)
            if not default_user:
                default_user = request.env['res.users'].sudo().search([
                    ('active', '=', True),
                    ('share', '=', False),
                ], limit=1)

            # Get default company
            default_company = request.env['res.company'].sudo().search([], limit=1)

            # Create new cart - explicitly set required fields to avoid singleton errors
            cart = SaleOrder.create({
                'partner_id': partner.id,
                'user_id': default_user.id if default_user else False,
                'company_id': default_company.id if default_company else False,
                'source_channel': 'line',
                'source_line_channel_id': request.line_channel.id if hasattr(request, 'line_channel') else False,
            })

        return cart

    def _format_cart(self, cart):
        """Format cart for API response"""
        lines = []
        for line in cart.order_line:
            template = line.product_id.product_tmpl_id
            stock_status, qty_available, is_service = _get_stock_status(template)
            lines.append({
                'id': line.id,
                'product': {
                    'id': line.product_id.id,
                    'name': line.product_id.name,
                    'image_url': get_product_image_url(template),
                    'price': line.product_id.lst_price,
                },
                'quantity': line.product_uom_qty,
                'price_unit': line.price_unit,
                'subtotal': line.price_subtotal,
                'qty_available': qty_available,
                'stock_status': stock_status,
                'is_service': is_service,
            })

        return {
            'id': cart.id,
            'name': cart.name,
            'lines': lines,
            'item_count': sum(line['quantity'] for line in lines),
            'subtotal': cart.amount_untaxed,
            'tax': cart.amount_tax,
            'total': cart.amount_total,
            'currency': cart.currency_id.symbol,
        }

    @http.route('/api/line-buyer/cart', type='http', auth='none', methods=['GET', 'OPTIONS'], csrf=False)
    @require_auth
    def get_cart(self, **kwargs):
        """Get current cart contents"""
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            # Ensure partner exists
            if not request.line_partner:
                # Create partner if not exists
                request.line_partner = request.env['res.partner'].sudo().get_or_create_from_line(
                    request.line_user_id,
                    request.line_channel.id,
                    {'display_name': request.line_member.display_name}
                )
                request.line_member.sudo().with_context(tracking_disable=True).partner_id = request.line_partner

            cart = self._get_or_create_cart(request.line_partner)
            return success_response(self._format_cart(cart))

        except Exception as e:
            _logger.error(f'Error in get_cart: {str(e)}')
            return error_response(str(e), 500)

    @http.route('/api/line-buyer/cart/add', type='http', auth='none', methods=['POST', 'OPTIONS'], csrf=False)
    @require_auth
    def add_to_cart(self, **kwargs):
        """
        Add product to cart.

        POST body (JSON):
        - product_id: Product ID (required)
        - quantity: Quantity to add (default 1)
        """
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            # Parse JSON body
            try:
                data = json.loads(request.httprequest.data.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError):
                return error_response('Invalid JSON body', 400)

            product_id = data.get('product_id')
            quantity = float(data.get('quantity', 1))

            if not product_id:
                return error_response('product_id is required', 400)

            if quantity <= 0:
                return error_response('quantity must be positive', 400)

            # Get product — frontend sends product.template ID
            template = request.env['product.template'].sudo().browse(int(product_id))
            if not template.exists():
                return error_response('Product not found', 404)

            if not template.sale_ok:
                return error_response('Product not available for sale', 400)

            # Get first variant (product.product) for sale order line
            product = template.product_variant_id
            if not product:
                return error_response('No product variant available', 400)

            # Stock validation for storable products
            if template.type != 'service':
                available = template.qty_available if hasattr(template, 'qty_available') else 0
                if available <= 0:
                    return error_response('สินค้าหมด', 400, 'OUT_OF_STOCK')
                if quantity > available:
                    return error_response(
                        f'สต๊อกไม่เพียงพอ (เหลือ {int(available)} ชิ้น)',
                        400, 'INSUFFICIENT_STOCK'
                    )

            # Ensure partner exists
            if not request.line_partner:
                request.line_partner = request.env['res.partner'].sudo().get_or_create_from_line(
                    request.line_user_id,
                    request.line_channel.id,
                    {'display_name': request.line_member.display_name}
                )
                request.line_member.sudo().with_context(tracking_disable=True).partner_id = request.line_partner

            # Get or create cart
            cart = self._get_or_create_cart(request.line_partner)

            # Check if product already in cart
            existing_line = cart.order_line.filtered(
                lambda l: l.product_id.id == product.id
            )

            # Use context with tracking disabled
            ctx = dict(
                tracking_disable=True,
                mail_create_nosubscribe=True,
                mail_auto_subscribe_no_notify=True,
            )

            if existing_line:
                new_qty = existing_line.product_uom_qty + quantity
                # Stock validation for updated total
                if template.type != 'service':
                    available = template.qty_available if hasattr(template, 'qty_available') else 0
                    if new_qty > available:
                        return error_response(
                            f'สต๊อกไม่เพียงพอ (เหลือ {int(available)} ชิ้น, ในตะกร้า {int(existing_line.product_uom_qty)} ชิ้น)',
                            400, 'INSUFFICIENT_STOCK'
                        )
                # Update quantity
                existing_line.with_context(**ctx).product_uom_qty = new_qty
            else:
                # Add new line
                request.env['sale.order.line'].sudo().with_context(**ctx).create({
                    'order_id': cart.id,
                    'product_id': product.id,
                    'product_uom_qty': quantity,
                })

            # Reload cart
            cart = request.env['sale.order'].sudo().with_context(**ctx).browse(cart.id)

            return success_response(self._format_cart(cart), message='Product added to cart')

        except Exception as e:
            _logger.error(f'Error in add_to_cart: {str(e)}')
            return error_response(str(e), 500)

    @http.route('/api/line-buyer/cart/update', type='http', auth='none', methods=['POST', 'OPTIONS'], csrf=False)
    @require_auth
    def update_cart_line(self, **kwargs):
        """
        Update cart line quantity.

        POST body (JSON):
        - line_id: Order line ID (required)
        - quantity: New quantity (required, 0 to remove)
        """
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            data = json.loads(request.httprequest.data.decode('utf-8'))

            line_id = data.get('line_id')
            quantity = float(data.get('quantity', 0))

            if not line_id:
                return error_response('line_id is required', 400)

            # Use tracking_disable context for API operations
            ctx = dict(
                tracking_disable=True,
                mail_create_nosubscribe=True,
                mail_auto_subscribe_no_notify=True,
            )

            # Get line
            line = request.env['sale.order.line'].sudo().with_context(**ctx).browse(int(line_id))
            if not line.exists():
                return error_response('Line not found', 404)

            # Verify line belongs to user's cart
            if line.order_id.partner_id.id != request.line_partner.id:
                return error_response('Unauthorized', 403)

            if line.order_id.state != 'draft':
                return error_response('Cannot modify confirmed order', 400)

            cart_id = line.order_id.id

            if quantity <= 0:
                # Remove line
                line.with_context(**ctx).unlink()
            else:
                # Stock validation for storable products
                template = line.product_id.product_tmpl_id
                if template.type != 'service':
                    available = template.qty_available if hasattr(template, 'qty_available') else 0
                    if quantity > available:
                        return error_response(
                            f'สต๊อกไม่เพียงพอ (เหลือ {int(available)} ชิ้น)',
                            400, 'INSUFFICIENT_STOCK'
                        )
                # Update quantity
                line.with_context(**ctx).product_uom_qty = quantity

            # Reload cart
            cart = request.env['sale.order'].sudo().with_context(**ctx).browse(cart_id)
            if cart.exists():
                return success_response(self._format_cart(cart))
            else:
                return success_response({'lines': [], 'total': 0})

        except Exception as e:
            _logger.error(f'Error in update_cart_line: {str(e)}')
            return error_response(str(e), 500)

    @http.route('/api/line-buyer/cart/remove', type='http', auth='none', methods=['POST', 'OPTIONS'], csrf=False)
    @require_auth
    def remove_from_cart(self, **kwargs):
        """
        Remove item from cart.

        POST body (JSON):
        - line_id: Order line ID (required)
        """
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            data = json.loads(request.httprequest.data.decode('utf-8'))
            line_id = data.get('line_id')

            if not line_id:
                return error_response('line_id is required', 400)

            # Use tracking_disable context for API operations
            ctx = dict(
                tracking_disable=True,
                mail_create_nosubscribe=True,
                mail_auto_subscribe_no_notify=True,
            )

            line = request.env['sale.order.line'].sudo().with_context(**ctx).browse(int(line_id))
            if not line.exists():
                return error_response('Line not found', 404)

            if line.order_id.partner_id.id != request.line_partner.id:
                return error_response('Unauthorized', 403)

            cart_id = line.order_id.id
            line.with_context(**ctx).unlink()

            cart = request.env['sale.order'].sudo().with_context(**ctx).browse(cart_id)
            return success_response(self._format_cart(cart) if cart.exists() else {'lines': [], 'total': 0})

        except Exception as e:
            _logger.error(f'Error in remove_from_cart: {str(e)}')
            return error_response(str(e), 500)

    @http.route('/api/line-buyer/cart/clear', type='http', auth='none', methods=['POST', 'OPTIONS'], csrf=False)
    @require_auth
    def clear_cart(self, **kwargs):
        """Clear all items from cart"""
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            if not request.line_partner:
                return success_response({'lines': [], 'total': 0})

            # Use tracking_disable context for API operations
            ctx = dict(
                tracking_disable=True,
                mail_create_nosubscribe=True,
                mail_auto_subscribe_no_notify=True,
            )

            cart = self._get_or_create_cart(request.line_partner)
            cart.order_line.with_context(**ctx).unlink()

            return success_response(self._format_cart(cart), message='Cart cleared')

        except Exception as e:
            _logger.error(f'Error in clear_cart: {str(e)}')
            return error_response(str(e), 500)
