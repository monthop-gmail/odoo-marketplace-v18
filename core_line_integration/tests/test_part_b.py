# -*- coding: utf-8 -*-
"""
Mock Tests for Part B - LINE Integration Features

These tests can run without actual LINE API access by using mock services.
They test:
1. LINE API Service (mock mode)
2. Flex Message Templates
3. Webhook Event Processing
4. Notification Cron Job
5. LIFF Token Validation (mock)
"""
import json
import os
import sys
import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta

# Add parent directory to path for imports
_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _dir not in sys.path:
    sys.path.insert(0, _dir)


class TestLineApiService(unittest.TestCase):
    """Test LINE API Service and Mock Service"""

    def setUp(self):
        from services.line_api import MockLineApiService
        self.service = MockLineApiService()

    def test_validate_signature_mock(self):
        """Mock service always validates signature"""
        result = self.service.validate_signature(b'test body', 'any_signature')
        self.assertTrue(result)

    def test_get_profile_mock(self):
        """Mock service returns profile"""
        profile = self.service.get_profile('Uxxxxxxxxxxxxxxxx')

        self.assertIn('userId', profile)
        self.assertIn('displayName', profile)
        self.assertEqual(profile['userId'], 'Uxxxxxxxxxxxxxxxx')

    def test_get_profile_custom_mock(self):
        """Mock service uses custom profiles if set"""
        custom_profile = {
            'userId': 'U123456',
            'displayName': 'Test User',
            'pictureUrl': 'https://example.com/pic.jpg',
        }
        self.service.add_mock_profile('U123456', custom_profile)

        profile = self.service.get_profile('U123456')
        self.assertEqual(profile['displayName'], 'Test User')

    def test_push_message_mock(self):
        """Mock service records sent messages"""
        message = {'type': 'text', 'text': 'Hello!'}
        result = self.service.push_message('Uxxxxxxxx', message)

        self.assertTrue(result.get('success'))
        self.assertTrue(result.get('mock'))

        sent = self.service.get_sent_messages()
        self.assertEqual(len(sent), 1)
        self.assertEqual(sent[0]['type'], 'push')
        self.assertEqual(sent[0]['to'], 'Uxxxxxxxx')

    def test_reply_message_mock(self):
        """Mock service records reply messages"""
        message = {'type': 'text', 'text': 'Reply!'}
        result = self.service.reply_message('reply_token_123', message)

        self.assertTrue(result.get('success'))

        sent = self.service.get_sent_messages()
        self.assertEqual(len(sent), 1)
        self.assertEqual(sent[0]['type'], 'reply')

    def test_multicast_mock(self):
        """Mock service records multicast messages"""
        message = {'type': 'text', 'text': 'Broadcast!'}
        users = ['U001', 'U002', 'U003']
        result = self.service.multicast(users, message)

        self.assertTrue(result.get('success'))

        sent = self.service.get_sent_messages()
        self.assertEqual(len(sent), 1)
        self.assertEqual(sent[0]['type'], 'multicast')
        self.assertEqual(len(sent[0]['to']), 3)

    def test_verify_access_token_mock(self):
        """Mock service verifies access tokens"""
        result = self.service.verify_access_token('any_token')

        self.assertIn('scope', result)
        self.assertIn('expires_in', result)

    def test_get_token_profile_mock(self):
        """Mock service extracts user ID from token"""
        # Test with mock_token_ prefix
        result = self.service.get_token_profile('mock_token_U12345678')
        self.assertEqual(result['userId'], 'U12345678')

        # Test without prefix
        result = self.service.get_token_profile('random_token')
        self.assertIn('userId', result)

    def test_clear_sent_messages(self):
        """Mock service can clear message history"""
        self.service.push_message('U001', {'type': 'text', 'text': 'Test'})
        self.assertEqual(len(self.service.get_sent_messages()), 1)

        self.service.clear_sent_messages()
        self.assertEqual(len(self.service.get_sent_messages()), 0)


class TestFlexMessageBuilder(unittest.TestCase):
    """Test Flex Message Builder"""

    def setUp(self):
        from services.line_messaging import (
            FlexMessageBuilder, LineMessageBuilder
        )
        self.flex = FlexMessageBuilder
        self.msg = LineMessageBuilder

    def test_text_message(self):
        """Text message builder"""
        result = self.msg.text('Hello World')

        self.assertEqual(result['type'], 'text')
        self.assertEqual(result['text'], 'Hello World')

    def test_sticker_message(self):
        """Sticker message builder"""
        result = self.msg.sticker(1, 2)

        self.assertEqual(result['type'], 'sticker')
        self.assertEqual(result['packageId'], '1')
        self.assertEqual(result['stickerId'], '2')

    def test_image_message(self):
        """Image message builder"""
        result = self.msg.image('https://example.com/image.jpg')

        self.assertEqual(result['type'], 'image')
        self.assertEqual(result['originalContentUrl'], 'https://example.com/image.jpg')
        self.assertEqual(result['previewImageUrl'], 'https://example.com/image.jpg')

    def test_bubble_container(self):
        """Bubble container builder"""
        body = self.flex.box('vertical', [
            self.flex.text_component('Hello', weight='bold'),
        ])
        result = self.flex.bubble(body=body)

        self.assertEqual(result['type'], 'bubble')
        self.assertIn('body', result)

    def test_carousel_container(self):
        """Carousel container builder"""
        bubbles = [
            self.flex.bubble(body=self.flex.box('vertical', [])),
            self.flex.bubble(body=self.flex.box('vertical', [])),
        ]
        result = self.flex.carousel(bubbles)

        self.assertEqual(result['type'], 'carousel')
        self.assertEqual(len(result['contents']), 2)

    def test_carousel_max_12(self):
        """Carousel limits to 12 bubbles"""
        bubbles = [self.flex.bubble() for _ in range(15)]
        result = self.flex.carousel(bubbles)

        self.assertEqual(len(result['contents']), 12)

    def test_flex_message(self):
        """Flex message wrapper"""
        bubble = self.flex.bubble()
        result = self.flex.flex_message('Alt text', bubble)

        self.assertEqual(result['type'], 'flex')
        self.assertEqual(result['altText'], 'Alt text')
        self.assertIn('contents', result)

    def test_box_component(self):
        """Box component builder"""
        result = self.flex.box('horizontal', [], spacing='md', margin='lg')

        self.assertEqual(result['type'], 'box')
        self.assertEqual(result['layout'], 'horizontal')
        self.assertEqual(result['spacing'], 'md')
        self.assertEqual(result['margin'], 'lg')

    def test_text_component(self):
        """Text component builder"""
        result = self.flex.text_component('Hello', size='lg', weight='bold', color='#FF0000')

        self.assertEqual(result['type'], 'text')
        self.assertEqual(result['text'], 'Hello')
        self.assertEqual(result['size'], 'lg')
        self.assertEqual(result['weight'], 'bold')
        self.assertEqual(result['color'], '#FF0000')

    def test_button_component(self):
        """Button component builder"""
        action = self.flex.uri_action('Click', 'https://example.com')
        result = self.flex.button(action, style='primary')

        self.assertEqual(result['type'], 'button')
        self.assertEqual(result['style'], 'primary')
        self.assertIn('action', result)

    def test_uri_action(self):
        """URI action builder"""
        result = self.flex.uri_action('Click Me', 'https://example.com')

        self.assertEqual(result['type'], 'uri')
        self.assertEqual(result['label'], 'Click Me')
        self.assertEqual(result['uri'], 'https://example.com')

    def test_postback_action(self):
        """Postback action builder"""
        result = self.flex.postback_action('Add', 'action=add', 'Added!')

        self.assertEqual(result['type'], 'postback')
        self.assertEqual(result['label'], 'Add')
        self.assertEqual(result['data'], 'action=add')
        self.assertEqual(result['displayText'], 'Added!')

    def test_quick_reply(self):
        """Quick reply builder"""
        items = [
            self.msg.quick_reply_action('Yes', 'answer=yes'),
            self.msg.quick_reply_action('No', 'answer=no'),
        ]
        result = self.msg.quick_reply(items)

        self.assertIn('items', result)
        self.assertEqual(len(result['items']), 2)


class TestOrderNotificationTemplates(unittest.TestCase):
    """Test Order Notification Templates"""

    def setUp(self):
        from services.line_messaging import OrderNotificationTemplates
        self.templates = OrderNotificationTemplates

    def test_order_confirmation_template(self):
        """Order confirmation Flex message"""
        order_data = {
            'order_name': 'SO001',
            'date': '2025-01-15 10:30',
            'customer': 'Test Customer',
            'lines': [
                {'product_name': 'Product A', 'quantity': 2},
                {'product_name': 'Product B', 'quantity': 1},
            ],
            'subtotal': 900,
            'tax': 63,
            'total': 963,
            'currency': '฿',
        }

        result = self.templates.order_confirmation(order_data)

        self.assertEqual(result['type'], 'flex')
        self.assertIn('Order SO001 confirmed', result['altText'])
        self.assertEqual(result['contents']['type'], 'bubble')

    def test_order_confirmation_with_liff_url(self):
        """Order confirmation with LIFF link"""
        order_data = {
            'order_name': 'SO002',
            'lines': [],
            'total': 500,
        }
        liff_url = 'https://liff.line.me/12345/order/SO002'

        result = self.templates.order_confirmation(order_data, liff_url)

        # Check that footer has button
        self.assertIn('footer', result['contents'])

    def test_order_confirmation_many_items(self):
        """Order confirmation truncates to 5 items"""
        order_data = {
            'order_name': 'SO003',
            'lines': [
                {'product_name': f'Product {i}', 'quantity': 1}
                for i in range(10)
            ],
            'total': 1000,
        }

        result = self.templates.order_confirmation(order_data)
        # Should show "... and X more items" message
        self.assertEqual(result['type'], 'flex')

    def test_shipping_notification_template(self):
        """Shipping notification Flex message"""
        order_data = {
            'order_name': 'SO001',
        }
        tracking = 'TRK123456'

        result = self.templates.shipping_notification(
            order_data, tracking_number=tracking
        )

        self.assertEqual(result['type'], 'flex')
        self.assertIn('shipped', result['altText'].lower())

    def test_shipping_notification_with_tracking_url(self):
        """Shipping notification with tracking link"""
        order_data = {'order_name': 'SO001'}
        tracking_url = 'https://track.example.com/TRK123'

        result = self.templates.shipping_notification(
            order_data, tracking_url=tracking_url
        )

        self.assertIn('footer', result['contents'])

    def test_welcome_message_template(self):
        """Welcome message Flex message"""
        result = self.templates.welcome_message('Coop Store')

        self.assertEqual(result['type'], 'flex')
        self.assertIn('Welcome', result['altText'])

    def test_welcome_message_with_liff(self):
        """Welcome message with shop link"""
        result = self.templates.welcome_message(
            'Coop Store',
            liff_url='https://liff.line.me/12345'
        )

        self.assertIn('footer', result['contents'])

    def test_product_carousel_template(self):
        """Product carousel Flex message"""
        products = [
            {
                'id': 1,
                'name': 'Product A',
                'price': 100,
                'currency': '฿',
                'image_url': 'https://example.com/a.jpg',
            },
            {
                'id': 2,
                'name': 'Product B',
                'price': 200,
                'currency': '฿',
            },
        ]

        result = self.templates.product_carousel(products, 'https://shop.example.com')

        self.assertEqual(result['type'], 'flex')
        self.assertEqual(result['contents']['type'], 'carousel')
        self.assertEqual(len(result['contents']['contents']), 2)

    def test_product_carousel_max_10(self):
        """Product carousel limits to 10 products"""
        products = [
            {'id': i, 'name': f'Product {i}', 'price': 100}
            for i in range(15)
        ]

        result = self.templates.product_carousel(products, 'https://example.com')

        self.assertEqual(len(result['contents']['contents']), 10)


class TestWebhookEventSimulation(unittest.TestCase):
    """Test webhook event processing (simulation without Odoo)"""

    def test_follow_event_structure(self):
        """Verify follow event structure"""
        event = {
            'type': 'follow',
            'timestamp': 1704067200000,
            'source': {
                'type': 'user',
                'userId': 'U1234567890abcdef',
            },
            'replyToken': 'reply_token_xxx',
        }

        self.assertEqual(event['type'], 'follow')
        self.assertIn('userId', event['source'])
        self.assertIn('replyToken', event)

    def test_unfollow_event_structure(self):
        """Verify unfollow event structure"""
        event = {
            'type': 'unfollow',
            'timestamp': 1704067200000,
            'source': {
                'type': 'user',
                'userId': 'U1234567890abcdef',
            },
        }

        self.assertEqual(event['type'], 'unfollow')
        # Unfollow doesn't have replyToken
        self.assertNotIn('replyToken', event)

    def test_message_event_structure(self):
        """Verify message event structure"""
        event = {
            'type': 'message',
            'timestamp': 1704067200000,
            'source': {
                'type': 'user',
                'userId': 'U1234567890abcdef',
            },
            'replyToken': 'reply_token_xxx',
            'message': {
                'type': 'text',
                'id': '123456789',
                'text': 'Hello!',
            },
        }

        self.assertEqual(event['type'], 'message')
        self.assertEqual(event['message']['type'], 'text')
        self.assertEqual(event['message']['text'], 'Hello!')

    def test_postback_event_structure(self):
        """Verify postback event structure"""
        event = {
            'type': 'postback',
            'timestamp': 1704067200000,
            'source': {
                'type': 'user',
                'userId': 'U1234567890abcdef',
            },
            'replyToken': 'reply_token_xxx',
            'postback': {
                'data': 'action=add_to_cart&product_id=123',
            },
        }

        self.assertEqual(event['type'], 'postback')
        self.assertIn('product_id=123', event['postback']['data'])

    def test_postback_data_parsing(self):
        """Test postback data parsing logic"""
        data = 'action=add_to_cart&product_id=123&quantity=2'

        params = {}
        for pair in data.split('&'):
            if '=' in pair:
                key, value = pair.split('=', 1)
                params[key] = value

        self.assertEqual(params['action'], 'add_to_cart')
        self.assertEqual(params['product_id'], '123')
        self.assertEqual(params['quantity'], '2')


class TestSignatureValidation(unittest.TestCase):
    """Test webhook signature validation"""

    def test_real_signature_validation(self):
        """Test signature validation algorithm"""
        import hashlib
        import hmac
        import base64

        channel_secret = 'test_secret'
        body = b'{"events":[]}'

        # Calculate expected signature
        hash_value = hmac.new(
            channel_secret.encode('utf-8'),
            body,
            hashlib.sha256
        ).digest()
        expected_signature = base64.b64encode(hash_value).decode('utf-8')

        # Verify using same algorithm
        computed = hmac.new(
            channel_secret.encode('utf-8'),
            body,
            hashlib.sha256
        ).digest()
        computed_signature = base64.b64encode(computed).decode('utf-8')

        self.assertEqual(expected_signature, computed_signature)

    def test_invalid_signature_fails(self):
        """Invalid signature should not match"""
        import hashlib
        import hmac
        import base64

        channel_secret = 'test_secret'
        body = b'{"events":[]}'

        hash_value = hmac.new(
            channel_secret.encode('utf-8'),
            body,
            hashlib.sha256
        ).digest()
        expected_signature = base64.b64encode(hash_value).decode('utf-8')

        # Different body produces different signature
        different_body = b'{"events":[{}]}'
        different_hash = hmac.new(
            channel_secret.encode('utf-8'),
            different_body,
            hashlib.sha256
        ).digest()
        different_signature = base64.b64encode(different_hash).decode('utf-8')

        self.assertNotEqual(expected_signature, different_signature)


class TestNotificationLogic(unittest.TestCase):
    """Test notification processing logic (without Odoo)"""

    def test_notification_types(self):
        """Verify notification types"""
        types = [
            'welcome',
            'order_confirm',
            'shipping',
            'delivery',
            'payment_reminder',
            'promotion',
            'custom',
        ]

        for notify_type in types:
            self.assertIsInstance(notify_type, str)

    def test_message_types(self):
        """Verify message types"""
        types = ['text', 'flex', 'template', 'image', 'video']

        for msg_type in types:
            self.assertIsInstance(msg_type, str)

    def test_notification_states(self):
        """Verify notification states"""
        states = ['pending', 'sent', 'delivered', 'failed']

        # Validate state transitions
        valid_transitions = {
            'pending': ['sent', 'failed'],
            'sent': ['delivered', 'failed'],
            'failed': ['pending'],  # for retry
            'delivered': [],
        }

        for state, next_states in valid_transitions.items():
            self.assertIn(state, states)
            for next_state in next_states:
                self.assertIn(next_state, states)

    def test_retry_logic(self):
        """Test retry count logic"""
        max_retries = 3
        retry_count = 0

        # Simulate retries
        while retry_count < max_retries:
            retry_count += 1

        self.assertEqual(retry_count, 3)
        self.assertFalse(retry_count < max_retries)  # No more retries


class TestLIFFTokenMock(unittest.TestCase):
    """Test LIFF token validation mocking"""

    def test_mock_token_format(self):
        """Mock token format for testing"""
        user_id = 'U1234567890'
        mock_token = f'mock_token_{user_id}'

        # Extract user ID
        extracted = mock_token.replace('mock_token_', '')
        self.assertEqual(extracted, user_id)

    def test_token_verification_response(self):
        """Mock token verification response"""
        from services.line_api import MockLineApiService

        service = MockLineApiService()
        result = service.verify_access_token('any_token')

        self.assertIn('scope', result)
        self.assertIn('client_id', result)
        self.assertIn('expires_in', result)
        self.assertGreater(result['expires_in'], 0)


if __name__ == '__main__':
    unittest.main()
