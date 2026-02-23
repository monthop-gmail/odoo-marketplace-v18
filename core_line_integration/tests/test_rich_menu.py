# -*- coding: utf-8 -*-
"""
Tests for LINE Rich Menu
"""
from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError


class TestLineRichMenu(TransactionCase):
    """Test cases for line.rich.menu model"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create test channel
        cls.channel = cls.env['line.channel'].create({
            'name': 'Test Channel',
            'code': 'test_rich_menu',
            'channel_id': 'test789',
            'channel_secret': 'secret789',
            'channel_access_token': 'token789',
        })

        # Create LIFF for testing
        cls.liff = cls.env['line.liff'].create({
            'name': 'Test LIFF',
            'liff_id': 'test-liff-id',
            'liff_type': 'buyer',
            'channel_id': cls.channel.id,
        })

    def test_01_create_rich_menu(self):
        """Test creating a rich menu"""
        rich_menu = self.env['line.rich.menu'].create({
            'name': 'Test Rich Menu',
            'channel_id': self.channel.id,
            'chat_bar_text': 'Menu',
        })

        self.assertTrue(rich_menu.exists())
        self.assertEqual(rich_menu.state, 'draft')
        self.assertEqual(rich_menu.size, 'full')

    def test_02_compute_dimensions_full(self):
        """Test dimension computation for full size"""
        rich_menu = self.env['line.rich.menu'].create({
            'name': 'Full Menu',
            'channel_id': self.channel.id,
            'size': 'full',
        })

        self.assertEqual(rich_menu.width, 2500)
        self.assertEqual(rich_menu.height, 1686)

    def test_03_compute_dimensions_half(self):
        """Test dimension computation for half size"""
        rich_menu = self.env['line.rich.menu'].create({
            'name': 'Half Menu',
            'channel_id': self.channel.id,
            'size': 'half',
        })

        self.assertEqual(rich_menu.width, 2500)
        self.assertEqual(rich_menu.height, 843)

    def test_04_create_rich_menu_area(self):
        """Test creating rich menu areas"""
        rich_menu = self.env['line.rich.menu'].create({
            'name': 'Menu with Areas',
            'channel_id': self.channel.id,
        })

        area = self.env['line.rich.menu.area'].create({
            'rich_menu_id': rich_menu.id,
            'name': 'Button 1',
            'x': 0,
            'y': 0,
            'area_width': 833,
            'area_height': 843,
            'action_type': 'uri',
            'action_uri': 'https://example.com',
        })

        self.assertTrue(area.exists())
        self.assertEqual(len(rich_menu.area_ids), 1)

    def test_05_build_uri_action(self):
        """Test building URI action"""
        rich_menu = self.env['line.rich.menu'].create({
            'name': 'URI Menu',
            'channel_id': self.channel.id,
        })

        area = self.env['line.rich.menu.area'].create({
            'rich_menu_id': rich_menu.id,
            'name': 'Link Button',
            'x': 0,
            'y': 0,
            'area_width': 833,
            'area_height': 843,
            'action_type': 'uri',
            'action_uri': 'https://example.com/page',
        })

        action = area._build_action()

        self.assertEqual(action['type'], 'uri')
        self.assertEqual(action['uri'], 'https://example.com/page')

    def test_06_build_message_action(self):
        """Test building message action"""
        rich_menu = self.env['line.rich.menu'].create({
            'name': 'Message Menu',
            'channel_id': self.channel.id,
        })

        area = self.env['line.rich.menu.area'].create({
            'rich_menu_id': rich_menu.id,
            'name': 'Message Button',
            'x': 0,
            'y': 0,
            'area_width': 833,
            'area_height': 843,
            'action_type': 'message',
            'action_text': 'Hello!',
        })

        action = area._build_action()

        self.assertEqual(action['type'], 'message')
        self.assertEqual(action['text'], 'Hello!')

    def test_07_build_postback_action(self):
        """Test building postback action"""
        rich_menu = self.env['line.rich.menu'].create({
            'name': 'Postback Menu',
            'channel_id': self.channel.id,
        })

        area = self.env['line.rich.menu.area'].create({
            'rich_menu_id': rich_menu.id,
            'name': 'Postback Button',
            'x': 0,
            'y': 0,
            'area_width': 833,
            'area_height': 843,
            'action_type': 'postback',
            'action_data': 'action=buy&itemid=123',
            'action_display_text': 'Buy Item',
        })

        action = area._build_action()

        self.assertEqual(action['type'], 'postback')
        self.assertEqual(action['data'], 'action=buy&itemid=123')
        self.assertEqual(action['displayText'], 'Buy Item')

    def test_08_build_liff_action(self):
        """Test building LIFF action"""
        rich_menu = self.env['line.rich.menu'].create({
            'name': 'LIFF Menu',
            'channel_id': self.channel.id,
        })

        area = self.env['line.rich.menu.area'].create({
            'rich_menu_id': rich_menu.id,
            'name': 'LIFF Button',
            'x': 0,
            'y': 0,
            'area_width': 833,
            'area_height': 843,
            'action_type': 'liff',
            'liff_id': self.liff.id,
        })

        action = area._build_action()

        self.assertEqual(action['type'], 'uri')
        self.assertIn('liff.line.me', action['uri'])
        self.assertIn('test-liff-id', action['uri'])

    def test_09_build_rich_menu_object(self):
        """Test building rich menu object for LINE API"""
        rich_menu = self.env['line.rich.menu'].create({
            'name': 'API Menu',
            'channel_id': self.channel.id,
            'chat_bar_text': 'Open Menu',
            'selected': True,
        })

        self.env['line.rich.menu.area'].create({
            'rich_menu_id': rich_menu.id,
            'name': 'Button',
            'x': 0,
            'y': 0,
            'area_width': 2500,
            'area_height': 1686,
            'action_type': 'message',
            'action_text': 'Test',
        })

        menu_obj = rich_menu._build_rich_menu_object()

        self.assertEqual(menu_obj['name'], 'API Menu')
        self.assertEqual(menu_obj['chatBarText'], 'Open Menu')
        self.assertTrue(menu_obj['selected'])
        self.assertEqual(menu_obj['size']['width'], 2500)
        self.assertEqual(menu_obj['size']['height'], 1686)
        self.assertEqual(len(menu_obj['areas']), 1)

    def test_10_action_create_on_line_no_image(self):
        """Test create on LINE fails without image"""
        rich_menu = self.env['line.rich.menu'].create({
            'name': 'No Image Menu',
            'channel_id': self.channel.id,
        })

        self.env['line.rich.menu.area'].create({
            'rich_menu_id': rich_menu.id,
            'name': 'Button',
            'x': 0,
            'y': 0,
            'area_width': 833,
            'area_height': 843,
            'action_type': 'message',
            'action_text': 'Test',
        })

        with self.assertRaises(UserError) as context:
            rich_menu.action_create_on_line()

        self.assertIn('image', str(context.exception).lower())

    def test_11_action_create_on_line_no_areas(self):
        """Test create on LINE fails without areas"""
        rich_menu = self.env['line.rich.menu'].create({
            'name': 'No Areas Menu',
            'channel_id': self.channel.id,
            'image': 'dGVzdA==',  # Base64 'test'
        })

        with self.assertRaises(UserError) as context:
            rich_menu.action_create_on_line()

        self.assertIn('area', str(context.exception).lower())

    def test_12_default_values(self):
        """Test default values"""
        rich_menu = self.env['line.rich.menu'].create({
            'name': 'Default Menu',
            'channel_id': self.channel.id,
        })

        self.assertEqual(rich_menu.state, 'draft')
        self.assertEqual(rich_menu.size, 'full')
        self.assertEqual(rich_menu.chat_bar_text, 'Menu')
        self.assertTrue(rich_menu.selected)
        self.assertTrue(rich_menu.active)

    def test_13_area_default_values(self):
        """Test area default values"""
        rich_menu = self.env['line.rich.menu'].create({
            'name': 'Area Test Menu',
            'channel_id': self.channel.id,
        })

        area = self.env['line.rich.menu.area'].create({
            'rich_menu_id': rich_menu.id,
            'name': 'Test Area',
            'action_type': 'message',
            'action_text': 'Test',
        })

        self.assertEqual(area.x, 0)
        self.assertEqual(area.y, 0)
        self.assertEqual(area.area_width, 833)
        self.assertEqual(area.area_height, 843)
        self.assertEqual(area.sequence, 10)
