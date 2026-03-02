# -*- coding: utf-8 -*-
"""
Buyer-facing Endorsement API - browse endorsed products and ambassador profiles
Protected by require_auth decorator
"""
import logging

from odoo import http
from odoo.http import request

from odoo.addons.core_line_integration.controllers.main import (
    success_response, error_response, require_auth, format_product, get_product_image_url
)
from .ambassador_main import format_ambassador, format_endorsement

_logger = logging.getLogger(__name__)


class BuyerEndorsementsController(http.Controller):
    """Buyer-facing endorsement browsing API"""

    @http.route('/api/line-buyer/endorsed-products', type='http', auth='none',
                methods=['GET', 'OPTIONS'], csrf=False)
    @require_auth
    def list_endorsed_products(self, **kwargs):
        """List products with active endorsements."""
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            page = int(kwargs.get('page', 1))
            limit = min(int(kwargs.get('limit', 20)), 50)
            offset = (page - 1) * limit
            search = kwargs.get('search', '')
            ambassador_id = kwargs.get('ambassador_id', '')
            specialty = kwargs.get('specialty', '')

            domain = [('state', '=', 'active')]
            if ambassador_id:
                domain.append(('ambassador_id', '=', int(ambassador_id)))
            if specialty:
                domain.append(('ambassador_id.ambassador_specialty_ids.code', '=', specialty))

            Endorsement = request.env['product.endorsement'].sudo()
            total = Endorsement.search_count(domain)
            endorsements = Endorsement.search(domain, limit=limit, offset=offset,
                                              order='create_date desc')

            items = []
            for e in endorsements:
                product = e.product_id
                if search and search.lower() not in (product.name or '').lower():
                    continue
                item = format_endorsement(e)
                item['product'].update({
                    'currency': product.currency_id.symbol or '฿',
                    'is_published': product.is_published,
                })
                items.append(item)

            return success_response({
                'items': items,
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': total,
                    'pages': (total + limit - 1) // limit,
                },
            })

        except Exception as e:
            _logger.error(f'Error listing endorsed products: {str(e)}')
            return error_response(str(e), 500)

    @http.route('/api/line-buyer/products/<int:product_id>/endorsement', type='http',
                auth='none', methods=['GET', 'OPTIONS'], csrf=False)
    @require_auth
    def get_product_endorsement(self, product_id, **kwargs):
        """Get endorsements for a specific product."""
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            endorsements = request.env['product.endorsement'].sudo().search([
                ('product_id', '=', product_id),
                ('state', '=', 'active'),
            ], order='create_date desc')

            if not endorsements:
                return success_response({
                    'has_endorsement': False,
                    'endorsements': [],
                })

            return success_response({
                'has_endorsement': True,
                'endorsements': [format_endorsement(e) for e in endorsements],
            })

        except Exception as e:
            _logger.error(f'Error getting product endorsement: {str(e)}')
            return error_response(str(e), 500)

    @http.route('/api/line-buyer/ambassadors', type='http', auth='none',
                methods=['GET', 'OPTIONS'], csrf=False)
    @require_auth
    def list_ambassadors(self, **kwargs):
        """Browse ambassador profiles (public)."""
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            page = int(kwargs.get('page', 1))
            limit = min(int(kwargs.get('limit', 20)), 50)
            offset = (page - 1) * limit
            search = kwargs.get('search', '')
            specialty = kwargs.get('specialty', '')

            domain = [
                ('is_ambassador', '=', True),
                ('ambassador_state', '=', 'approved'),
            ]
            if search:
                domain.append(('name', 'ilike', search))
            if specialty:
                domain.append(('ambassador_specialty_ids.code', '=', specialty))

            Partner = request.env['res.partner'].sudo()
            total = Partner.search_count(domain)
            ambassadors = Partner.search(domain, limit=limit, offset=offset,
                                         order='endorsement_count desc, name')

            return success_response({
                'items': [format_ambassador(a) for a in ambassadors],
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': total,
                    'pages': (total + limit - 1) // limit,
                },
            })

        except Exception as e:
            _logger.error(f'Error listing ambassadors: {str(e)}')
            return error_response(str(e), 500)

    @http.route('/api/line-buyer/ambassadors/<int:ambassador_id>', type='http',
                auth='none', methods=['GET', 'OPTIONS'], csrf=False)
    @require_auth
    def get_ambassador(self, ambassador_id, **kwargs):
        """Get ambassador profile with endorsed products."""
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            partner = request.env['res.partner'].sudo().browse(ambassador_id)
            if not partner.exists() or not partner.is_ambassador:
                return error_response('Ambassador not found', 404, 'NOT_FOUND')
            if partner.ambassador_state != 'approved':
                return error_response('Ambassador is not active', 400, 'NOT_ACTIVE')

            data = format_ambassador(partner)

            # Include endorsed products
            endorsements = request.env['product.endorsement'].sudo().search([
                ('ambassador_id', '=', partner.id),
                ('state', '=', 'active'),
            ], order='create_date desc', limit=20)
            data['endorsed_products'] = [format_endorsement(e) for e in endorsements]

            return success_response(data)

        except Exception as e:
            _logger.error(f'Error getting ambassador: {str(e)}')
            return error_response(str(e), 500)
