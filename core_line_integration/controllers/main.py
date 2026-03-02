# -*- coding: utf-8 -*-
"""
Base controller with common utilities for LINE Marketplace API
"""
import json
import logging
from functools import wraps

from odoo import http
from odoo.http import request, Response

_logger = logging.getLogger(__name__)


def json_response(data, status=200):
    """Create a JSON response with proper headers"""
    return Response(
        json.dumps(data, ensure_ascii=False, default=str),
        status=status,
        mimetype='application/json',
        headers=[
            ('Access-Control-Allow-Origin', '*'),
            ('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS'),
            ('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Line-User-Id, X-Channel-Code'),
        ]
    )


def error_response(message, status=400, code=None):
    """Create an error response"""
    data = {
        'success': False,
        'error': {
            'message': message,
            'code': code or f'ERR_{status}',
        }
    }
    return json_response(data, status)


def success_response(data=None, message=None):
    """Create a success response"""
    response = {'success': True}
    if data is not None:
        response['data'] = data
    if message:
        response['message'] = message
    return json_response(response, 200)


def require_auth(func):
    """
    Decorator to require authentication.
    In production: validates LINE access token (from LIFF)
    In mock mode: accepts X-Line-User-Id header
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        mock_auth = request.env['ir.config_parameter'].sudo().get_param(
            'core_line_integration.mock_auth', 'True'
        ) == 'True'

        if mock_auth:
            # Mock authentication mode
            line_user_id = request.httprequest.headers.get('X-Line-User-Id')
            channel_code = request.httprequest.headers.get('X-Channel-Code', 'demo_coop')

            if not line_user_id:
                return error_response('Missing X-Line-User-Id header', 401, 'AUTH_REQUIRED')

            # Get or create member
            channel = request.env['line.channel'].sudo().search([
                ('code', '=', channel_code)
            ], limit=1)

            if not channel:
                return error_response(f'Channel not found: {channel_code}', 404, 'CHANNEL_NOT_FOUND')

            member = request.env['line.channel.member'].sudo().get_or_create_member(
                channel.id,
                line_user_id,
                {'display_name': f'Test User {line_user_id[:8]}'}
            )

            # Store in request for later use
            request.line_user_id = line_user_id
            request.line_channel = channel
            request.line_member = member
            request.line_partner = member.partner_id

        else:
            # Production mode - validate LINE access token (from LIFF)
            auth_header = request.httprequest.headers.get('Authorization')
            channel_code = request.httprequest.headers.get('X-Channel-Code')

            if not auth_header:
                return error_response('Missing Authorization header', 401, 'AUTH_REQUIRED')

            # Extract Bearer token
            if not auth_header.startswith('Bearer '):
                return error_response('Invalid Authorization header format', 401, 'INVALID_AUTH')

            access_token = auth_header[7:]  # Remove 'Bearer ' prefix

            if not channel_code:
                return error_response('Missing X-Channel-Code header', 401, 'CHANNEL_REQUIRED')

            # Get channel
            channel = request.env['line.channel'].sudo().search([
                ('code', '=', channel_code),
                ('active', '=', True),
            ], limit=1)

            if not channel:
                return error_response(f'Channel not found: {channel_code}', 404, 'CHANNEL_NOT_FOUND')

            # Validate LIFF access token
            try:
                from ..services.line_api import LineApiService, LineApiError

                line_service = LineApiService(
                    channel.channel_access_token,
                    channel.channel_secret
                )

                # Verify token and get user profile
                token_info = line_service.verify_access_token(access_token)
                profile = line_service.get_token_profile(access_token)

                line_user_id = profile.get('userId')
                if not line_user_id:
                    return error_response('Failed to get LINE user ID', 401, 'INVALID_TOKEN')

                # Get or create member with context for API operations
                ctx = dict(
                    tracking_disable=True,
                    mail_create_nosubscribe=True,
                    mail_auto_subscribe_no_notify=True,
                )

                member = request.env['line.channel.member'].sudo().with_context(**ctx).get_or_create_member(
                    channel.id,
                    line_user_id,
                    {
                        'display_name': profile.get('displayName', ''),
                        'picture_url': profile.get('pictureUrl', ''),
                    }
                )

                # Store in request for later use
                request.line_user_id = line_user_id
                request.line_channel = channel
                request.line_member = member
                request.line_partner = member.partner_id
                request.line_access_token = access_token

            except Exception as e:
                _logger.error(f'LINE auth failed: {e}')
                return error_response('Invalid LINE access token', 401, 'INVALID_TOKEN')

        return func(*args, **kwargs)
    return wrapper


def get_product_image_url(product, field='image_256'):
    """Get product image URL"""
    base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
    if product[field]:
        return f"{base_url}/web/image/product.template/{product.id}/{field}"
    return f"{base_url}/web/static/img/placeholder.png"


def _get_stock_status(product):
    """Determine stock status for a product.
    Returns (stock_status, qty_available, is_service).
    Service products are always 'in_stock'.
    """
    LOW_STOCK_THRESHOLD = 5
    is_service = product.type == 'service'
    qty = product.qty_available if hasattr(product, 'qty_available') else 0

    if is_service:
        return 'in_stock', qty, True

    if qty <= 0:
        return 'out_of_stock', qty, False
    elif qty <= LOW_STOCK_THRESHOLD:
        return 'low_stock', qty, False
    else:
        return 'in_stock', qty, False


def format_product(product, include_details=False):
    """Format product for API response"""
    base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')

    stock_status, qty_available, is_service = _get_stock_status(product)

    data = {
        'id': product.id,
        'name': product.name,
        'price': product.list_price,
        'currency': product.currency_id.symbol,
        'image_url': get_product_image_url(product),
        'category': {
            'id': product.categ_id.id,
            'name': product.categ_id.name,
        } if product.categ_id else None,
        'is_published': product.is_published,
        'qty_available': qty_available,
        'stock_status': stock_status,
        'is_service': is_service,
    }

    # Add seller info for marketplace products
    if hasattr(product, 'marketplace_seller_id') and product.marketplace_seller_id:
        data['seller'] = {
            'id': product.marketplace_seller_id.id,
            'name': product.marketplace_seller_id.name,
        }

    if include_details:
        data.update({
            'description': product.description_sale or '',
            'short_description': product.description or '',
            'weight': product.weight,
            'uom': product.uom_id.name if product.uom_id else None,
            'images': [],
        })

        # Add extra images
        if hasattr(product, 'product_template_image_ids'):
            for img in product.product_template_image_ids:
                data['images'].append({
                    'id': img.id,
                    'url': f"{base_url}/web/image/product.image/{img.id}/image_256",
                })

    return data


def format_order_line(line):
    """Format sale order line for API response"""
    return {
        'id': line.id,
        'product': {
            'id': line.product_id.id,
            'name': line.product_id.name,
            'image_url': get_product_image_url(line.product_id.product_tmpl_id),
        },
        'quantity': line.product_uom_qty,
        'price_unit': line.price_unit,
        'subtotal': line.price_subtotal,
        'tax': line.price_tax,
        'total': line.price_total,
    }


def format_order(order, include_lines=True):
    """Format sale order for API response"""
    data = {
        'id': order.id,
        'name': order.name,
        'date': order.date_order.isoformat() if order.date_order else None,
        'state': order.state,
        'state_display': dict(order._fields['state'].selection).get(order.state, ''),
        'subtotal': order.amount_untaxed,
        'tax': order.amount_tax,
        'total': order.amount_total,
        'currency': order.currency_id.symbol,
        'item_count': len(order.order_line),
    }

    if include_lines:
        data['lines'] = [format_order_line(line) for line in order.order_line]

    return data


class LineBuyerApiController(http.Controller):
    """Base controller for LINE Marketplace API"""

    @http.route('/api/line-buyer/health', type='http', auth='none', methods=['GET'], csrf=False)
    def health_check(self):
        """Health check endpoint"""
        return success_response({
            'status': 'ok',
            'module': 'core_line_integration',
            'version': '18.0.1.0.0',
        })

    @http.route('/api/line-buyer/config', type='http', auth='none', methods=['GET'], csrf=False)
    def get_config(self):
        """Get public configuration for client app"""
        channels = request.env['line.channel'].sudo().search([('active', '=', True)])

        return success_response({
            'channels': [{
                'code': ch.code,
                'name': ch.name,
                'liff_url': ch.liff_url,
            } for ch in channels],
            'mock_auth': request.env['ir.config_parameter'].sudo().get_param(
                'core_line_integration.mock_auth', 'True'
            ) == 'True',
        })
