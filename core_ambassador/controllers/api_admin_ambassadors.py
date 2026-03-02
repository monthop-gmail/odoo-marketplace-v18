# -*- coding: utf-8 -*-
"""
Admin Ambassador Management API
Protected by require_admin decorator from core_line_integration
"""
import json
import logging

from odoo import http, SUPERUSER_ID
from odoo.http import request

from odoo.addons.core_line_integration.controllers.main import (
    success_response, error_response
)
from odoo.addons.core_line_integration.controllers.admin_main import require_admin
from .ambassador_main import format_ambassador, format_endorsement, format_endorsement_request

_logger = logging.getLogger(__name__)


class AdminAmbassadorsController(http.Controller):
    """Admin ambassador management API"""

    # ==================== Ambassadors ====================

    @http.route('/api/line-admin/ambassadors', type='http', auth='none',
                methods=['GET', 'OPTIONS'], csrf=False)
    @require_admin
    def list_ambassadors(self, **kwargs):
        """List all ambassadors with filters."""
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            page = int(kwargs.get('page', 1))
            limit = min(int(kwargs.get('limit', 20)), 50)
            offset = (page - 1) * limit
            state = kwargs.get('state', 'all')
            search = kwargs.get('search', '')
            tier = kwargs.get('tier', '')

            domain = [('is_ambassador', '=', True)]
            if state and state != 'all':
                domain.append(('ambassador_state', '=', state))
            if search:
                domain.append(('name', 'ilike', search))
            if tier:
                domain.append(('ambassador_tier', '=', tier))

            Partner = request.env['res.partner'].sudo()
            total = Partner.search_count(domain)
            ambassadors = Partner.search(domain, limit=limit, offset=offset,
                                         order='ambassador_approved_date desc, name')

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

    @http.route('/api/line-admin/ambassadors/<int:ambassador_id>', type='http',
                auth='none', methods=['GET', 'OPTIONS'], csrf=False)
    @require_admin
    def get_ambassador(self, ambassador_id, **kwargs):
        """Get ambassador detail."""
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            partner = request.env['res.partner'].sudo().browse(ambassador_id)
            if not partner.exists() or not partner.is_ambassador:
                return error_response('Ambassador not found', 404, 'NOT_FOUND')

            data = format_ambassador(partner)
            data['state'] = partner.ambassador_state

            # Application info
            if partner.ambassador_application_id:
                app = partner.ambassador_application_id
                data['application'] = {
                    'id': app.id,
                    'name': app.name,
                    'state': app.state,
                    'submitted_date': app.submitted_date.isoformat() if app.submitted_date else None,
                }

            # Endorsement stats
            Endorsement = request.env['product.endorsement'].sudo()
            data['endorsement_stats'] = {
                'active': Endorsement.search_count([
                    ('ambassador_id', '=', partner.id), ('state', '=', 'active')]),
                'revoked': Endorsement.search_count([
                    ('ambassador_id', '=', partner.id), ('state', '=', 'revoked')]),
                'total': Endorsement.search_count([
                    ('ambassador_id', '=', partner.id)]),
            }

            return success_response(data)

        except Exception as e:
            _logger.error(f'Error getting ambassador: {str(e)}')
            return error_response(str(e), 500)

    @http.route('/api/line-admin/ambassadors/<int:ambassador_id>/approve', type='http',
                auth='none', methods=['POST', 'OPTIONS'], csrf=False)
    @require_admin
    def approve_ambassador(self, ambassador_id, **kwargs):
        """Approve a pending ambassador."""
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            partner = request.env['res.partner'].with_user(SUPERUSER_ID).browse(ambassador_id)
            if not partner.exists() or not partner.is_ambassador:
                return error_response('Ambassador not found', 404, 'NOT_FOUND')

            body = json.loads(request.httprequest.data or '{}')
            if body.get('tier'):
                partner.ambassador_tier = body['tier']

            partner.action_ambassador_approve()

            return success_response(
                format_ambassador(partner),
                message='อนุมัติ Ambassador สำเร็จ'
            )

        except Exception as e:
            _logger.error(f'Error approving ambassador: {str(e)}')
            return error_response(str(e), 500)

    @http.route('/api/line-admin/ambassadors/<int:ambassador_id>/reject', type='http',
                auth='none', methods=['POST', 'OPTIONS'], csrf=False)
    @require_admin
    def reject_ambassador(self, ambassador_id, **kwargs):
        """Reject a pending ambassador."""
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            partner = request.env['res.partner'].with_user(SUPERUSER_ID).browse(ambassador_id)
            if not partner.exists() or not partner.is_ambassador:
                return error_response('Ambassador not found', 404, 'NOT_FOUND')

            partner.action_ambassador_reject()

            return success_response(
                format_ambassador(partner),
                message='ปฏิเสธ Ambassador'
            )

        except Exception as e:
            _logger.error(f'Error rejecting ambassador: {str(e)}')
            return error_response(str(e), 500)

    @http.route('/api/line-admin/ambassadors/<int:ambassador_id>/suspend', type='http',
                auth='none', methods=['POST', 'OPTIONS'], csrf=False)
    @require_admin
    def suspend_ambassador(self, ambassador_id, **kwargs):
        """Suspend an approved ambassador."""
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            partner = request.env['res.partner'].with_user(SUPERUSER_ID).browse(ambassador_id)
            if not partner.exists() or not partner.is_ambassador:
                return error_response('Ambassador not found', 404, 'NOT_FOUND')

            partner.action_ambassador_suspend()

            return success_response(
                format_ambassador(partner),
                message='ระงับ Ambassador'
            )

        except Exception as e:
            _logger.error(f'Error suspending ambassador: {str(e)}')
            return error_response(str(e), 500)

    @http.route('/api/line-admin/ambassadors/<int:ambassador_id>/tier', type='http',
                auth='none', methods=['PUT', 'OPTIONS'], csrf=False)
    @require_admin
    def update_tier(self, ambassador_id, **kwargs):
        """
        Change ambassador tier.

        JSON body:
        - tier: bronze/silver/gold
        """
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            body = json.loads(request.httprequest.data or '{}')
            tier = body.get('tier')
            if tier not in ('bronze', 'silver', 'gold'):
                return error_response('Invalid tier', 400, 'VALIDATION_ERROR')

            tier_rates = {'bronze': 5.0, 'silver': 7.0, 'gold': 10.0}

            partner = request.env['res.partner'].with_user(SUPERUSER_ID).browse(ambassador_id)
            if not partner.exists() or not partner.is_ambassador:
                return error_response('Ambassador not found', 404, 'NOT_FOUND')

            partner.write({
                'ambassador_tier': tier,
                'ambassador_commission_rate': tier_rates[tier],
            })

            return success_response(
                format_ambassador(partner),
                message=f'เปลี่ยน tier เป็น {tier} สำเร็จ'
            )

        except json.JSONDecodeError:
            return error_response('Invalid JSON body', 400, 'INVALID_JSON')
        except Exception as e:
            _logger.error(f'Error updating tier: {str(e)}')
            return error_response(str(e), 500)

    # ==================== Applications ====================

    @http.route('/api/line-admin/ambassador-applications', type='http', auth='none',
                methods=['GET', 'OPTIONS'], csrf=False)
    @require_admin
    def list_applications(self, **kwargs):
        """List ambassador applications."""
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            page = int(kwargs.get('page', 1))
            limit = min(int(kwargs.get('limit', 20)), 50)
            offset = (page - 1) * limit
            state = kwargs.get('state', 'submitted')

            domain = []
            if state and state != 'all':
                domain.append(('state', '=', state))

            Application = request.env['ambassador.application'].sudo()
            total = Application.search_count(domain)
            apps = Application.search(domain, limit=limit, offset=offset,
                                      order='create_date desc')

            return success_response({
                'items': [{
                    'id': app.id,
                    'name': app.name,
                    'full_name': app.full_name,
                    'partner_id': app.partner_id.id,
                    'partner_name': app.partner_id.name,
                    'state': app.state,
                    'requested_tier': app.requested_tier,
                    'specialty_ids': [{'id': s.id, 'name': s.name} for s in app.specialty_ids],
                    'submitted_date': app.submitted_date.isoformat() if app.submitted_date else None,
                    'bio': app.bio or '',
                } for app in apps],
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': total,
                    'pages': (total + limit - 1) // limit,
                },
            })

        except Exception as e:
            _logger.error(f'Error listing applications: {str(e)}')
            return error_response(str(e), 500)

    # ==================== Endorsements (Platform-wide) ====================

    @http.route('/api/line-admin/endorsements', type='http', auth='none',
                methods=['GET', 'OPTIONS'], csrf=False)
    @require_admin
    def list_endorsements(self, **kwargs):
        """List all endorsements (platform-wide)."""
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            page = int(kwargs.get('page', 1))
            limit = min(int(kwargs.get('limit', 20)), 50)
            offset = (page - 1) * limit
            state = kwargs.get('state', 'all')

            domain = []
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

    @http.route('/api/line-admin/endorsements/<int:endorsement_id>/revoke', type='http',
                auth='none', methods=['POST', 'OPTIONS'], csrf=False)
    @require_admin
    def revoke_endorsement(self, endorsement_id, **kwargs):
        """Revoke an endorsement."""
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            endorsement = request.env['product.endorsement'].with_user(SUPERUSER_ID).browse(endorsement_id)
            if not endorsement.exists():
                return error_response('Endorsement not found', 404, 'NOT_FOUND')

            endorsement.action_revoke()

            return success_response(
                format_endorsement(endorsement),
                message='เพิกถอนการรับรองสำเร็จ'
            )

        except Exception as e:
            _logger.error(f'Error revoking endorsement: {str(e)}')
            return error_response(str(e), 500)
