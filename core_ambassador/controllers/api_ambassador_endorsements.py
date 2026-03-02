# -*- coding: utf-8 -*-
"""
Ambassador Endorsement Management API
Protected by require_ambassador decorator
"""
import json
import logging

from odoo import http, SUPERUSER_ID
from odoo.http import request

from odoo.addons.core_line_integration.controllers.main import (
    success_response, error_response
)
from .ambassador_main import (
    require_ambassador, format_ambassador, format_endorsement, format_endorsement_request
)

_logger = logging.getLogger(__name__)


class AmbassadorEndorsementsController(http.Controller):
    """Ambassador's endorsement management API"""

    # ==================== Endorsements ====================

    @http.route('/api/line-ambassador/endorsements', type='http', auth='none',
                methods=['GET', 'OPTIONS'], csrf=False)
    @require_ambassador
    def list_endorsements(self, **kwargs):
        """List ambassador's endorsements."""
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            page = int(kwargs.get('page', 1))
            limit = min(int(kwargs.get('limit', 20)), 50)
            offset = (page - 1) * limit
            state = kwargs.get('state', 'active')

            domain = [('ambassador_id', '=', request.ambassador_partner.id)]
            if state and state != 'all':
                domain.append(('state', '=', state))

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

    @http.route('/api/line-ambassador/endorsements/<int:endorsement_id>', type='http',
                auth='none', methods=['GET', 'OPTIONS'], csrf=False)
    @require_ambassador
    def get_endorsement(self, endorsement_id, **kwargs):
        """Get endorsement detail."""
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            endorsement = request.env['product.endorsement'].sudo().browse(endorsement_id)
            if not endorsement.exists():
                return error_response('Endorsement not found', 404, 'NOT_FOUND')
            if endorsement.ambassador_id.id != request.ambassador_partner.id:
                return error_response('Unauthorized', 403, 'UNAUTHORIZED')

            return success_response(format_endorsement(endorsement))

        except Exception as e:
            _logger.error(f'Error getting endorsement: {str(e)}')
            return error_response(str(e), 500)

    @http.route('/api/line-ambassador/endorsements/<int:endorsement_id>', type='http',
                auth='none', methods=['PUT', 'OPTIONS'], csrf=False)
    @require_ambassador
    def update_endorsement(self, endorsement_id, **kwargs):
        """
        Update endorsement content.

        JSON body:
        - endorsement_text
        - endorsement_video_url
        - rating (0-5)
        """
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            endorsement = request.env['product.endorsement'].with_user(SUPERUSER_ID).browse(endorsement_id)
            if not endorsement.exists():
                return error_response('Endorsement not found', 404, 'NOT_FOUND')
            if endorsement.ambassador_id.id != request.ambassador_partner.id:
                return error_response('Unauthorized', 403, 'UNAUTHORIZED')
            if endorsement.state != 'active':
                return error_response('Can only update active endorsements', 400, 'INVALID_STATE')

            body = json.loads(request.httprequest.data or '{}')
            vals = {}
            if 'endorsement_text' in body:
                vals['endorsement_text'] = body['endorsement_text']
            if 'endorsement_video_url' in body:
                vals['endorsement_video_url'] = body['endorsement_video_url']
            if 'rating' in body:
                rating = float(body['rating'])
                if rating < 0 or rating > 5:
                    return error_response('Rating must be 0-5', 400, 'VALIDATION_ERROR')
                vals['rating'] = rating

            if vals:
                endorsement.write(vals)

            return success_response(format_endorsement(endorsement),
                                    message='อัปเดตการรับรองสำเร็จ')

        except json.JSONDecodeError:
            return error_response('Invalid JSON body', 400, 'INVALID_JSON')
        except Exception as e:
            _logger.error(f'Error updating endorsement: {str(e)}')
            return error_response(str(e), 500)

    # ==================== Requests ====================

    @http.route('/api/line-ambassador/requests', type='http', auth='none',
                methods=['GET', 'OPTIONS'], csrf=False)
    @require_ambassador
    def list_requests(self, **kwargs):
        """List endorsement requests to this ambassador."""
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            page = int(kwargs.get('page', 1))
            limit = min(int(kwargs.get('limit', 20)), 50)
            offset = (page - 1) * limit
            state = kwargs.get('state', 'pending')

            domain = [('ambassador_id', '=', request.ambassador_partner.id)]
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

    @http.route('/api/line-ambassador/requests/<int:request_id>', type='http',
                auth='none', methods=['GET', 'OPTIONS'], csrf=False)
    @require_ambassador
    def get_request(self, request_id, **kwargs):
        """Get endorsement request detail."""
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            req = request.env['endorsement.request'].sudo().browse(request_id)
            if not req.exists():
                return error_response('Request not found', 404, 'NOT_FOUND')
            if req.ambassador_id.id != request.ambassador_partner.id:
                return error_response('Unauthorized', 403, 'UNAUTHORIZED')

            return success_response(format_endorsement_request(req))

        except Exception as e:
            _logger.error(f'Error getting request: {str(e)}')
            return error_response(str(e), 500)

    @http.route('/api/line-ambassador/requests/<int:request_id>/approve', type='http',
                auth='none', methods=['POST', 'OPTIONS'], csrf=False)
    @require_ambassador
    def approve_request(self, request_id, **kwargs):
        """
        Approve endorsement request.

        JSON body (optional):
        - response_message: ambassador's response text
        - endorsement_text: endorsement review text
        - endorsement_video_url: review video URL
        - rating: 0-5
        """
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            req = request.env['endorsement.request'].with_user(SUPERUSER_ID).browse(request_id)
            if not req.exists():
                return error_response('Request not found', 404, 'NOT_FOUND')
            if req.ambassador_id.id != request.ambassador_partner.id:
                return error_response('Unauthorized', 403, 'UNAUTHORIZED')
            if req.state != 'pending':
                return error_response('Only pending requests can be approved', 400, 'INVALID_STATE')

            body = json.loads(request.httprequest.data or '{}')

            if body.get('response_message'):
                req.response_message = body['response_message']

            req.action_approve()

            # Update endorsement with extra content
            if req.endorsement_id:
                vals = {}
                if body.get('endorsement_text'):
                    vals['endorsement_text'] = body['endorsement_text']
                if body.get('endorsement_video_url'):
                    vals['endorsement_video_url'] = body['endorsement_video_url']
                if body.get('rating'):
                    vals['rating'] = min(max(float(body['rating']), 0), 5)
                if vals:
                    req.endorsement_id.write(vals)

            return success_response(
                format_endorsement_request(req),
                message='อนุมัติการรับรองสินค้าสำเร็จ'
            )

        except json.JSONDecodeError:
            return error_response('Invalid JSON body', 400, 'INVALID_JSON')
        except Exception as e:
            _logger.error(f'Error approving request: {str(e)}')
            return error_response(str(e), 500)

    @http.route('/api/line-ambassador/requests/<int:request_id>/reject', type='http',
                auth='none', methods=['POST', 'OPTIONS'], csrf=False)
    @require_ambassador
    def reject_request(self, request_id, **kwargs):
        """
        Reject endorsement request.

        JSON body (optional):
        - response_message: reason for rejection
        """
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            req = request.env['endorsement.request'].with_user(SUPERUSER_ID).browse(request_id)
            if not req.exists():
                return error_response('Request not found', 404, 'NOT_FOUND')
            if req.ambassador_id.id != request.ambassador_partner.id:
                return error_response('Unauthorized', 403, 'UNAUTHORIZED')
            if req.state != 'pending':
                return error_response('Only pending requests can be rejected', 400, 'INVALID_STATE')

            body = json.loads(request.httprequest.data or '{}')
            if body.get('response_message'):
                req.response_message = body['response_message']

            req.action_reject()

            return success_response(
                format_endorsement_request(req),
                message='ปฏิเสธคำขอรับรองสินค้า'
            )

        except json.JSONDecodeError:
            return error_response('Invalid JSON body', 400, 'INVALID_JSON')
        except Exception as e:
            _logger.error(f'Error rejecting request: {str(e)}')
            return error_response(str(e), 500)

    # ==================== Dashboard ====================

    @http.route('/api/line-ambassador/dashboard', type='http', auth='none',
                methods=['GET', 'OPTIONS'], csrf=False)
    @require_ambassador
    def get_dashboard(self, **kwargs):
        """Get ambassador dashboard stats."""
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            partner = request.ambassador_partner
            Endorsement = request.env['product.endorsement'].sudo()
            Request = request.env['endorsement.request'].sudo()

            active_endorsements = Endorsement.search_count([
                ('ambassador_id', '=', partner.id),
                ('state', '=', 'active'),
            ])
            pending_requests = Request.search_count([
                ('ambassador_id', '=', partner.id),
                ('state', '=', 'pending'),
            ])
            total_endorsements = Endorsement.search_count([
                ('ambassador_id', '=', partner.id),
            ])

            return success_response({
                'ambassador': {
                    'name': partner.name,
                    'tier': partner.ambassador_tier,
                    'commission_rate': partner.ambassador_commission_rate,
                },
                'stats': {
                    'active_endorsements': active_endorsements,
                    'total_endorsements': total_endorsements,
                    'pending_requests': pending_requests,
                },
            })

        except Exception as e:
            _logger.error(f'Error getting dashboard: {str(e)}')
            return error_response(str(e), 500)
