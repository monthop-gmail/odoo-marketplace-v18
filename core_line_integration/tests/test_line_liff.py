# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase, tagged
from odoo.exceptions import ValidationError
from unittest.mock import patch


@tagged('post_install', '-at_install', 'core_line_integration', 'line_liff')
class TestLineLiff(TransactionCase):
    """Test cases for line.liff model"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create a test LINE channel
        cls.channel = cls.env['line.channel'].create({
            'name': 'Test Channel',
            'code': 'test_channel',
            'channel_id': '1234567890',
            'channel_secret': 'test_secret',
            'channel_access_token': 'test_token',
        })

    def test_create_liff_basic(self):
        """Test basic LIFF creation"""
        liff = self.env['line.liff'].create({
            'name': 'Buyer App',
            'liff_id': '1234567890-AbCdEfGh',
            'channel_id': self.channel.id,
            'liff_type': 'buyer',
        })
        self.assertTrue(liff.id)
        self.assertEqual(liff.name, 'Buyer App')
        self.assertEqual(liff.liff_type, 'buyer')
        self.assertTrue(liff.active)

    def test_liff_url_computation(self):
        """Test LIFF URL is computed correctly"""
        liff = self.env['line.liff'].create({
            'name': 'Buyer App',
            'liff_id': '1234567890-AbCdEfGh',
            'channel_id': self.channel.id,
            'liff_type': 'buyer',
        })
        self.assertEqual(liff.liff_url, 'https://liff.line.me/1234567890-AbCdEfGh')

    def test_liff_url_format(self):
        """Test LIFF URL format is correct"""
        liff = self.env['line.liff'].create({
            'name': 'Test App',
            'liff_id': '1111111111-TestTest',
            'channel_id': self.channel.id,
            'liff_type': 'other',
        })
        # Check URL starts with liff.line.me
        self.assertTrue(liff.liff_url.startswith('https://liff.line.me/'))
        self.assertIn('1111111111-TestTest', liff.liff_url)

    def test_liff_id_unique_constraint(self):
        """Test that LIFF ID must be unique"""
        self.env['line.liff'].create({
            'name': 'First App',
            'liff_id': '1234567890-UniqueId',
            'channel_id': self.channel.id,
            'liff_type': 'buyer',
        })
        # Try to create another with same LIFF ID
        with self.assertRaises(Exception):  # IntegrityError wrapped
            self.env['line.liff'].create({
                'name': 'Second App',
                'liff_id': '1234567890-UniqueId',
                'channel_id': self.channel.id,
                'liff_type': 'seller',
            })

    def test_channel_type_unique_constraint(self):
        """Test that each channel can only have one LIFF per type"""
        self.env['line.liff'].create({
            'name': 'Buyer App 1',
            'liff_id': '1234567890-BuyerOne',
            'channel_id': self.channel.id,
            'liff_type': 'buyer',
        })
        # Try to create another buyer LIFF for same channel
        with self.assertRaises(Exception):  # IntegrityError wrapped
            self.env['line.liff'].create({
                'name': 'Buyer App 2',
                'liff_id': '1234567890-BuyerTwo',
                'channel_id': self.channel.id,
                'liff_type': 'buyer',
            })

    def test_different_types_allowed(self):
        """Test that different LIFF types can coexist on same channel"""
        buyer_liff = self.env['line.liff'].create({
            'name': 'Buyer App',
            'liff_id': '1234567890-BuyerApp',
            'channel_id': self.channel.id,
            'liff_type': 'buyer',
        })
        seller_liff = self.env['line.liff'].create({
            'name': 'Seller App',
            'liff_id': '1234567890-SellerAp',
            'channel_id': self.channel.id,
            'liff_type': 'seller',
        })
        admin_liff = self.env['line.liff'].create({
            'name': 'Admin App',
            'liff_id': '1234567890-AdminApp',
            'channel_id': self.channel.id,
            'liff_type': 'admin',
        })
        self.assertTrue(buyer_liff.id)
        self.assertTrue(seller_liff.id)
        self.assertTrue(admin_liff.id)

    def test_liff_size_default(self):
        """Test default LIFF size is 'full'"""
        liff = self.env['line.liff'].create({
            'name': 'Test App',
            'liff_id': '1234567890-SizeTest',
            'channel_id': self.channel.id,
            'liff_type': 'other',
        })
        self.assertEqual(liff.liff_size, 'full')

    def test_liff_features_default(self):
        """Test default feature flags are True"""
        liff = self.env['line.liff'].create({
            'name': 'Test App',
            'liff_id': '1234567890-Features',
            'channel_id': self.channel.id,
            'liff_type': 'buyer',
        })
        self.assertTrue(liff.feature_browse_products)
        self.assertTrue(liff.feature_cart)
        self.assertTrue(liff.feature_checkout)
        self.assertTrue(liff.feature_order_history)
        self.assertTrue(liff.feature_profile)

    def test_get_liff_by_type(self):
        """Test get_liff_by_type class method"""
        buyer_liff = self.env['line.liff'].create({
            'name': 'Buyer App',
            'liff_id': '1234567890-ByTypeB1',
            'channel_id': self.channel.id,
            'liff_type': 'buyer',
        })
        seller_liff = self.env['line.liff'].create({
            'name': 'Seller App',
            'liff_id': '1234567890-ByTypeS1',
            'channel_id': self.channel.id,
            'liff_type': 'seller',
        })

        # Get buyer LIFF
        result = self.env['line.liff'].get_liff_by_type(self.channel.id, 'buyer')
        self.assertEqual(result.id, buyer_liff.id)

        # Get seller LIFF
        result = self.env['line.liff'].get_liff_by_type(self.channel.id, 'seller')
        self.assertEqual(result.id, seller_liff.id)

        # Get non-existent type
        result = self.env['line.liff'].get_liff_by_type(self.channel.id, 'admin')
        self.assertFalse(result)

    def test_get_liff_by_type_inactive(self):
        """Test get_liff_by_type excludes inactive LIFFs"""
        liff = self.env['line.liff'].create({
            'name': 'Inactive App',
            'liff_id': '1234567890-Inactive',
            'channel_id': self.channel.id,
            'liff_type': 'promotion',
            'active': False,
        })
        result = self.env['line.liff'].get_liff_by_type(self.channel.id, 'promotion')
        self.assertFalse(result)

    def test_get_liff_config(self):
        """Test get_liff_config returns correct configuration"""
        liff = self.env['line.liff'].create({
            'name': 'Config Test',
            'liff_id': '1234567890-ConfigTe',
            'channel_id': self.channel.id,
            'liff_type': 'buyer',
            'liff_size': 'tall',
            'feature_browse_products': True,
            'feature_cart': True,
            'feature_checkout': False,
            'feature_order_history': True,
            'feature_profile': False,
        })

        config = self.env['line.liff'].get_liff_config('1234567890-ConfigTe')
        self.assertEqual(config['liff_id'], '1234567890-ConfigTe')
        self.assertEqual(config['liff_type'], 'buyer')
        self.assertEqual(config['liff_size'], 'tall')
        self.assertEqual(config['channel_code'], 'test_channel')
        self.assertTrue(config['features']['browse_products'])
        self.assertTrue(config['features']['cart'])
        self.assertFalse(config['features']['checkout'])
        self.assertTrue(config['features']['order_history'])
        self.assertFalse(config['features']['profile'])

    def test_get_liff_config_not_found(self):
        """Test get_liff_config returns error for non-existent LIFF"""
        config = self.env['line.liff'].get_liff_config('nonexistent-liff')
        self.assertIn('error', config)

    def test_log_access(self):
        """Test log_access increments counter"""
        liff = self.env['line.liff'].create({
            'name': 'Access Test',
            'liff_id': '1234567890-AccessTe',
            'channel_id': self.channel.id,
            'liff_type': 'other',
        })
        self.assertEqual(liff.access_count, 0)
        self.assertFalse(liff.last_access_date)

        liff.log_access()
        self.assertEqual(liff.access_count, 1)
        self.assertTrue(liff.last_access_date)

        liff.log_access()
        self.assertEqual(liff.access_count, 2)

    def test_action_open_liff(self):
        """Test action_open_liff returns correct action"""
        liff = self.env['line.liff'].create({
            'name': 'Open Test',
            'liff_id': '1234567890-OpenTest',
            'channel_id': self.channel.id,
            'liff_type': 'buyer',
        })
        action = liff.action_open_liff()
        self.assertEqual(action['type'], 'ir.actions.act_url')
        self.assertEqual(action['url'], 'https://liff.line.me/1234567890-OpenTest')
        self.assertEqual(action['target'], 'new')

    def test_action_open_liff_returns_action(self):
        """Test action_open_liff returns URL action"""
        liff = self.env['line.liff'].create({
            'name': 'Action Test',
            'liff_id': '1234567890-ActnTest',
            'channel_id': self.channel.id,
            'liff_type': 'other',
        })
        action = liff.action_open_liff()
        self.assertEqual(action['type'], 'ir.actions.act_url')
        self.assertIn('liff.line.me', action['url'])

    def test_channel_code_related_field(self):
        """Test channel_code is correctly stored"""
        liff = self.env['line.liff'].create({
            'name': 'Related Test',
            'liff_id': '1234567890-Related1',
            'channel_id': self.channel.id,
            'liff_type': 'buyer',
        })
        self.assertEqual(liff.channel_code, 'test_channel')

    def test_cascade_delete(self):
        """Test LIFF is deleted when channel is deleted"""
        channel = self.env['line.channel'].create({
            'name': 'Temporary Channel',
            'code': 'temp_channel',
        })
        liff = self.env['line.liff'].create({
            'name': 'Cascade Test',
            'liff_id': '1234567890-Cascade1',
            'channel_id': channel.id,
            'liff_type': 'buyer',
        })
        liff_id = liff.id
        channel.unlink()
        # LIFF should be deleted
        self.assertFalse(self.env['line.liff'].browse(liff_id).exists())
