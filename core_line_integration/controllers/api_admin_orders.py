# -*- coding: utf-8 -*-
"""
Admin Orders, Notifications & Settings API
- GET /api/line-admin/orders — all platform orders
- GET /api/line-admin/orders/stats — order stats by state
- GET /api/line-admin/orders/<id> — order detail
- POST /api/line-admin/notifications/send — send broadcast
- GET /api/line-admin/notifications/history — notification log
- GET /api/line-admin/settings — channel info
- PUT /api/line-admin/settings — update settings
"""
import json
import logging
from datetime import datetime

from odoo import http
from odoo.http import request

from .main import success_response, error_response
from .admin_main import (
    require_admin, format_admin_order, format_admin_order_detail, format_notify_log
)

_logger = logging.getLogger(__name__)

ORDERS_PER_PAGE = 20
NOTIFICATIONS_PER_PAGE = 20


class LineAdminOrdersController(http.Controller):

    # ==================== Orders ====================

    @http.route('/api/line-admin/orders', type='http', auth='none',
                methods=['GET', 'OPTIONS'], csrf=False)
    @require_admin
    def get_orders(self):
        """List all platform orders with filter"""
        try:
            params = request.params
            status = params.get('status', '')
            search = params.get('search', '').strip()
            page = int(params.get('page', 1))
            limit = int(params.get('limit', ORDERS_PER_PAGE))
            offset = (page - 1) * limit

            domain = []

            if status and status != 'all':
                domain.append(('state', '=', status))
            else:
                # Exclude draft/cancelled by default
                domain.append(('state', 'not in', ['draft', 'cancel']))

            if search:
                domain.append('|')
                domain.append(('name', 'ilike', search))
                domain.append(('partner_id.name', 'ilike', search))

            Order = request.env['sale.order'].sudo()
            total = Order.search_count(domain)
            orders = Order.search(domain, limit=limit, offset=offset, order='date_order desc')

            return success_response({
                'orders': [format_admin_order(o) for o in orders],
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': total,
                    'pages': (total + limit - 1) // limit if limit else 1,
                },
            })

        except Exception as e:
            _logger.error(f'Admin orders list error: {e}')
            return error_response(str(e), 500, 'ORDERS_ERROR')

    @http.route('/api/line-admin/orders/stats', type='http', auth='none',
                methods=['GET', 'OPTIONS'], csrf=False)
    @require_admin
    def get_order_stats(self):
        """Get order count by state"""
        try:
            Order = request.env['sale.order'].sudo()

            today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

            stats = {
                'draft': Order.search_count([('state', '=', 'draft')]),
                'sent': Order.search_count([('state', '=', 'sent')]),
                'sale': Order.search_count([('state', '=', 'sale')]),
                'done': Order.search_count([('state', '=', 'done')]),
                'cancel': Order.search_count([('state', '=', 'cancel')]),
                'today_total': Order.search_count([
                    ('date_order', '>=', today_start),
                    ('state', 'in', ['sale', 'done']),
                ]),
            }

            # Today's revenue
            today_orders = Order.search([
                ('date_order', '>=', today_start),
                ('state', 'in', ['sale', 'done']),
            ])
            stats['today_revenue'] = sum(today_orders.mapped('amount_total'))
            stats['currency'] = '฿'

            return success_response(stats)

        except Exception as e:
            _logger.error(f'Admin order stats error: {e}')
            return error_response(str(e), 500, 'ORDER_STATS_ERROR')

    @http.route('/api/line-admin/orders/<int:order_id>', type='http', auth='none',
                methods=['GET', 'OPTIONS'], csrf=False)
    @require_admin
    def get_order_detail(self, order_id):
        """Get order detail"""
        try:
            order = request.env['sale.order'].sudo().browse(order_id)
            if not order.exists():
                return error_response('Order not found', 404, 'ORDER_NOT_FOUND')

            return success_response(format_admin_order_detail(order))

        except Exception as e:
            _logger.error(f'Admin order detail error: {e}')
            return error_response(str(e), 500, 'ORDER_ERROR')

    # ==================== Notifications ====================

    @http.route('/api/line-admin/notifications/send', type='http', auth='none',
                methods=['POST', 'OPTIONS'], csrf=False)
    @require_admin
    def send_notification(self):
        """Send broadcast notification via LINE"""
        try:
            body = json.loads(request.httprequest.data or '{}')
            target = body.get('target', 'all')  # all, buyers, sellers
            message_type = body.get('message_type', 'text')  # text, flex
            message = body.get('message', '').strip()

            if not message:
                return error_response('Message is required', 400, 'MISSING_MESSAGE')

            channel = request.line_channel

            # Get target members
            domain = [
                ('channel_id', '=', channel.id),
                ('is_following', '=', True),
            ]
            if target == 'sellers':
                domain.append(('member_type', '=', 'seller'))
            elif target == 'buyers':
                domain.append(('member_type', 'in', ['buyer', False]))

            members = request.env['line.channel.member'].sudo().search(domain)

            if not members:
                return error_response('No target members found', 400, 'NO_TARGETS')

            # Create notification logs for each member
            NotifyLog = request.env['line.notify.log'].sudo()
            sent_count = 0
            failed_count = 0

            for member in members:
                log_vals = {
                    'channel_id': channel.id,
                    'partner_id': member.partner_id.id if member.partner_id else False,
                    'line_user_id': member.line_user_id,
                    'notify_type': 'custom',
                    'message_type': message_type,
                    'message': message,
                    'state': 'pending',
                }

                if message_type == 'flex':
                    log_vals['flex_json'] = message
                    log_vals['message'] = 'Flex message'

                log = NotifyLog.create(log_vals)

                try:
                    log.action_send()
                    if log.state == 'sent':
                        sent_count += 1
                    else:
                        failed_count += 1
                except Exception as send_err:
                    _logger.warning(f'Failed to send to {member.line_user_id}: {send_err}')
                    failed_count += 1

            _logger.info(
                f'Admin {request.admin_user.name} sent broadcast: '
                f'target={target}, sent={sent_count}, failed={failed_count}'
            )

            return success_response({
                'sent_count': sent_count,
                'failed_count': failed_count,
                'total_targets': len(members),
            }, message=f'Notification sent to {sent_count} members')

        except json.JSONDecodeError:
            return error_response('Invalid JSON body', 400, 'INVALID_JSON')
        except Exception as e:
            _logger.error(f'Send notification error: {e}')
            return error_response(str(e), 500, 'NOTIFICATION_ERROR')

    @http.route('/api/line-admin/notifications/history', type='http', auth='none',
                methods=['GET', 'OPTIONS'], csrf=False)
    @require_admin
    def get_notification_history(self):
        """Get notification send history"""
        try:
            params = request.params
            page = int(params.get('page', 1))
            limit = int(params.get('limit', NOTIFICATIONS_PER_PAGE))
            offset = (page - 1) * limit

            domain = [('channel_id', '=', request.line_channel.id)]

            notify_type = params.get('type', '')
            if notify_type and notify_type != 'all':
                domain.append(('notify_type', '=', notify_type))

            NotifyLog = request.env['line.notify.log'].sudo()
            total = NotifyLog.search_count(domain)
            logs = NotifyLog.search(domain, limit=limit, offset=offset, order='create_date desc')

            return success_response({
                'notifications': [format_notify_log(log) for log in logs],
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': total,
                    'pages': (total + limit - 1) // limit if limit else 1,
                },
            })

        except Exception as e:
            _logger.error(f'Notification history error: {e}')
            return error_response(str(e), 500, 'HISTORY_ERROR')

    # ==================== Settings ====================

    @http.route('/api/line-admin/settings', type='http', auth='none',
                methods=['GET', 'OPTIONS'], csrf=False)
    @require_admin
    def get_settings(self):
        """Get admin settings (channel info, LIFF apps, notification config)"""
        try:
            channel = request.line_channel
            ICP = request.env['ir.config_parameter'].sudo()

            # Channel info
            channel_info = {
                'id': channel.id,
                'name': channel.name,
                'code': channel.code,
                'active': channel.active,
                'liff_url': channel.liff_url if hasattr(channel, 'liff_url') else '',
            }

            # LIFF apps
            liff_apps = []
            LiffApp = request.env['line.liff'].sudo()
            if LiffApp._table_exist() if hasattr(LiffApp, '_table_exist') else True:
                try:
                    apps = LiffApp.search([('channel_id', '=', channel.id)])
                    liff_apps = [{
                        'id': app.id,
                        'name': app.name,
                        'liff_id': app.liff_id if hasattr(app, 'liff_id') else '',
                        'url': app.url if hasattr(app, 'url') else '',
                        'active': app.active if hasattr(app, 'active') else True,
                    } for app in apps]
                except Exception:
                    pass

            # Notification settings from ir.config_parameter
            settings = {
                'auto_notify_new_order': ICP.get_param(
                    'core_line_integration.auto_notify_new_order', 'True') == 'True',
                'auto_notify_shipping': ICP.get_param(
                    'core_line_integration.auto_notify_shipping', 'True') == 'True',
                'mock_auth': ICP.get_param(
                    'core_line_integration.mock_auth', 'True') == 'True',
            }

            return success_response({
                'channel': channel_info,
                'liff_apps': liff_apps,
                'settings': settings,
            })

        except Exception as e:
            _logger.error(f'Admin settings error: {e}')
            return error_response(str(e), 500, 'SETTINGS_ERROR')

    @http.route('/api/line-admin/settings', type='http', auth='none',
                methods=['PUT', 'OPTIONS'], csrf=False)
    @require_admin
    def update_settings(self):
        """Update notification settings"""
        try:
            body = json.loads(request.httprequest.data or '{}')
            ICP = request.env['ir.config_parameter'].sudo()

            updated = []

            if 'auto_notify_new_order' in body:
                ICP.set_param(
                    'core_line_integration.auto_notify_new_order',
                    'True' if body['auto_notify_new_order'] else 'False'
                )
                updated.append('auto_notify_new_order')

            if 'auto_notify_shipping' in body:
                ICP.set_param(
                    'core_line_integration.auto_notify_shipping',
                    'True' if body['auto_notify_shipping'] else 'False'
                )
                updated.append('auto_notify_shipping')

            _logger.info(f'Admin {request.admin_user.name} updated settings: {updated}')

            return success_response({
                'updated': updated,
            }, message='Settings updated successfully')

        except json.JSONDecodeError:
            return error_response('Invalid JSON body', 400, 'INVALID_JSON')
        except Exception as e:
            _logger.error(f'Update settings error: {e}')
            return error_response(str(e), 500, 'SETTINGS_ERROR')
