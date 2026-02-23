# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase, tagged
from odoo.exceptions import ValidationError


@tagged('post_install', '-at_install', 'core_line_integration', 'line_channel_liff')
class TestLineChannelLiff(TransactionCase):
    """Test cases for line.channel and line.liff integration"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create test LINE channels
        cls.channel1 = cls.env['line.channel'].create({
            'name': 'Channel One',
            'code': 'channel_one',
            'channel_id': '1111111111',
        })
        cls.channel2 = cls.env['line.channel'].create({
            'name': 'Channel Two',
            'code': 'channel_two',
            'channel_id': '2222222222',
        })

    def test_channel_liff_count(self):
        """Test liff_count is computed correctly"""
        self.assertEqual(self.channel1.liff_count, 0)

        self.env['line.liff'].create({
            'name': 'Buyer App',
            'liff_id': '1111111111-Buyer001',
            'channel_id': self.channel1.id,
            'liff_type': 'buyer',
        })
        self.channel1.invalidate_recordset(['liff_count'])
        self.assertEqual(self.channel1.liff_count, 1)

        self.env['line.liff'].create({
            'name': 'Seller App',
            'liff_id': '1111111111-Seller01',
            'channel_id': self.channel1.id,
            'liff_type': 'seller',
        })
        self.channel1.invalidate_recordset(['liff_count'])
        self.assertEqual(self.channel1.liff_count, 2)

    def test_channel_liff_ids_relation(self):
        """Test liff_ids One2many relation"""
        buyer = self.env['line.liff'].create({
            'name': 'Buyer App',
            'liff_id': '1111111111-RelBuyer',
            'channel_id': self.channel1.id,
            'liff_type': 'buyer',
        })
        seller = self.env['line.liff'].create({
            'name': 'Seller App',
            'liff_id': '1111111111-RelSellr',
            'channel_id': self.channel1.id,
            'liff_type': 'seller',
        })
        self.channel1.invalidate_recordset(['liff_ids'])
        self.assertIn(buyer, self.channel1.liff_ids)
        self.assertIn(seller, self.channel1.liff_ids)

    def test_default_buyer_liff_computed(self):
        """Test default_buyer_liff_id is computed correctly"""
        self.assertFalse(self.channel1.default_buyer_liff_id)

        buyer = self.env['line.liff'].create({
            'name': 'Buyer App',
            'liff_id': '1111111111-DefBuyer',
            'channel_id': self.channel1.id,
            'liff_type': 'buyer',
        })
        self.channel1.invalidate_recordset(['default_buyer_liff_id', 'liff_ids'])
        self.assertEqual(self.channel1.default_buyer_liff_id.id, buyer.id)

    def test_default_seller_liff_computed(self):
        """Test default_seller_liff_id is computed correctly"""
        self.assertFalse(self.channel1.default_seller_liff_id)

        seller = self.env['line.liff'].create({
            'name': 'Seller App',
            'liff_id': '1111111111-DefSellr',
            'channel_id': self.channel1.id,
            'liff_type': 'seller',
        })
        self.channel1.invalidate_recordset(['default_seller_liff_id', 'liff_ids'])
        self.assertEqual(self.channel1.default_seller_liff_id.id, seller.id)

    def test_default_liff_excludes_inactive(self):
        """Test default LIFF excludes inactive LIFFs"""
        buyer = self.env['line.liff'].create({
            'name': 'Inactive Buyer',
            'liff_id': '1111111111-InacBuyr',
            'channel_id': self.channel1.id,
            'liff_type': 'buyer',
            'active': False,
        })
        self.channel1.invalidate_recordset(['default_buyer_liff_id', 'liff_ids'])
        self.assertFalse(self.channel1.default_buyer_liff_id)

    def test_get_buyer_liff_url_from_new_model(self):
        """Test get_buyer_liff_url uses new LIFF model"""
        buyer = self.env['line.liff'].create({
            'name': 'Buyer App',
            'liff_id': '1111111111-GetBuyUr',
            'channel_id': self.channel1.id,
            'liff_type': 'buyer',
        })
        self.channel1.invalidate_recordset(['default_buyer_liff_id', 'liff_ids'])
        url = self.channel1.get_buyer_liff_url()
        self.assertEqual(url, 'https://liff.line.me/1111111111-GetBuyUr')

    def test_get_buyer_liff_url_fallback_to_legacy(self):
        """Test get_buyer_liff_url falls back to legacy field"""
        # Set legacy liff_id
        self.channel1.liff_id = '9999999999-LegacyId'
        url = self.channel1.get_buyer_liff_url()
        self.assertEqual(url, 'https://liff.line.me/9999999999-LegacyId')

    def test_get_seller_liff_url(self):
        """Test get_seller_liff_url returns correct URL"""
        seller = self.env['line.liff'].create({
            'name': 'Seller App',
            'liff_id': '1111111111-GetSelUr',
            'channel_id': self.channel1.id,
            'liff_type': 'seller',
        })
        self.channel1.invalidate_recordset(['default_seller_liff_id', 'liff_ids'])
        url = self.channel1.get_seller_liff_url()
        self.assertEqual(url, 'https://liff.line.me/1111111111-GetSelUr')

    def test_get_seller_liff_url_no_seller(self):
        """Test get_seller_liff_url returns False when no seller LIFF"""
        url = self.channel1.get_seller_liff_url()
        self.assertFalse(url)

    def test_get_liff_by_type_from_channel(self):
        """Test channel's get_liff_by_type method"""
        buyer = self.env['line.liff'].create({
            'name': 'Buyer App',
            'liff_id': '1111111111-ChByType',
            'channel_id': self.channel1.id,
            'liff_type': 'buyer',
        })
        result = self.channel1.get_liff_by_type('buyer')
        self.assertEqual(result.id, buyer.id)

        result = self.channel1.get_liff_by_type('admin')
        self.assertFalse(result)

    def test_action_view_liffs(self):
        """Test action_view_liffs returns correct action"""
        action = self.channel1.action_view_liffs()
        self.assertEqual(action['type'], 'ir.actions.act_window')
        self.assertEqual(action['res_model'], 'line.liff')
        self.assertEqual(action['domain'], [('channel_id', '=', self.channel1.id)])
        self.assertEqual(action['context']['default_channel_id'], self.channel1.id)

    def test_multiple_channels_independent_liffs(self):
        """Test LIFFs are independent between channels"""
        buyer1 = self.env['line.liff'].create({
            'name': 'Channel 1 Buyer',
            'liff_id': '1111111111-Ch1Buyer',
            'channel_id': self.channel1.id,
            'liff_type': 'buyer',
        })
        buyer2 = self.env['line.liff'].create({
            'name': 'Channel 2 Buyer',
            'liff_id': '2222222222-Ch2Buyer',
            'channel_id': self.channel2.id,
            'liff_type': 'buyer',
        })

        self.channel1.invalidate_recordset(['liff_ids', 'default_buyer_liff_id'])
        self.channel2.invalidate_recordset(['liff_ids', 'default_buyer_liff_id'])

        self.assertIn(buyer1, self.channel1.liff_ids)
        self.assertNotIn(buyer2, self.channel1.liff_ids)
        self.assertIn(buyer2, self.channel2.liff_ids)
        self.assertNotIn(buyer1, self.channel2.liff_ids)

    def test_legacy_liff_url_computation(self):
        """Test legacy liff_url field still works"""
        self.channel1.liff_id = '9999999999-LegacyUr'
        self.assertEqual(self.channel1.liff_url, 'https://liff.line.me/9999999999-LegacyUr')

        self.channel1.liff_id = False
        self.assertFalse(self.channel1.liff_url)

    def test_channel_with_all_liff_types(self):
        """Test channel can have all LIFF types"""
        liff_types = ['buyer', 'seller', 'admin', 'promotion', 'support', 'other']
        liffs = {}

        for i, liff_type in enumerate(liff_types):
            liffs[liff_type] = self.env['line.liff'].create({
                'name': f'{liff_type.title()} App',
                'liff_id': f'1111111111-Type{i:04d}',
                'channel_id': self.channel1.id,
                'liff_type': liff_type,
            })

        self.channel1.invalidate_recordset(['liff_ids', 'liff_count'])
        self.assertEqual(self.channel1.liff_count, 6)

        for liff_type, liff in liffs.items():
            result = self.channel1.get_liff_by_type(liff_type)
            self.assertEqual(result.id, liff.id)


@tagged('post_install', '-at_install', 'core_line_integration', 'line_liff_api')
class TestLineLiffApi(TransactionCase):
    """Test cases for LIFF API methods"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.channel = cls.env['line.channel'].create({
            'name': 'API Test Channel',
            'code': 'api_channel',
            'channel_id': '3333333333',
        })
        cls.buyer_liff = cls.env['line.liff'].create({
            'name': 'API Buyer App',
            'liff_id': '3333333333-ApiBuyer',
            'channel_id': cls.channel.id,
            'liff_type': 'buyer',
            'liff_size': 'full',
            'feature_browse_products': True,
            'feature_cart': True,
            'feature_checkout': True,
            'feature_order_history': False,
            'feature_profile': True,
        })

    def test_get_liff_config_complete(self):
        """Test get_liff_config returns complete configuration"""
        config = self.env['line.liff'].get_liff_config('3333333333-ApiBuyer')

        self.assertEqual(config['liff_id'], '3333333333-ApiBuyer')
        self.assertEqual(config['liff_type'], 'buyer')
        self.assertEqual(config['liff_size'], 'full')
        self.assertEqual(config['channel_code'], 'api_channel')

        features = config['features']
        self.assertTrue(features['browse_products'])
        self.assertTrue(features['cart'])
        self.assertTrue(features['checkout'])
        self.assertFalse(features['order_history'])
        self.assertTrue(features['profile'])

    def test_log_access_updates_stats(self):
        """Test log_access updates statistics"""
        initial_count = self.buyer_liff.access_count
        initial_date = self.buyer_liff.last_access_date

        self.buyer_liff.log_access()

        self.assertEqual(self.buyer_liff.access_count, initial_count + 1)
        self.assertTrue(self.buyer_liff.last_access_date)
        if initial_date:
            self.assertGreaterEqual(self.buyer_liff.last_access_date, initial_date)

    def test_log_access_multiple_times(self):
        """Test log_access increments correctly with multiple calls"""
        initial_count = self.buyer_liff.access_count

        for i in range(5):
            self.buyer_liff.log_access()

        self.assertEqual(self.buyer_liff.access_count, initial_count + 5)
