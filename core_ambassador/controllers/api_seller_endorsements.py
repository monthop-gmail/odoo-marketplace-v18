# -*- coding: utf-8 -*-
"""
Seller Endorsement API - sellers request endorsement from ambassadors
Protected by require_seller decorator from core_line_integration
"""
import json
import logging

from odoo import http, SUPERUSER_ID
from odoo.http import request

from odoo.addons.core_line_integration.controllers.main import (
    success_response, error_response, get_product_image_url
)
from odoo.addons.core_line_integration.controllers.seller_main import require_seller
from .ambassador_main import format_ambassador, format_endorsement, format_endorsement_request

_logger = logging.getLogger(__name__)


class SellerEndorsementsController(http.Controller):
    """Seller's endorsement management API"""

    # ==================== Endorsements on Seller's Products ====================

    @http.route('/api/line-seller/endorsements', type='http', auth='none',
                methods=['GET', 'OPTIONS'], csrf=False)
    @require_seller
    def list_endorsements(self, **kwargs):
        """List endorsements on seller's products."""
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            page = int(kwargs.get('page', 1))
            limit = min(int(kwargs.get('limit', 20)), 50)
            offset = (page - 1) * limit

            domain = [
                ('seller_id', '=', request.seller_partner.id),
                ('state', '=', 'active'),
            ]

            Endorsement = request.env['product.endorsement'].sudo()
            total = Endorsement.search_count(domain)
            endorsements = Endorsement.search(domain, limit=limit, offset=offset,
                                              order='create_date desc')

            return success_response({
                'items': [format_endorsement(e) for e in endorsements],
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': total,
                    'pages': (total + limit - 1) // limit,
                },
            })

        except Exception as e:
            _logger.error(f'Error listing endorsements: {str(e)}')
            return error_response(str(e), 500)

    # ==================== Request Endorsement ====================

    @http.route('/api/line-seller/endorsements/request', type='http', auth='none',
                methods=['POST', 'OPTIONS'], csrf=False)
    @require_seller
    def request_endorsement(self, **kwargs):
        """
        Request endorsement from an ambassador.

        JSON body:
        - ambassador_id (required)
        - product_id (required)
        - message (optional)
        """
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            body = json.loads(request.httprequest.data or '{}')

            ambassador_id = body.get('ambassador_id')
            product_id = body.get('product_id')

            if not ambassador_id or not product_id:
                return error_response(
                    'กรุณาระบุ ambassador_id และ product_id',
                    400, 'VALIDATION_ERROR'
                )

            sudo = lambda model: request.env[model].with_user(SUPERUSER_ID)

            # Validate ambassador
            ambassador = sudo('res.partner').browse(ambassador_id)
            if not ambassador.exists() or not ambassador.is_ambassador:
                return error_response('Ambassador not found', 404, 'AMBASSADOR_NOT_FOUND')
            if ambassador.ambassador_state != 'approved':
                return error_response('Ambassador is not active', 400, 'AMBASSADOR_NOT_ACTIVE')

            # Validate product belongs to seller
            product = sudo('product.template').browse(product_id)
            if not product.exists():
                return error_response('Product not found', 404, 'PRODUCT_NOT_FOUND')
            if product.marketplace_seller_id.id != request.seller_partner.id:
                return error_response('Not your product', 403, 'NOT_YOUR_PRODUCT')

            # Check existing active endorsement
            existing_endorsement = sudo('product.endorsement').search([
                ('ambassador_id', '=', ambassador_id),
                ('product_id', '=', product_id),
                ('state', '=', 'active'),
            ], limit=1)
            if existing_endorsement:
                return error_response(
                    'สินค้านี้ได้รับการรับรองจาก Ambassador นี้แล้ว',
                    400, 'ALREADY_ENDORSED'
                )

            # Check existing pending request
            existing_request = sudo('endorsement.request').search([
                ('seller_id', '=', request.seller_partner.id),
                ('ambassador_id', '=', ambassador_id),
                ('product_id', '=', product_id),
                ('state', 'in', ('draft', 'pending')),
            ], limit=1)
            if existing_request:
                return error_response(
                    'มีคำขอรับรองสินค้านี้อยู่แล้ว',
                    400, 'REQUEST_EXISTS'
                )

            # Create and submit request
            req = sudo('endorsement.request').create({
                'seller_id': request.seller_partner.id,
                'ambassador_id': ambassador_id,
                'product_id': product_id,
                'message': body.get('message', ''),
            })
            req.action_submit()

            return success_response(
                format_endorsement_request(req),
                message='ส่งคำขอรับรองสินค้าสำเร็จ'
            )

        except json.JSONDecodeError:
            return error_response('Invalid JSON body', 400, 'INVALID_JSON')
        except Exception as e:
            _logger.error(f'Error requesting endorsement: {str(e)}')
            return error_response(str(e), 500)

    # ==================== Seller's Outgoing Requests ====================

    @http.route('/api/line-seller/endorsements/requests', type='http', auth='none',
                methods=['GET', 'OPTIONS'], csrf=False)
    @require_seller
    def list_requests(self, **kwargs):
        """List seller's outgoing endorsement requests."""
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            page = int(kwargs.get('page', 1))
            limit = min(int(kwargs.get('limit', 20)), 50)
            offset = (page - 1) * limit
            state = kwargs.get('state', 'all')

            domain = [('seller_id', '=', request.seller_partner.id)]
            if state and state != 'all':
                domain.append(('state', '=', state))

            Request = request.env['endorsement.request'].sudo()
            total = Request.search_count(domain)
            requests_list = Request.search(domain, limit=limit, offset=offset,
                                           order='create_date desc')

            return success_response({
                'items': [format_endorsement_request(r) for r in requests_list],
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': total,
                    'pages': (total + limit - 1) // limit,
                },
            })

        except Exception as e:
            _logger.error(f'Error listing requests: {str(e)}')
            return error_response(str(e), 500)

    @http.route('/api/line-seller/endorsements/requests/<int:request_id>', type='http',
                auth='none', methods=['DELETE', 'OPTIONS'], csrf=False)
    @require_seller
    def cancel_request(self, request_id, **kwargs):
        """Cancel a pending endorsement request."""
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            req = request.env['endorsement.request'].with_user(SUPERUSER_ID).browse(request_id)
            if not req.exists():
                return error_response('Request not found', 404, 'NOT_FOUND')
            if req.seller_id.id != request.seller_partner.id:
                return error_response('Unauthorized', 403, 'UNAUTHORIZED')
            if req.state not in ('draft', 'pending'):
                return error_response('Can only cancel draft or pending requests', 400, 'INVALID_STATE')

            req.action_cancel()

            return success_response(
                format_endorsement_request(req),
                message='ยกเลิกคำขอรับรองสำเร็จ'
            )

        except Exception as e:
            _logger.error(f'Error cancelling request: {str(e)}')
            return error_response(str(e), 500)

    # ==================== Browse Ambassadors ====================

    @http.route('/api/line-seller/ambassadors', type='http', auth='none',
                methods=['GET', 'OPTIONS'], csrf=False)
    @require_seller
    def list_ambassadors(self, **kwargs):
        """Browse available ambassadors."""
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

    @http.route('/api/line-seller/ambassadors/<int:ambassador_id>', type='http',
                auth='none', methods=['GET', 'OPTIONS'], csrf=False)
    @require_seller
    def get_ambassador(self, ambassador_id, **kwargs):
        """Get ambassador profile detail."""
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            partner = request.env['res.partner'].sudo().browse(ambassador_id)
            if not partner.exists() or not partner.is_ambassador:
                return error_response('Ambassador not found', 404, 'NOT_FOUND')
            if partner.ambassador_state != 'approved':
                return error_response('Ambassador is not active', 400, 'NOT_ACTIVE')

            data = format_ambassador(partner)

            # Include recent endorsements
            endorsements = request.env['product.endorsement'].sudo().search([
                ('ambassador_id', '=', partner.id),
                ('state', '=', 'active'),
            ], limit=10, order='create_date desc')
            data['recent_endorsements'] = [format_endorsement(e) for e in endorsements]

            return success_response(data)

        except Exception as e:
            _logger.error(f'Error getting ambassador: {str(e)}')
            return error_response(str(e), 500)
