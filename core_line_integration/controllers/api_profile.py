# -*- coding: utf-8 -*-
"""
Buyer Profile API endpoints for LINE Marketplace
"""
import json
import logging

from odoo import http
from odoo.http import request

from .main import success_response, error_response, require_auth

_logger = logging.getLogger(__name__)


class ProfileApiController(http.Controller):
    """Buyer Profile API"""

    @http.route('/api/line-buyer/profile', type='http', auth='none', methods=['GET', 'OPTIONS'], csrf=False)
    @require_auth
    def get_profile(self, **kwargs):
        """Get current user profile"""
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            member = request.line_member
            partner = request.line_partner

            profile = {
                'line_user_id': member.line_user_id,
                'display_name': member.display_name,
                'picture_url': member.picture_url,
                'channel': {
                    'code': request.line_channel.code,
                    'name': request.line_channel.name,
                },
                'registration_state': member.registration_state,
                'is_verified': member.registration_state == 'verified',
            }

            if partner:
                profile.update({
                    'partner_id': partner.id,
                    'name': partner.name,
                    'email': partner.email or '',
                    'phone': partner.phone or partner.mobile or '',
                    'street': partner.street or '',
                    'city': partner.city or '',
                    'zip': partner.zip or '',
                    'notification_preferences': {
                        'orders': partner.line_notify_orders,
                        'promotions': partner.line_notify_promotions,
                    },
                    'stats': {
                        'order_count': member.order_count,
                        'total_spent': member.total_spent,
                    }
                })

            return success_response(profile)

        except Exception as e:
            _logger.error(f'Error in get_profile: {str(e)}')
            return error_response(str(e), 500)

    @http.route('/api/line-buyer/profile', type='http', auth='none', methods=['PUT', 'POST', 'OPTIONS'], csrf=False)
    @require_auth
    def update_profile(self, **kwargs):
        """
        Update user profile.

        PUT body (JSON):
        - name: Full name
        - email: Email address
        - phone: Phone number
        - street: Address
        - city: City
        - zip: Postal code
        - notify_orders: Order notification preference
        - notify_promotions: Promotion notification preference
        """
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            data = json.loads(request.httprequest.data.decode('utf-8'))

            # Ensure partner exists
            if not request.line_partner:
                request.line_partner = request.env['res.partner'].sudo().get_or_create_from_line(
                    request.line_user_id,
                    request.line_channel.id,
                    {'display_name': request.line_member.display_name}
                )
                request.line_member.sudo().with_context(
                    tracking_disable=True,
                ).partner_id = request.line_partner

            partner = request.line_partner

            # Update allowed fields
            update_vals = {}
            allowed_fields = {
                'name': 'name',
                'email': 'email',
                'phone': 'phone',
                'street': 'street',
                'city': 'city',
                'zip': 'zip',
            }

            for api_field, model_field in allowed_fields.items():
                if api_field in data:
                    update_vals[model_field] = data[api_field]

            # Handle notification preferences
            if 'notify_orders' in data:
                update_vals['line_notify_orders'] = bool(data['notify_orders'])
            if 'notify_promotions' in data:
                update_vals['line_notify_promotions'] = bool(data['notify_promotions'])

            if update_vals:
                # Get admin user for write operation (some fields may require user context)
                admin_user = request.env.ref('base.user_admin', raise_if_not_found=False)
                if not admin_user:
                    admin_user = request.env['res.users'].sudo().search([
                        ('active', '=', True),
                        ('share', '=', False),
                    ], limit=1)

                # Use tracking_disable context for API writes
                ctx = dict(
                    tracking_disable=True,
                    mail_create_nosubscribe=True,
                    mail_auto_subscribe_no_notify=True,
                )
                if admin_user:
                    partner.with_user(admin_user).with_context(**ctx).write(update_vals)
                else:
                    partner.sudo().with_context(**ctx).write(update_vals)

            # Update member registration state if profile is complete
            if partner.name and partner.phone:
                if request.line_member.registration_state == 'new':
                    request.line_member.sudo().with_context(
                        tracking_disable=True,
                    ).registration_state = 'profile_pending'

            return success_response({
                'partner_id': partner.id,
                'name': partner.name,
            }, message='Profile updated')

        except Exception as e:
            _logger.error(f'Error in update_profile: {str(e)}')
            return error_response(str(e), 500)

    @http.route('/api/line-buyer/profile/verify', type='http', auth='none', methods=['POST', 'OPTIONS'], csrf=False)
    @require_auth
    def request_verification(self, **kwargs):
        """
        Request profile verification.
        In production, this might trigger OTP verification via LINE.
        """
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            member = request.line_member
            partner = request.line_partner

            if not partner:
                return error_response('Profile not found. Please complete your profile first.', 400)

            if not partner.name or not partner.phone:
                return error_response('Please complete your name and phone number first.', 400)

            if member.registration_state == 'verified':
                return success_response({'status': 'already_verified'})

            # In mock mode, auto-verify
            mock_auth = request.env['ir.config_parameter'].sudo().get_param(
                'core_line_integration.mock_auth', 'True'
            ) == 'True'

            if mock_auth:
                member.registration_state = 'verified'
                return success_response({
                    'status': 'verified',
                }, message='Profile verified (mock mode)')
            else:
                # Production mode - would send OTP
                member.registration_state = 'profile_pending'
                return success_response({
                    'status': 'pending',
                }, message='Verification pending. Check your LINE for OTP.')

        except Exception as e:
            _logger.error(f'Error in request_verification: {str(e)}')
            return error_response(str(e), 500)

    @http.route('/api/line-buyer/profile/channels', type='http', auth='none', methods=['GET', 'OPTIONS'], csrf=False)
    @require_auth
    def get_channel_memberships(self, **kwargs):
        """Get all LINE channel memberships for current user"""
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            if not request.line_partner:
                return success_response({'memberships': []})

            memberships = request.env['line.channel.member'].sudo().search([
                ('partner_id', '=', request.line_partner.id),
            ])

            result = []
            for m in memberships:
                result.append({
                    'channel_code': m.channel_id.code,
                    'channel_name': m.channel_id.name,
                    'is_following': m.is_following,
                    'follow_date': m.follow_date.isoformat() if m.follow_date else None,
                    'order_count': m.order_count,
                })

            return success_response({'memberships': result})

        except Exception as e:
            _logger.error(f'Error in get_channel_memberships: {str(e)}')
            return error_response(str(e), 500)
