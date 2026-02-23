# -*- coding: utf-8 -*-
"""
Tests for LINE Marketplace Wishlist
"""
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestLineWishlist(TransactionCase):
    """Test cases for line.wishlist model"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create test channel
        cls.channel = cls.env['line.channel'].create({
            'name': 'Test Channel',
            'code': 'test_wishlist',
            'channel_id': 'test123',
            'channel_secret': 'secret123',
            'channel_access_token': 'token123',
        })

        # Create test partner
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test Customer',
            'email': 'test@example.com',
        })

        # Create test product category
        cls.category = cls.env['product.category'].create({
            'name': 'Test Category',
        })

        # Create test products
        cls.product1 = cls.env['product.template'].create({
            'name': 'Test Product 1',
            'list_price': 100.0,
            'categ_id': cls.category.id,
            'is_published': True,
        })

        cls.product2 = cls.env['product.template'].create({
            'name': 'Test Product 2',
            'list_price': 200.0,
            'categ_id': cls.category.id,
            'is_published': True,
        })

    def test_01_create_wishlist_item(self):
        """Test creating a wishlist item"""
        wishlist = self.env['line.wishlist'].create({
            'partner_id': self.partner.id,
            'product_id': self.product1.id,
            'channel_id': self.channel.id,
        })

        self.assertTrue(wishlist.exists())
        self.assertEqual(wishlist.partner_id, self.partner)
        self.assertEqual(wishlist.product_id, self.product1)
        self.assertEqual(wishlist.product_price, 100.0)

    def test_02_unique_partner_product(self):
        """Test that same product cannot be added twice for same partner"""
        self.env['line.wishlist'].create({
            'partner_id': self.partner.id,
            'product_id': self.product1.id,
        })

        with self.assertRaises(Exception):
            self.env['line.wishlist'].create({
                'partner_id': self.partner.id,
                'product_id': self.product1.id,
            })

    def test_03_price_dropped_computation(self):
        """Test price dropped computation"""
        wishlist = self.env['line.wishlist'].create({
            'partner_id': self.partner.id,
            'product_id': self.product1.id,
            'product_price': 150.0,  # Original price was higher
        })

        # Product price is 100, saved price was 150
        self.assertTrue(wishlist.price_dropped)

    def test_04_price_not_dropped(self):
        """Test price not dropped when current price is same or higher"""
        wishlist = self.env['line.wishlist'].create({
            'partner_id': self.partner.id,
            'product_id': self.product1.id,
            'product_price': 100.0,  # Same as current price
        })

        self.assertFalse(wishlist.price_dropped)

    def test_05_auto_set_price_on_create(self):
        """Test that product price is auto-set on create"""
        wishlist = self.env['line.wishlist'].create({
            'partner_id': self.partner.id,
            'product_id': self.product2.id,
        })

        self.assertEqual(wishlist.product_price, 200.0)

    def test_06_multiple_items_per_partner(self):
        """Test partner can have multiple different products"""
        wishlist1 = self.env['line.wishlist'].create({
            'partner_id': self.partner.id,
            'product_id': self.product1.id,
        })

        wishlist2 = self.env['line.wishlist'].create({
            'partner_id': self.partner.id,
            'product_id': self.product2.id,
        })

        self.assertEqual(len(self.env['line.wishlist'].search([
            ('partner_id', '=', self.partner.id)
        ])), 2)

    def test_07_delete_wishlist_item(self):
        """Test deleting wishlist item"""
        wishlist = self.env['line.wishlist'].create({
            'partner_id': self.partner.id,
            'product_id': self.product1.id,
        })

        wishlist_id = wishlist.id
        wishlist.unlink()

        self.assertFalse(self.env['line.wishlist'].browse(wishlist_id).exists())

    def test_08_related_product_name(self):
        """Test related product name field"""
        wishlist = self.env['line.wishlist'].create({
            'partner_id': self.partner.id,
            'product_id': self.product1.id,
        })

        self.assertEqual(wishlist.product_name, 'Test Product 1')

    def test_09_current_price_related(self):
        """Test current price related field"""
        wishlist = self.env['line.wishlist'].create({
            'partner_id': self.partner.id,
            'product_id': self.product1.id,
        })

        self.assertEqual(wishlist.current_price, 100.0)

        # Update product price
        self.product1.list_price = 80.0

        # Reload and check
        wishlist.invalidate_recordset()
        self.assertEqual(wishlist.current_price, 80.0)

    def test_10_notes_field(self):
        """Test notes field"""
        wishlist = self.env['line.wishlist'].create({
            'partner_id': self.partner.id,
            'product_id': self.product1.id,
            'notes': 'Want to buy for birthday',
        })

        self.assertEqual(wishlist.notes, 'Want to buy for birthday')
