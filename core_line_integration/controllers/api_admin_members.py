# -*- coding: utf-8 -*-
"""
Admin Members & Sellers API
- GET /api/line-admin/members — member list
- GET /api/line-admin/members/<id> — member detail
- GET /api/line-admin/sellers — seller list
- GET /api/line-admin/sellers/<id> — seller detail
- POST /api/line-admin/sellers/<id>/approve — approve seller
- POST /api/line-admin/sellers/<id>/deny — deny seller
- GET /api/line-admin/shops/<id>/staff — list shop staff
- POST /api/line-admin/shops/<id>/staff — add staff via admin
- DELETE /api/line-admin/shops/<id>/staff/<staff_id> — remove staff via admin
"""
import json
import logging

from odoo import http
from odoo.http import request

from .main import success_response, error_response
from .admin_main import require_admin, format_member, format_seller

_logger = logging.getLogger(__name__)

MEMBERS_PER_PAGE = 20


class LineAdminMembersController(http.Controller):

    # ==================== Members ====================

    @http.route('/api/line-admin/members', type='http', auth='none',
                methods=['GET', 'OPTIONS'], csrf=False)
    @require_admin
    def get_members(self):
        """List LINE channel members with search and filter"""
        try:
            params = request.params
            search = params.get('search', '').strip()
            member_type = params.get('type', '')
            page = int(params.get('page', 1))
            limit = int(params.get('limit', MEMBERS_PER_PAGE))
            offset = (page - 1) * limit

            domain = [('channel_id', '=', request.line_channel.id)]

            if search:
                domain.append(('display_name', 'ilike', search))
            if member_type and member_type != 'all':
                domain.append(('member_type', '=', member_type))

            Member = request.env['line.channel.member'].sudo()
            total = Member.search_count(domain)
            members = Member.search(domain, limit=limit, offset=offset, order='create_date desc')

            return success_response({
                'members': [format_member(m) for m in members],
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': total,
                    'pages': (total + limit - 1) // limit if limit else 1,
                },
            })

        except Exception as e:
            _logger.error(f'Admin members list error: {e}')
            return error_response(str(e), 500, 'MEMBERS_ERROR')

    @http.route('/api/line-admin/members/<int:member_id>', type='http', auth='none',
                methods=['GET', 'OPTIONS'], csrf=False)
    @require_admin
    def get_member_detail(self, member_id):
        """Get member detail with order history"""
        try:
            member = request.env['line.channel.member'].sudo().browse(member_id)
            if not member.exists():
                return error_response('Member not found', 404, 'MEMBER_NOT_FOUND')

            data = format_member(member)

            # Add recent orders if partner exists
            data['recent_orders'] = []
            if member.partner_id:
                orders = request.env['sale.order'].sudo().search([
                    ('partner_id', '=', member.partner_id.id),
                    ('state', 'in', ['sale', 'done']),
                ], limit=10, order='date_order desc')

                data['recent_orders'] = [{
                    'id': o.id,
                    'name': o.name,
                    'date': o.date_order.isoformat() if o.date_order else None,
                    'state': o.state,
                    'total': o.amount_total,
                    'currency': o.currency_id.symbol if o.currency_id else '฿',
                } for o in orders]

            # Check if member is a seller
            if member.partner_id and member.partner_id.seller:
                data['seller_info'] = format_seller(member.partner_id)

            return success_response(data)

        except Exception as e:
            _logger.error(f'Admin member detail error: {e}')
            return error_response(str(e), 500, 'MEMBER_ERROR')

    # ==================== Sellers ====================

    @http.route('/api/line-admin/sellers', type='http', auth='none',
                methods=['GET', 'OPTIONS'], csrf=False)
    @require_admin
    def get_sellers(self):
        """List marketplace sellers with state filter"""
        try:
            params = request.params
            state = params.get('state', '')
            search = params.get('search', '').strip()
            page = int(params.get('page', 1))
            limit = int(params.get('limit', MEMBERS_PER_PAGE))
            offset = (page - 1) * limit

            domain = [('seller', '=', True)]

            if state and state != 'all':
                domain.append(('state', '=', state))
            if search:
                domain.append(('name', 'ilike', search))

            Partner = request.env['res.partner'].sudo()
            total = Partner.search_count(domain)
            sellers = Partner.search(domain, limit=limit, offset=offset, order='create_date desc')

            # Count by state
            state_counts = {
                'pending': Partner.search_count([('seller', '=', True), ('state', '=', 'pending')]),
                'approved': Partner.search_count([('seller', '=', True), ('state', '=', 'approved')]),
                'denied': Partner.search_count([('seller', '=', True), ('state', '=', 'denied')]),
            }

            return success_response({
                'sellers': [format_seller(s) for s in sellers],
                'state_counts': state_counts,
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': total,
                    'pages': (total + limit - 1) // limit if limit else 1,
                },
            })

        except Exception as e:
            _logger.error(f'Admin sellers list error: {e}')
            return error_response(str(e), 500, 'SELLERS_ERROR')

    @http.route('/api/line-admin/sellers/<int:seller_id>', type='http', auth='none',
                methods=['GET', 'OPTIONS'], csrf=False)
    @require_admin
    def get_seller_detail(self, seller_id):
        """Get seller detail with products and orders"""
        try:
            partner = request.env['res.partner'].sudo().browse(seller_id)
            if not partner.exists() or not partner.seller:
                return error_response('Seller not found', 404, 'SELLER_NOT_FOUND')

            data = format_seller(partner)

            # Recent products
            products = []
            ProductTemplate = request.env['product.template'].sudo()
            if 'marketplace_seller_id' in ProductTemplate._fields:
                product_recs = ProductTemplate.search([
                    ('marketplace_seller_id', '=', partner.id),
                ], limit=10, order='create_date desc')
                products = [{
                    'id': p.id,
                    'name': p.name,
                    'price': p.list_price,
                    'status': p.status if 'status' in p._fields else '',
                    'is_published': p.is_published if hasattr(p, 'is_published') else False,
                } for p in product_recs]
            data['products'] = products

            # Recent orders for this seller
            orders = []
            OrderLine = request.env['sale.order.line'].sudo()
            if 'marketplace_seller_id' in OrderLine._fields:
                order_lines = OrderLine.search([
                    ('marketplace_seller_id', '=', partner.id),
                    ('order_id.state', 'in', ['sale', 'done']),
                ], limit=10, order='create_date desc')
                seen_orders = set()
                for line in order_lines:
                    if line.order_id.id not in seen_orders:
                        seen_orders.add(line.order_id.id)
                        orders.append({
                            'id': line.order_id.id,
                            'name': line.order_id.name,
                            'date': line.order_id.date_order.isoformat() if line.order_id.date_order else None,
                            'total': line.order_id.amount_total,
                            'state': line.order_id.state,
                        })
            data['orders'] = orders

            # LINE member info
            if partner:
                member = request.env['line.channel.member'].sudo().search([
                    ('partner_id', '=', partner.id),
                    ('channel_id', '=', request.line_channel.id),
                ], limit=1)
                if member:
                    data['line_member'] = format_member(member)

            return success_response(data)

        except Exception as e:
            _logger.error(f'Admin seller detail error: {e}')
            return error_response(str(e), 500, 'SELLER_ERROR')

    @http.route('/api/line-admin/sellers/<int:seller_id>/approve', type='http', auth='none',
                methods=['POST', 'OPTIONS'], csrf=False)
    @require_admin
    def approve_seller(self, seller_id):
        """Approve a pending seller"""
        try:
            partner = request.env['res.partner'].with_user(request.admin_user).browse(seller_id)
            if not partner.exists() or not partner.seller:
                return error_response('Seller not found', 404, 'SELLER_NOT_FOUND')

            if partner.state != 'pending':
                return error_response(
                    f'Seller is {partner.state}, can only approve pending sellers',
                    400, 'INVALID_STATE'
                )

            partner.approve()

            _logger.info(f'Admin {request.admin_user.name} approved seller {partner.name} (ID: {partner.id})')

            return success_response({
                'seller': format_seller(partner),
            }, message='Seller approved successfully')

        except Exception as e:
            _logger.error(f'Seller approve error: {e}')
            return error_response(str(e), 500, 'APPROVE_ERROR')

    @http.route('/api/line-admin/sellers/<int:seller_id>/deny', type='http', auth='none',
                methods=['POST', 'OPTIONS'], csrf=False)
    @require_admin
    def deny_seller(self, seller_id):
        """Deny a pending seller"""
        try:
            partner = request.env['res.partner'].with_user(request.admin_user).browse(seller_id)
            if not partner.exists() or not partner.seller:
                return error_response('Seller not found', 404, 'SELLER_NOT_FOUND')

            if partner.state != 'pending':
                return error_response(
                    f'Seller is {partner.state}, can only deny pending sellers',
                    400, 'INVALID_STATE'
                )

            partner.deny()

            _logger.info(f'Admin {request.admin_user.name} denied seller {partner.name} (ID: {partner.id})')

            return success_response({
                'seller': format_seller(partner),
            }, message='Seller denied successfully')

        except Exception as e:
            _logger.error(f'Seller deny error: {e}')
            return error_response(str(e), 500, 'DENY_ERROR')

    # ==================== Shop Staff (Admin) ====================

    @http.route('/api/line-admin/shops/<int:shop_id>/staff', type='http', auth='none',
                methods=['GET', 'OPTIONS'], csrf=False)
    @require_admin
    def list_shop_staff(self, shop_id):
        """List staff members of a shop."""
        try:
            shop = request.env['seller.shop'].sudo().browse(shop_id)
            if not shop.exists():
                return error_response('Shop not found', 404, 'SHOP_NOT_FOUND')

            staff_records = request.env['seller.shop.staff'].sudo().search([
                ('shop_id', '=', shop.id),
            ], order='join_date desc')

            return success_response({
                'shop': {'id': shop.id, 'name': shop.name},
                'staff': [{
                    'id': s.id,
                    'partner_id': s.staff_partner_id.id,
                    'name': s.staff_partner_id.name or '',
                    'role': s.role,
                    'is_active': s.is_active,
                    'join_date': s.join_date.isoformat() if s.join_date else None,
                    'invited_by': s.invited_by.name if s.invited_by else '',
                } for s in staff_records],
                'total': len(staff_records),
            })

        except Exception as e:
            _logger.error(f'Admin list shop staff error: {e}')
            return error_response(str(e), 500, 'STAFF_LIST_ERROR')

    @http.route('/api/line-admin/shops/<int:shop_id>/staff', type='http', auth='none',
                methods=['POST', 'OPTIONS'], csrf=False)
    @require_admin
    def add_shop_staff(self, shop_id):
        """Add a staff member to a shop via admin."""
        try:
            shop = request.env['seller.shop'].sudo().browse(shop_id)
            if not shop.exists():
                return error_response('Shop not found', 404, 'SHOP_NOT_FOUND')

            body = json.loads(request.httprequest.data or '{}')
            partner_id = int(body.get('partner_id', 0))
            role = body.get('role', 'staff')

            if not partner_id:
                return error_response('partner_id is required', 400, 'MISSING_PARTNER_ID')
            if role not in ('staff', 'manager'):
                return error_response('role must be "staff" or "manager"', 400, 'INVALID_ROLE')

            partner = request.env['res.partner'].sudo().browse(partner_id)
            if not partner.exists():
                return error_response('Partner not found', 404, 'PARTNER_NOT_FOUND')

            if partner.seller and partner.state == 'approved':
                return error_response(
                    'An approved seller cannot be added as staff',
                    400, 'IS_APPROVED_SELLER'
                )

            # Check existing staff record
            existing = request.env['seller.shop.staff'].sudo().search([
                ('staff_partner_id', '=', partner.id),
                ('is_active', '=', True),
            ], limit=1)
            if existing:
                return error_response(
                    'This person is already active staff in a shop',
                    400, 'ALREADY_STAFF'
                )

            staff = request.env['seller.shop.staff'].sudo().create({
                'shop_id': shop.id,
                'staff_partner_id': partner.id,
                'role': role,
                'invited_by': request.admin_user.partner_id.id,
            })

            # Sync LINE member type
            member = request.env['line.channel.member'].sudo().search([
                ('partner_id', '=', partner.id),
                ('channel_id', '=', request.line_channel.id),
            ], limit=1)
            if member:
                member.sync_member_type_from_partner()

            _logger.info(f'Admin {request.admin_user.name} added staff {partner.name} to shop {shop.name}')

            return success_response({
                'staff': {
                    'id': staff.id,
                    'partner_id': partner.id,
                    'name': partner.name,
                    'role': staff.role,
                    'is_active': staff.is_active,
                },
            }, message='Staff member added successfully')

        except (json.JSONDecodeError, ValueError):
            return error_response('Invalid JSON body', 400, 'INVALID_JSON')
        except Exception as e:
            _logger.error(f'Admin add shop staff error: {e}')
            return error_response(str(e), 500, 'STAFF_ADD_ERROR')

    @http.route('/api/line-admin/shops/<int:shop_id>/staff/<int:staff_id>', type='http', auth='none',
                methods=['DELETE', 'OPTIONS'], csrf=False)
    @require_admin
    def remove_shop_staff(self, shop_id, staff_id):
        """Remove a staff member from a shop via admin."""
        try:
            staff = request.env['seller.shop.staff'].sudo().browse(staff_id)
            if not staff.exists() or staff.shop_id.id != shop_id:
                return error_response('Staff not found', 404, 'STAFF_NOT_FOUND')

            staff.sudo().write({'is_active': False})

            # Sync LINE member type
            member = request.env['line.channel.member'].sudo().search([
                ('partner_id', '=', staff.staff_partner_id.id),
                ('channel_id', '=', request.line_channel.id),
            ], limit=1)
            if member:
                member.sync_member_type_from_partner()

            _logger.info(f'Admin {request.admin_user.name} removed staff {staff.staff_partner_id.name} from shop {staff.shop_id.name}')

            return success_response(message='Staff member removed')

        except Exception as e:
            _logger.error(f'Admin remove shop staff error: {e}')
            return error_response(str(e), 500, 'STAFF_REMOVE_ERROR')
