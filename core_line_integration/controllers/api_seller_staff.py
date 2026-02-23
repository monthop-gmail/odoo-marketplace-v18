# -*- coding: utf-8 -*-
"""
Seller Staff Management API endpoints for LIFF Seller App
- GET  /api/line-seller/staff         — list shop staff (owner only)
- POST /api/line-seller/staff/invite   — invite staff by LINE user ID (owner only)
- DELETE /api/line-seller/staff/<id>   — remove staff (owner only)
- GET  /api/line-seller/staff/my-status — get current user's staff status
"""
import json
import logging

from odoo import http
from odoo.http import request

from .seller_main import require_seller, owner_only
from .main import require_auth, success_response, error_response

_logger = logging.getLogger(__name__)


def _format_staff(staff):
    """Format staff record for API response."""
    return {
        'id': staff.id,
        'partner_id': staff.staff_partner_id.id,
        'name': staff.staff_partner_id.name or '',
        'role': staff.role,
        'is_active': staff.is_active,
        'join_date': staff.join_date.isoformat() if staff.join_date else None,
        'invited_by': staff.invited_by.name if staff.invited_by else '',
    }


class SellerStaffController(http.Controller):

    @http.route('/api/line-seller/staff', type='http', auth='none',
                methods=['GET', 'OPTIONS'], csrf=False)
    @require_seller
    @owner_only
    def list_staff(self, **kwargs):
        """List all staff members of the shop (owner only)."""
        seller = request.seller_partner
        shop = seller.seller_shop_id if hasattr(seller, 'seller_shop_id') else None
        if not shop:
            return error_response('Shop not found', 404, 'SHOP_NOT_FOUND')

        staff_records = request.env['seller.shop.staff'].sudo().search([
            ('shop_id', '=', shop.id),
        ], order='join_date desc')

        return success_response({
            'staff': [_format_staff(s) for s in staff_records],
            'total': len(staff_records),
        })

    @http.route('/api/line-seller/staff/invite', type='http', auth='none',
                methods=['POST', 'OPTIONS'], csrf=False)
    @require_seller
    @owner_only
    def invite_staff(self, **kwargs):
        """Invite a new staff member by LINE user ID (owner only)."""
        seller = request.seller_partner
        shop = seller.seller_shop_id if hasattr(seller, 'seller_shop_id') else None
        if not shop:
            return error_response('Shop not found', 404, 'SHOP_NOT_FOUND')

        try:
            body = json.loads(request.httprequest.data or '{}')
        except (json.JSONDecodeError, ValueError):
            return error_response('Invalid JSON body', 400, 'INVALID_JSON')

        line_user_id = body.get('line_user_id', '').strip()
        role = body.get('role', 'staff')

        if not line_user_id:
            return error_response('line_user_id is required', 400, 'MISSING_LINE_USER_ID')
        if role not in ('staff', 'manager'):
            return error_response('role must be "staff" or "manager"', 400, 'INVALID_ROLE')

        # Find the LINE channel member and their partner
        member = request.env['line.channel.member'].sudo().search([
            ('line_user_id', '=', line_user_id),
            ('channel_id', '=', request.line_channel.id),
        ], limit=1)

        if not member or not member.partner_id:
            return error_response(
                'LINE user not found or not registered',
                404, 'USER_NOT_FOUND'
            )

        partner = member.partner_id

        # Cannot invite yourself
        if partner.id == seller.id:
            return error_response('Cannot add yourself as staff', 400, 'SELF_INVITE')

        # Cannot invite an approved seller
        if partner.seller and partner.state == 'approved':
            return error_response(
                'An approved seller cannot be added as staff',
                400, 'IS_APPROVED_SELLER'
            )

        # Check if already staff somewhere
        existing = request.env['seller.shop.staff'].sudo().search([
            ('staff_partner_id', '=', partner.id),
        ], limit=1)
        if existing:
            if existing.shop_id.id == shop.id and existing.is_active:
                return error_response('This person is already staff in your shop', 400, 'ALREADY_STAFF')
            elif existing.is_active:
                return error_response(
                    'This person is already staff in another shop',
                    400, 'STAFF_IN_OTHER_SHOP'
                )
            else:
                # Reactivate and reassign to this shop
                existing.sudo().write({
                    'shop_id': shop.id,
                    'role': role,
                    'is_active': True,
                    'invited_by': seller.id,
                    'join_date': request.env['seller.shop.staff']._fields['join_date'].default(
                        request.env['seller.shop.staff']
                    ),
                })
                # Sync LINE member type
                member.sync_member_type_from_partner()
                return success_response({
                    'staff': _format_staff(existing),
                }, message='Staff member reactivated')

        try:
            staff = request.env['seller.shop.staff'].sudo().create({
                'shop_id': shop.id,
                'staff_partner_id': partner.id,
                'role': role,
                'invited_by': seller.id,
            })
            # Sync LINE member type to 'seller' for staff
            member.sync_member_type_from_partner()

            return success_response({
                'staff': _format_staff(staff),
            }, message='Staff member invited successfully')
        except Exception as e:
            _logger.warning('Staff invite failed: %s', str(e))
            return error_response(str(e), 400, 'INVITE_FAILED')

    @http.route('/api/line-seller/staff/<int:staff_id>', type='http', auth='none',
                methods=['DELETE', 'OPTIONS'], csrf=False)
    @require_seller
    @owner_only
    def remove_staff(self, staff_id, **kwargs):
        """Remove a staff member (owner only). Deactivates, does not delete."""
        seller = request.seller_partner
        shop = seller.seller_shop_id if hasattr(seller, 'seller_shop_id') else None
        if not shop:
            return error_response('Shop not found', 404, 'SHOP_NOT_FOUND')

        staff = request.env['seller.shop.staff'].sudo().browse(staff_id)
        if not staff.exists() or staff.shop_id.id != shop.id:
            return error_response('Staff not found', 404, 'STAFF_NOT_FOUND')

        staff.sudo().write({'is_active': False})

        # Sync the removed staff's LINE member type back to 'buyer'
        member = request.env['line.channel.member'].sudo().search([
            ('partner_id', '=', staff.staff_partner_id.id),
            ('channel_id', '=', request.line_channel.id),
        ], limit=1)
        if member:
            member.sync_member_type_from_partner()

        return success_response(message='Staff member removed')

    @http.route('/api/line-seller/staff/my-status', type='http', auth='none',
                methods=['GET', 'OPTIONS'], csrf=False)
    @require_auth
    def get_my_staff_status(self, **kwargs):
        """Get current user's staff status (any authenticated user)."""
        partner = request.line_partner
        if not partner:
            return error_response('Not authenticated', 401)

        staff = request.env['seller.shop.staff'].sudo().search([
            ('staff_partner_id', '=', partner.id),
            ('is_active', '=', True),
        ], limit=1)

        if not staff:
            return success_response({
                'is_staff': False,
                'staff': None,
            })

        return success_response({
            'is_staff': True,
            'staff': {
                'id': staff.id,
                'shop_id': staff.shop_id.id,
                'shop_name': staff.shop_id.name,
                'role': staff.role,
                'owner_name': staff.seller_id.name if staff.seller_id else '',
                'join_date': staff.join_date.isoformat() if staff.join_date else None,
            },
        })
