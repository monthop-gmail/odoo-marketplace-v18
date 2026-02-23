# -*- coding: utf-8 -*-
"""
LIFF App Controller - serves the LINE LIFF frontend
"""
from odoo import http
from odoo.http import request

from .main import success_response, error_response


class LiffController(http.Controller):
    """
    Controller for serving LIFF app

    The LIFF app is a static HTML/CSS/JS application that runs inside LINE.
    This controller provides convenient routes and handles any server-side
    requirements.
    """

    @http.route('/line-buyer', type='http', auth='public', website=True)
    def liff_app(self, **kwargs):
        """
        Serve the LIFF app

        URL: /line-buyer

        This route redirects to the static LIFF index.html
        Can also be used as the LIFF endpoint URL
        """
        return request.redirect('/core_line_integration/static/liff/index.html')

    @http.route('/line-buyer/app', type='http', auth='public', website=True)
    def liff_app_direct(self, **kwargs):
        """
        Alternative route for LIFF app
        """
        return request.redirect('/core_line_integration/static/liff/index.html')

    @http.route('/line-buyer/product/<int:product_id>', type='http', auth='public', website=True)
    def liff_product(self, product_id, **kwargs):
        """
        Deep link to product detail

        URL: /line-buyer/product/<product_id>

        Redirects to LIFF app with product parameter
        """
        return request.redirect(f'/core_line_integration/static/liff/index.html?page=products&product={product_id}')

    @http.route('/line-buyer/order/<int:order_id>', type='http', auth='public', website=True)
    def liff_order(self, order_id, **kwargs):
        """
        Deep link to order detail

        URL: /line-buyer/order/<order_id>

        Redirects to LIFF app with order parameter
        """
        return request.redirect(f'/core_line_integration/static/liff/index.html?page=orders&order={order_id}')

    @http.route('/line-buyer/cart', type='http', auth='public', website=True)
    def liff_cart(self, **kwargs):
        """
        Deep link to cart

        URL: /line-buyer/cart
        """
        return request.redirect('/core_line_integration/static/liff/index.html?page=cart')

    # ========== Multi-Channel LIFF Routes ==========

    @http.route(['/line-buyer/<string:liff_type>', '/line/liff/<string:liff_type>'], type='http', auth='public', website=True)
    def liff_by_type(self, liff_type, **kwargs):
        """
        Route to LIFF by type with channel code

        URL: /line-buyer/support?channel=coop_a
        URL: /line-buyer/promotion?channel=coop_b

        Redirects to the appropriate static LIFF folder
        """
        liff_types = {
            'buyer': '/core_line_integration/static/liff/index.html',
            'seller': '/core_line_integration/static/liff_seller/index.html',
            'admin': '/core_line_integration/static/liff_admin/index.html',
            'promotion': '/core_line_integration/static/liff_promotion/index.html',
            'support': '/core_line_integration/static/liff_support/index.html',
        }

        if liff_type in liff_types:
            url = liff_types[liff_type]
            # Pass through any query parameters
            if kwargs:
                params = '&'.join(f'{k}={v}' for k, v in kwargs.items())
                url = f'{url}?{params}'
            return request.redirect(url)

        return request.redirect('/core_line_integration/static/liff/index.html')

    # ========== LIFF Configuration API ==========

    @http.route('/api/line-buyer/liff/config', type='http', auth='none',
                methods=['GET', 'OPTIONS'], csrf=False)
    def get_liff_config(self, **kwargs):
        """
        Get channel configuration from LIFF ID

        Query params:
        - liff_id: The LIFF ID from liff.getContext()

        Returns channel info for the LIFF to use
        """
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            liff_id = kwargs.get('liff_id')

            if not liff_id:
                return error_response('liff_id is required', 400)

            # Find LIFF record
            liff = request.env['line.liff'].sudo().search([
                ('liff_id', '=', liff_id),
                ('active', '=', True),
            ], limit=1)

            if not liff:
                return error_response('LIFF not found', 404, 'LIFF_NOT_FOUND')

            channel = liff.channel_id
            base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')

            # Get all LIFFs for this channel (for navigation)
            channel_liffs = {}
            for l in channel.liff_ids.filtered(lambda x: x.active):
                channel_liffs[l.liff_type] = {
                    'liff_id': l.liff_id,
                    'liff_url': l.liff_url,
                    'name': l.name,
                }

            return success_response({
                'channel': {
                    'id': channel.id,
                    'code': channel.code,
                    'name': channel.name,
                },
                'liff': {
                    'id': liff.id,
                    'liff_id': liff.liff_id,
                    'type': liff.liff_type,
                    'name': liff.name,
                },
                'liffs': channel_liffs,
                'api_base': base_url,
                'mock_auth': request.env['ir.config_parameter'].sudo().get_param(
                    'core_line_integration.mock_auth', 'True'
                ) == 'True',
            })

        except Exception as e:
            return error_response(str(e), 500)

    @http.route('/api/line-buyer/channel/<string:channel_code>/liffs', type='http', auth='none',
                methods=['GET', 'OPTIONS'], csrf=False)
    def get_channel_liffs(self, channel_code, **kwargs):
        """
        Get all LIFF apps for a channel

        Returns list of LIFFs with their URLs for Rich Menu configuration
        """
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            channel = request.env['line.channel'].sudo().search([
                ('code', '=', channel_code),
                ('active', '=', True),
            ], limit=1)

            if not channel:
                return error_response('Channel not found', 404, 'CHANNEL_NOT_FOUND')

            liffs = []
            for liff in channel.liff_ids.filtered(lambda x: x.active):
                liffs.append({
                    'id': liff.id,
                    'liff_id': liff.liff_id,
                    'type': liff.liff_type,
                    'name': liff.name,
                    'liff_url': liff.liff_url,
                    'size': liff.liff_size,
                    'is_default': liff.is_default,
                })

            return success_response({
                'channel': {
                    'id': channel.id,
                    'code': channel.code,
                    'name': channel.name,
                },
                'liffs': liffs,
            })

        except Exception as e:
            return error_response(str(e), 500)
