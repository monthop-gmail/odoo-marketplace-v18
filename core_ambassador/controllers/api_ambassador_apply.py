# -*- coding: utf-8 -*-
"""
Ambassador Application API - allows buyers to apply as ambassadors via LINE LIFF
"""
import json
import logging

from odoo import http, SUPERUSER_ID
from odoo.http import request

from odoo.addons.core_line_integration.controllers.main import (
    success_response, error_response, require_auth
)

_logger = logging.getLogger(__name__)


class AmbassadorApplyController(http.Controller):
    """Ambassador registration/application API for buyers"""

    @http.route('/api/line-buyer/ambassador/status', type='http', auth='none',
                methods=['GET', 'OPTIONS'], csrf=False)
    @require_auth
    def get_ambassador_status(self, **kwargs):
        """Get current user's ambassador status."""
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            partner = request.line_partner

            if not partner:
                return success_response({
                    'is_ambassador': False,
                    'ambassador_status': None,
                    'can_apply': True,
                    'message': 'ยังไม่ได้สมัครเป็น Ambassador',
                })

            if not partner.is_ambassador or partner.ambassador_state == 'none':
                return success_response({
                    'is_ambassador': False,
                    'ambassador_status': None,
                    'can_apply': True,
                    'message': 'ยังไม่ได้สมัครเป็น Ambassador',
                })

            status_messages = {
                'draft': 'กำลังกรอกใบสมัคร',
                'pending': 'รอการอนุมัติ',
                'approved': 'อนุมัติแล้ว',
                'rejected': 'ถูกปฏิเสธ',
                'suspended': 'ถูกระงับ',
            }

            data = {
                'is_ambassador': partner.ambassador_state == 'approved',
                'ambassador_status': partner.ambassador_state,
                'can_apply': partner.ambassador_state in ('none', 'rejected'),
                'message': status_messages.get(partner.ambassador_state, ''),
                'tier': partner.ambassador_tier,
                'commission_rate': partner.ambassador_commission_rate,
            }

            if partner.ambassador_state == 'approved':
                data.update({
                    'endorsement_count': partner.endorsement_count,
                    'approved_date': partner.ambassador_approved_date.isoformat()
                        if partner.ambassador_approved_date else None,
                })

            return success_response(data)

        except Exception as e:
            _logger.error(f'Error getting ambassador status: {str(e)}')
            return error_response(str(e), 500)

    @http.route('/api/line-buyer/ambassador/apply', type='http', auth='none',
                methods=['POST', 'OPTIONS'], csrf=False)
    @require_auth
    def apply_ambassador(self, **kwargs):
        """
        Submit ambassador application.

        JSON body:
        - full_name (required)
        - phone, email
        - specialty_ids (list of int)
        - bio, experience, motivation
        - social_youtube, social_facebook, social_tiktok, social_instagram
        - portfolio_url
        - requested_tier (bronze/silver/gold, default bronze)
        """
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            partner = request.line_partner
            if not partner:
                return error_response('User profile not found', 400, 'NO_PROFILE')

            # Check if already ambassador or has pending application
            if partner.is_ambassador and partner.ambassador_state in ('pending', 'approved'):
                return error_response(
                    'คุณสมัครเป็น Ambassador อยู่แล้ว',
                    400, 'ALREADY_APPLIED'
                )

            body = json.loads(request.httprequest.data or '{}')

            full_name = body.get('full_name', '').strip()
            if not full_name:
                return error_response('กรุณาระบุชื่อ-นามสกุล', 400, 'VALIDATION_ERROR')

            sudo = lambda model: request.env[model].with_user(SUPERUSER_ID)

            # Check existing application
            existing = sudo('ambassador.application').search([
                ('partner_id', '=', partner.id),
                ('state', 'not in', ('rejected',)),
            ], limit=1)
            if existing:
                return error_response(
                    'คุณมีใบสมัครอยู่แล้ว',
                    400, 'APPLICATION_EXISTS'
                )

            # Validate specialties
            specialty_ids = body.get('specialty_ids', [])
            if specialty_ids:
                valid_specialties = sudo('ambassador.specialty').search([
                    ('id', 'in', specialty_ids),
                    ('active', '=', True),
                ])
                specialty_ids = valid_specialties.ids

            vals = {
                'partner_id': partner.id,
                'full_name': full_name,
                'phone': body.get('phone', partner.phone or ''),
                'email': body.get('email', partner.email or ''),
                'specialty_ids': [(6, 0, specialty_ids)],
                'bio': body.get('bio', ''),
                'experience': body.get('experience', ''),
                'motivation': body.get('motivation', ''),
                'social_youtube': body.get('social_youtube', ''),
                'social_facebook': body.get('social_facebook', ''),
                'social_tiktok': body.get('social_tiktok', ''),
                'social_instagram': body.get('social_instagram', ''),
                'portfolio_url': body.get('portfolio_url', ''),
                'requested_tier': body.get('requested_tier', 'bronze'),
            }

            application = sudo('ambassador.application').create(vals)
            application.action_submit()

            # Check auto-approve
            auto_approve = request.env['ir.config_parameter'].sudo().get_param(
                'core_ambassador.auto_approve', 'False'
            )
            if auto_approve == 'True':
                application.action_approve()

            return success_response({
                'application_id': application.id,
                'application_name': application.name,
                'state': application.state,
            }, message='สมัครเป็น Ambassador สำเร็จ')

        except json.JSONDecodeError:
            return error_response('Invalid JSON body', 400, 'INVALID_JSON')
        except Exception as e:
            _logger.error(f'Error applying ambassador: {str(e)}')
            return error_response(str(e), 500)

    @http.route('/api/line-buyer/ambassador/specialties', type='http', auth='none',
                methods=['GET', 'OPTIONS'], csrf=False)
    @require_auth
    def get_specialties(self, **kwargs):
        """List available ambassador specialties."""
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            specialties = request.env['ambassador.specialty'].sudo().search([
                ('active', '=', True),
            ], order='sequence, name')

            return success_response({
                'items': [{
                    'id': s.id,
                    'name': s.name,
                    'code': s.code,
                    'icon': s.icon or '',
                    'description': s.description or '',
                } for s in specialties],
            })

        except Exception as e:
            _logger.error(f'Error getting specialties: {str(e)}')
            return error_response(str(e), 500)
