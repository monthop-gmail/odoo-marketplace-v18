# -*- coding: utf-8 -*-
"""
Mock Authentication API for local testing
"""
import json
import logging
import secrets
import hashlib
from datetime import datetime, timedelta

from odoo import http
from odoo.http import request

from .main import success_response, error_response

_logger = logging.getLogger(__name__)

# Simple in-memory session store for mock auth
# In production, this would be replaced by actual LINE authentication
_mock_sessions = {}


class AuthApiController(http.Controller):
    """Mock Authentication API for testing"""

    @http.route('/api/line-buyer/auth/mock/login', type='http', auth='none',
                methods=['POST', 'OPTIONS'], csrf=False)
    def mock_login(self, **kwargs):
        """
        Mock login endpoint for testing without LINE.

        POST body (JSON):
        - line_user_id: Simulated LINE user ID (optional, will generate if not provided)
        - display_name: Display name (optional)
        - channel_code: Channel code (default: demo_coop)

        Returns:
        - session_token: Token to use in X-Session-Token header
        - line_user_id: The LINE user ID (generated or provided)
        """
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        # Check if mock auth is enabled
        mock_auth = request.env['ir.config_parameter'].sudo().get_param(
            'core_line_integration.mock_auth', 'True'
        ) == 'True'

        if not mock_auth:
            return error_response('Mock authentication is disabled', 403)

        try:
            data = json.loads(request.httprequest.data.decode('utf-8')) if request.httprequest.data else {}
        except json.JSONDecodeError:
            data = {}

        # Generate or use provided LINE user ID
        line_user_id = data.get('line_user_id') or f'U{secrets.token_hex(16)}'
        display_name = data.get('display_name') or f'Test User {line_user_id[:8]}'
        channel_code = data.get('channel_code', 'demo_coop')

        # Get channel
        channel = request.env['line.channel'].sudo().search([
            ('code', '=', channel_code),
            ('active', '=', True),
        ], limit=1)

        if not channel:
            return error_response(f'Channel not found: {channel_code}', 404)

        # Create or get member
        member = request.env['line.channel.member'].sudo().get_or_create_member(
            channel.id,
            line_user_id,
            {'display_name': display_name}
        )

        # Generate session token
        session_token = secrets.token_urlsafe(32)
        expiry = datetime.now() + timedelta(hours=24)

        # Store session
        _mock_sessions[session_token] = {
            'line_user_id': line_user_id,
            'channel_code': channel_code,
            'member_id': member.id,
            'expiry': expiry,
        }

        return success_response({
            'session_token': session_token,
            'line_user_id': line_user_id,
            'display_name': display_name,
            'channel': {
                'code': channel.code,
                'name': channel.name,
            },
            'expires_at': expiry.isoformat(),
        })

    @http.route('/api/line-buyer/auth/mock/logout', type='http', auth='none',
                methods=['POST', 'OPTIONS'], csrf=False)
    def mock_logout(self, **kwargs):
        """Mock logout - invalidate session"""
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        session_token = request.httprequest.headers.get('X-Session-Token')
        if session_token and session_token in _mock_sessions:
            del _mock_sessions[session_token]

        return success_response(message='Logged out')

    @http.route('/api/line-buyer/auth/mock/session', type='http', auth='none',
                methods=['GET', 'OPTIONS'], csrf=False)
    def get_session(self, **kwargs):
        """Get current mock session info"""
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        session_token = request.httprequest.headers.get('X-Session-Token')
        if not session_token or session_token not in _mock_sessions:
            return error_response('Not authenticated', 401)

        session = _mock_sessions[session_token]
        if datetime.now() > session['expiry']:
            del _mock_sessions[session_token]
            return error_response('Session expired', 401)

        return success_response({
            'line_user_id': session['line_user_id'],
            'channel_code': session['channel_code'],
            'expires_at': session['expiry'].isoformat(),
        })

    @http.route('/api/line-buyer/auth/test-users', type='http', auth='none',
                methods=['GET', 'OPTIONS'], csrf=False)
    def get_test_users(self, **kwargs):
        """
        Get list of existing test users for easy testing.
        Only available when mock auth is enabled.
        """
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        mock_auth = request.env['ir.config_parameter'].sudo().get_param(
            'core_line_integration.mock_auth', 'True'
        ) == 'True'

        if not mock_auth:
            return error_response('Mock authentication is disabled', 403)

        # Get recent members
        members = request.env['line.channel.member'].sudo().search([
            ('is_following', '=', True),
        ], limit=10, order='create_date desc')

        users = []
        for m in members:
            users.append({
                'line_user_id': m.line_user_id,
                'display_name': m.display_name,
                'channel_code': m.channel_id.code,
                'channel_name': m.channel_id.name,
                'has_partner': bool(m.partner_id),
                'order_count': m.order_count,
            })

        return success_response({
            'users': users,
            'hint': 'Use line_user_id with /api/line-buyer/auth/mock/login to login as this user',
        })


# Middleware-like function to validate mock sessions
def validate_mock_session(func):
    """Decorator to validate mock session token"""
    from functools import wraps

    @wraps(func)
    def wrapper(*args, **kwargs):
        session_token = request.httprequest.headers.get('X-Session-Token')

        if session_token and session_token in _mock_sessions:
            session = _mock_sessions[session_token]
            if datetime.now() <= session['expiry']:
                # Set request attributes from session
                request.line_user_id = session['line_user_id']

                channel = request.env['line.channel'].sudo().search([
                    ('code', '=', session['channel_code'])
                ], limit=1)
                request.line_channel = channel

                member = request.env['line.channel.member'].sudo().browse(session['member_id'])
                request.line_member = member
                request.line_partner = member.partner_id

        return func(*args, **kwargs)
    return wrapper
