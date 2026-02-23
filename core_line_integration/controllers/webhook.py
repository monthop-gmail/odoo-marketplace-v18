# -*- coding: utf-8 -*-
"""
LINE Webhook Controller - handles incoming events from LINE Platform
"""
import json
import logging

from odoo import http
from odoo.http import request, Response

from .main import json_response, error_response, success_response

_logger = logging.getLogger(__name__)


class LineWebhookController(http.Controller):
    """
    LINE Webhook Controller

    Handles webhook events from LINE Platform:
    - follow: User added bot as friend
    - unfollow: User blocked or deleted bot
    - message: User sent a message
    - postback: User clicked a postback button
    - join/leave: Bot joined/left group or room
    """

    def _get_line_service(self, channel):
        """Get LINE API service for the channel"""
        mock_mode = request.env['ir.config_parameter'].sudo().get_param(
            'core_line_integration.mock_auth', 'True'
        ) == 'True'

        if mock_mode:
            from ..services.line_api import MockLineApiService
            return MockLineApiService()
        else:
            from ..services.line_api import LineApiService
            return LineApiService(
                channel.channel_access_token,
                channel.channel_secret
            )

    def _validate_signature(self, channel):
        """
        Validate webhook signature from LINE

        Returns:
            bool: True if signature is valid
        """
        signature = request.httprequest.headers.get('X-Line-Signature')
        if not signature:
            _logger.warning('Missing X-Line-Signature header')
            return False

        body = request.httprequest.data
        line_service = self._get_line_service(channel)

        return line_service.validate_signature(body, signature)

    @http.route('/api/line-buyer/webhook/<string:channel_code>',
                type='http', auth='none', methods=['POST'], csrf=False)
    def webhook_handler(self, channel_code, **kwargs):
        """
        Main webhook endpoint for LINE events

        URL: /api/line-buyer/webhook/<channel_code>

        This endpoint should be registered in LINE Developer Console
        as the webhook URL for your LINE Channel.
        """
        try:
            # Get channel
            channel = request.env['line.channel'].sudo().search([
                ('code', '=', channel_code),
                ('active', '=', True),
            ], limit=1)

            if not channel:
                _logger.error(f'Webhook received for unknown channel: {channel_code}')
                return error_response('Channel not found', 404)

            # Validate signature (skip in mock mode)
            mock_mode = request.env['ir.config_parameter'].sudo().get_param(
                'core_line_integration.mock_auth', 'True'
            ) == 'True'

            if not mock_mode:
                if not self._validate_signature(channel):
                    _logger.warning(f'Invalid webhook signature for channel: {channel_code}')
                    return error_response('Invalid signature', 401)

            # Parse request body
            try:
                body = json.loads(request.httprequest.data.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                _logger.error(f'Failed to parse webhook body: {e}')
                return error_response('Invalid JSON', 400)

            # Process events
            events = body.get('events', [])
            _logger.info(f'Webhook received {len(events)} events for channel {channel_code}')

            for event in events:
                try:
                    self._process_event(channel, event)
                except Exception as e:
                    _logger.error(f'Error processing webhook event: {e}', exc_info=True)
                    # Continue processing other events

            # LINE expects 200 OK response
            return json_response({'status': 'ok'}, 200)

        except Exception as e:
            _logger.error(f'Webhook error: {e}', exc_info=True)
            # Still return 200 to avoid LINE retrying
            return json_response({'status': 'error', 'message': str(e)}, 200)

    def _process_event(self, channel, event):
        """
        Process a single webhook event

        Args:
            channel: line.channel record
            event: Event dict from LINE webhook
        """
        event_type = event.get('type')
        source = event.get('source', {})
        user_id = source.get('userId')
        timestamp = event.get('timestamp')
        reply_token = event.get('replyToken')

        _logger.info(f'Processing {event_type} event from user {user_id}')

        # Route to appropriate handler
        handlers = {
            'follow': self._handle_follow,
            'unfollow': self._handle_unfollow,
            'message': self._handle_message,
            'postback': self._handle_postback,
            'join': self._handle_join,
            'leave': self._handle_leave,
        }

        handler = handlers.get(event_type)
        if handler:
            handler(channel, event)
        else:
            _logger.info(f'Unhandled event type: {event_type}')

    def _handle_follow(self, channel, event):
        """
        Handle follow event - user added bot as friend
        """
        source = event.get('source', {})
        user_id = source.get('userId')
        reply_token = event.get('replyToken')

        if not user_id:
            _logger.warning('Follow event without userId')
            return

        _logger.info(f'User {user_id} followed channel {channel.code}')

        # Get user profile from LINE (or mock)
        line_service = self._get_line_service(channel)
        try:
            profile = line_service.get_profile(user_id)
        except Exception as e:
            _logger.error(f'Failed to get profile for {user_id}: {e}')
            profile = {'displayName': f'User {user_id[:8]}'}

        # Use context with tracking disabled for webhook operations
        ctx = dict(
            tracking_disable=True,
            mail_create_nosubscribe=True,
            mail_auto_subscribe_no_notify=True,
        )

        # Get or create member
        member = request.env['line.channel.member'].sudo().with_context(**ctx).get_or_create_member(
            channel.id,
            user_id,
            {
                'display_name': profile.get('displayName', ''),
                'picture_url': profile.get('pictureUrl', ''),
                'status_message': profile.get('statusMessage', ''),
            }
        )

        # Update member status
        member.with_context(**ctx).write({
            'is_following': True,
            'follow_date': fields_Datetime_now(),
        })

        # Sync member_type based on partner's current role
        if member.partner_id:
            member.sync_member_type_from_partner()
            member.assign_role_rich_menu()

        # Send welcome message if reply_token exists
        if reply_token and channel.welcome_message:
            try:
                from ..services.line_messaging import LineMessageBuilder, OrderNotificationTemplates

                # Create welcome message
                if channel.liff_url:
                    welcome = OrderNotificationTemplates.welcome_message(
                        channel.name,
                        channel.liff_url
                    )
                else:
                    welcome = LineMessageBuilder.text(channel.welcome_message)

                line_service.reply_message(reply_token, [welcome])
                _logger.info(f'Welcome message sent to {user_id}')

            except Exception as e:
                _logger.error(f'Failed to send welcome message: {e}')

        # Log the notification
        request.env['line.notify.log'].sudo().with_context(**ctx).create({
            'channel_id': channel.id,
            'line_user_id': user_id,
            'partner_id': member.partner_id.id if member.partner_id else False,
            'notify_type': 'welcome',
            'message': f'User followed: {profile.get("displayName", user_id)}',
            'state': 'sent',
            'sent_date': fields_Datetime_now(),
        })

    def _handle_unfollow(self, channel, event):
        """
        Handle unfollow event - user blocked or removed bot
        """
        source = event.get('source', {})
        user_id = source.get('userId')

        if not user_id:
            return

        _logger.info(f'User {user_id} unfollowed channel {channel.code}')

        # Update member status
        ctx = dict(
            tracking_disable=True,
            mail_create_nosubscribe=True,
            mail_auto_subscribe_no_notify=True,
        )

        member = request.env['line.channel.member'].sudo().search([
            ('channel_id', '=', channel.id),
            ('line_user_id', '=', user_id),
        ], limit=1)

        if member:
            member.with_context(**ctx).write({
                'is_following': False,
                'unfollow_date': fields_Datetime_now(),
            })

    def _handle_message(self, channel, event):
        """
        Handle message event - user sent a message
        """
        source = event.get('source', {})
        user_id = source.get('userId')
        reply_token = event.get('replyToken')
        message = event.get('message', {})
        message_type = message.get('type')
        message_text = message.get('text', '')

        if not user_id:
            return

        _logger.info(f'Message from {user_id}: {message_type} - {message_text[:50] if message_text else ""}')

        # Get or create member
        ctx = dict(
            tracking_disable=True,
            mail_create_nosubscribe=True,
            mail_auto_subscribe_no_notify=True,
        )

        member = request.env['line.channel.member'].sudo().with_context(**ctx).get_or_create_member(
            channel.id,
            user_id,
            {'display_name': f'User {user_id[:8]}'}
        )

        # Handle text messages with role-aware keyword responses
        if message_type == 'text' and reply_token:
            response = self._get_keyword_response(channel, message_text.lower().strip(), member)

            if response:
                line_service = self._get_line_service(channel)
                try:
                    line_service.reply_message(reply_token, [response])
                except Exception as e:
                    _logger.error(f'Failed to reply: {e}')

    def _get_keyword_response(self, channel, message_text, member=None):
        """
        Get role-aware response for keyword messages.

        Different roles get different keyword options:
        - buyer: shop, cart, orders
        - seller: shop, orders, dashboard, products
        - admin: shop, orders, dashboard, members
        """
        from ..services.line_messaging import LineMessageBuilder

        member_type = member.member_type if member else 'buyer'

        # Get LIFF URLs by type
        liff_urls = {}
        if channel:
            liff_apps = request.env['line.liff'].sudo().search([
                ('channel_id', '=', channel.id),
                ('active', '=', True),
            ])
            for app in liff_apps:
                liff_urls[app.liff_type] = app.liff_url

        buyer_url = liff_urls.get('buyer', channel.liff_url or '')
        seller_url = liff_urls.get('seller', '')
        admin_url = liff_urls.get('admin', '')

        # Common keywords
        keywords = {
            'hello': 'สวัสดีค่ะ! 👋 พิมพ์ "help" เพื่อดูคำสั่งที่ใช้ได้',
            'hi': 'สวัสดีค่ะ! 👋 พิมพ์ "help" เพื่อดูคำสั่งที่ใช้ได้',
            'สวัสดี': 'สวัสดีค่ะ! 👋 พิมพ์ "help" เพื่อดูคำสั่งที่ใช้ได้',
        }

        if member_type == 'seller':
            keywords.update({
                'help': (
                    '🏪 คำสั่งสำหรับผู้ขาย:\n\n'
                    '• "shop" — เปิดร้านค้า\n'
                    '• "dashboard" — แดชบอร์ดผู้ขาย\n'
                    '• "products" — จัดการสินค้า\n'
                    '• "orders" — คำสั่งซื้อ'
                ),
                'shop': f'🛍️ เปิดร้านค้า: {buyer_url}' if buyer_url else 'เร็วๆ นี้!',
                'dashboard': f'📊 แดชบอร์ดผู้ขาย: {seller_url}' if seller_url else 'เร็วๆ นี้!',
                'products': f'📦 จัดการสินค้า: {seller_url}?page=products' if seller_url else 'เร็วๆ นี้!',
                'orders': f'📋 คำสั่งซื้อ: {seller_url}?page=orders' if seller_url else 'เร็วๆ นี้!',
                'cart': f'🛒 ตะกร้าสินค้า: {buyer_url}?page=cart' if buyer_url else 'เร็วๆ นี้!',
            })
        elif member_type == 'admin':
            keywords.update({
                'help': (
                    '⚙️ คำสั่งสำหรับแอดมิน:\n\n'
                    '• "shop" — เปิดร้านค้า\n'
                    '• "dashboard" — แดชบอร์ดแอดมิน\n'
                    '• "members" — จัดการสมาชิก\n'
                    '• "orders" — คำสั่งซื้อ\n'
                    '• "sellers" — จัดการผู้ขาย'
                ),
                'shop': f'🛍️ เปิดร้านค้า: {buyer_url}' if buyer_url else 'เร็วๆ นี้!',
                'dashboard': f'📊 แดชบอร์ดแอดมิน: {admin_url}' if admin_url else 'เร็วๆ นี้!',
                'members': f'👥 จัดการสมาชิก: {admin_url}?page=members' if admin_url else 'เร็วๆ นี้!',
                'sellers': f'🏪 จัดการผู้ขาย: {admin_url}?page=sellers' if admin_url else 'เร็วๆ นี้!',
                'orders': f'📋 คำสั่งซื้อ: {admin_url}?page=orders' if admin_url else 'เร็วๆ นี้!',
                'cart': f'🛒 ตะกร้าสินค้า: {buyer_url}?page=cart' if buyer_url else 'เร็วๆ นี้!',
            })
        else:
            # buyer (default)
            keywords.update({
                'help': (
                    '🛍️ คำสั่งที่ใช้ได้:\n\n'
                    '• "shop" — เปิดร้านค้า\n'
                    '• "cart" — ตะกร้าสินค้า\n'
                    '• "orders" — คำสั่งซื้อของฉัน'
                ),
                'shop': f'🛍️ เปิดร้านค้า: {buyer_url}' if buyer_url else 'เร็วๆ นี้!',
                'cart': f'🛒 ตะกร้าสินค้า: {buyer_url}?page=cart' if buyer_url else 'เร็วๆ นี้!',
                'orders': f'📋 คำสั่งซื้อ: {buyer_url}?page=orders' if buyer_url else 'เร็วๆ นี้!',
            })

        response_text = keywords.get(message_text)
        if response_text:
            return LineMessageBuilder.text(response_text)

        return None

    def _handle_postback(self, channel, event):
        """
        Handle postback event - user clicked a postback button
        """
        source = event.get('source', {})
        user_id = source.get('userId')
        reply_token = event.get('replyToken')
        postback = event.get('postback', {})
        data = postback.get('data', '')

        if not user_id or not data:
            return

        _logger.info(f'Postback from {user_id}: {data}')

        # Parse postback data (format: action=xxx&param1=yyy&param2=zzz)
        params = {}
        for pair in data.split('&'):
            if '=' in pair:
                key, value = pair.split('=', 1)
                params[key] = value

        action = params.get('action')

        # Handle different actions
        if action == 'add_to_cart':
            self._handle_add_to_cart_postback(channel, user_id, params, reply_token)
        elif action == 'view_order':
            self._handle_view_order_postback(channel, user_id, params, reply_token)
        else:
            _logger.info(f'Unhandled postback action: {action}')

    def _handle_add_to_cart_postback(self, channel, user_id, params, reply_token):
        """Handle add to cart postback"""
        from ..services.line_messaging import LineMessageBuilder

        product_id = params.get('product_id')
        if not product_id:
            return

        ctx = dict(
            tracking_disable=True,
            mail_create_nosubscribe=True,
            mail_auto_subscribe_no_notify=True,
        )

        # Get member and partner
        member = request.env['line.channel.member'].sudo().search([
            ('channel_id', '=', channel.id),
            ('line_user_id', '=', user_id),
        ], limit=1)

        if not member or not member.partner_id:
            _logger.warning(f'Member or partner not found for add_to_cart: {user_id}')
            return

        # Get product
        product = request.env['product.product'].sudo().browse(int(product_id))
        if not product.exists() or not product.sale_ok:
            return

        # Get or create cart
        SaleOrder = request.env['sale.order'].sudo().with_context(**ctx)
        cart = SaleOrder.search([
            ('partner_id', '=', member.partner_id.id),
            ('state', '=', 'draft'),
            ('source_channel', '=', 'line'),
        ], limit=1, order='create_date desc')

        if not cart:
            default_user = request.env.ref('base.user_admin', raise_if_not_found=False)
            default_company = request.env['res.company'].sudo().search([], limit=1)

            cart = SaleOrder.create({
                'partner_id': member.partner_id.id,
                'user_id': default_user.id if default_user else False,
                'company_id': default_company.id if default_company else False,
                'source_channel': 'line',
                'source_line_channel_id': channel.id,
            })

        # Add product to cart
        existing_line = cart.order_line.filtered(lambda l: l.product_id.id == product.id)
        if existing_line:
            existing_line.with_context(**ctx).product_uom_qty += 1
        else:
            request.env['sale.order.line'].sudo().with_context(**ctx).create({
                'order_id': cart.id,
                'product_id': product.id,
                'product_uom_qty': 1,
            })

        # Reply confirmation
        if reply_token:
            line_service = self._get_line_service(channel)
            try:
                message = LineMessageBuilder.text(
                    f'✓ Added "{product.name}" to your cart.\n\n'
                    f'Cart total: {len(cart.order_line)} items'
                )
                line_service.reply_message(reply_token, [message])
            except Exception as e:
                _logger.error(f'Failed to reply add_to_cart: {e}')

    def _handle_view_order_postback(self, channel, user_id, params, reply_token):
        """Handle view order postback"""
        from ..services.line_messaging import LineMessageBuilder, OrderNotificationTemplates

        order_id = params.get('order_id')
        if not order_id:
            return

        # Get order
        order = request.env['sale.order'].sudo().browse(int(order_id))
        if not order.exists():
            return

        # Send order details
        if reply_token:
            line_service = self._get_line_service(channel)
            try:
                order_data = order.get_line_order_summary()
                order_data['currency'] = order.currency_id.symbol

                message = OrderNotificationTemplates.order_confirmation(
                    order_data,
                    f'{channel.liff_url}?page=order&id={order_id}' if channel.liff_url else None
                )
                line_service.reply_message(reply_token, [message])
            except Exception as e:
                _logger.error(f'Failed to reply view_order: {e}')

    def _handle_join(self, channel, event):
        """Handle join event - bot joined a group or room"""
        source = event.get('source', {})
        source_type = source.get('type')
        group_id = source.get('groupId') or source.get('roomId')

        _logger.info(f'Bot joined {source_type}: {group_id}')

    def _handle_leave(self, channel, event):
        """Handle leave event - bot left a group or room"""
        source = event.get('source', {})
        source_type = source.get('type')
        group_id = source.get('groupId') or source.get('roomId')

        _logger.info(f'Bot left {source_type}: {group_id}')


def fields_Datetime_now():
    """Helper to get current datetime"""
    from odoo import fields
    return fields.Datetime.now()
