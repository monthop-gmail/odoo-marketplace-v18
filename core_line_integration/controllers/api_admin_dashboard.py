# -*- coding: utf-8 -*-
"""
Admin Dashboard API
GET /api/line-admin/dashboard — platform stats, alerts
"""
import logging
from datetime import datetime, timedelta

from odoo import http
from odoo.http import request

from .main import success_response, error_response
from .admin_main import require_admin

_logger = logging.getLogger(__name__)


class LineAdminDashboardController(http.Controller):

    @http.route('/api/line-admin/dashboard', type='http', auth='none',
                methods=['GET', 'OPTIONS'], csrf=False)
    @require_admin
    def get_dashboard(self):
        """Get platform dashboard stats"""
        try:
            today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

            # Total LINE members
            total_members = request.env['line.channel.member'].sudo().search_count([
                ('channel_id', '=', request.line_channel.id),
            ])

            # Today's orders (confirmed+)
            today_orders = request.env['sale.order'].sudo().search_count([
                ('date_order', '>=', today_start),
                ('state', 'in', ['sale', 'done']),
            ])

            # Active sellers
            active_sellers = request.env['res.partner'].sudo().search_count([
                ('seller', '=', True),
                ('state', '=', 'approved'),
            ])

            # Today's revenue
            today_sales = request.env['sale.order'].sudo().search([
                ('date_order', '>=', today_start),
                ('state', 'in', ['sale', 'done']),
            ])
            today_revenue = sum(today_sales.mapped('amount_total'))

            # Pending sellers (awaiting approval)
            pending_sellers = request.env['res.partner'].sudo().search_count([
                ('seller', '=', True),
                ('state', '=', 'pending'),
            ])

            # Pending products (awaiting approval)
            pending_products = 0
            ProductTemplate = request.env['product.template'].sudo()
            if 'status' in ProductTemplate._fields:
                pending_products = ProductTemplate.search_count([
                    ('status', '=', 'pending'),
                ])

            # New members today
            new_members_today = request.env['line.channel.member'].sudo().search_count([
                ('channel_id', '=', request.line_channel.id),
                ('create_date', '>=', today_start),
            ])

            # Build alerts
            alerts = []
            if pending_sellers > 0:
                alerts.append({
                    'type': 'warning',
                    'icon': 'fa-user-clock',
                    'title': f'{pending_sellers} seller(s) pending approval',
                    'subtitle': 'Review and approve/deny seller applications',
                })
            if pending_products > 0:
                alerts.append({
                    'type': 'warning',
                    'icon': 'fa-box',
                    'title': f'{pending_products} product(s) pending approval',
                    'subtitle': 'Review marketplace product submissions',
                })
            if new_members_today > 0:
                alerts.append({
                    'type': 'info',
                    'icon': 'fa-user-plus',
                    'title': f'{new_members_today} new member(s) today',
                    'subtitle': 'New LINE followers joined',
                })

            return success_response({
                'stats': {
                    'total_members': total_members,
                    'today_orders': today_orders,
                    'active_sellers': active_sellers,
                    'today_revenue': today_revenue,
                    'currency': '฿',
                    'pending_sellers': pending_sellers,
                    'pending_products': pending_products,
                    'new_members_today': new_members_today,
                },
                'alerts': alerts,
            })

        except Exception as e:
            _logger.error(f'Admin dashboard error: {e}')
            return error_response(str(e), 500, 'DASHBOARD_ERROR')
