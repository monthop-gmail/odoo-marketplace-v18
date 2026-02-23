# -*- coding: utf-8 -*-
"""
Tests for LINE Marketplace Compare
"""
from odoo.tests.common import TransactionCase


class TestLineCompare(TransactionCase):
    """Test cases for line.compare.list and line.compare.item models"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create test channel
        cls.channel = cls.env['line.channel'].create({
            'name': 'Test Channel',
            'code': 'test_compare',
            'channel_id': 'test456',
            'channel_secret': 'secret456',
            'channel_access_token': 'token456',
        })

        # Create test partner
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test Customer',
            'email': 'compare@example.com',
        })

        # Create test product category
        cls.category = cls.env['product.category'].create({
            'name': 'Test Compare Category',
        })

        # Create test products
        cls.products = []
        for i in range(5):
            product = cls.env['product.template'].create({
                'name': f'Compare Product {i+1}',
                'list_price': (i + 1) * 100.0,
                'categ_id': cls.category.id,
                'is_published': True,
            })
            cls.products.append(product)

    def test_01_create_compare_list(self):
        """Test creating a compare list"""
        compare_list = self.env['line.compare.list'].create({
            'partner_id': self.partner.id,
            'channel_id': self.channel.id,
        })

        self.assertTrue(compare_list.exists())
        self.assertEqual(compare_list.partner_id, self.partner)
        self.assertEqual(compare_list.item_count, 0)

    def test_02_add_product_to_compare(self):
        """Test adding product to compare list"""
        compare_list = self.env['line.compare.list'].create({
            'partner_id': self.partner.id,
        })

        result = compare_list.add_product(self.products[0].id)

        self.assertIn('success', result)
        self.assertEqual(compare_list.item_count, 1)

    def test_03_max_items_limit(self):
        """Test maximum items limit (4 items)"""
        compare_list = self.env['line.compare.list'].create({
            'partner_id': self.partner.id,
        })

        # Add 4 products (max)
        for i in range(4):
            result = compare_list.add_product(self.products[i].id)
            self.assertIn('success', result)

        self.assertEqual(compare_list.item_count, 4)

        # Try to add 5th product
        result = compare_list.add_product(self.products[4].id)
        self.assertIn('error', result)
        self.assertEqual(compare_list.item_count, 4)

    def test_04_prevent_duplicate_products(self):
        """Test preventing duplicate products in compare list"""
        compare_list = self.env['line.compare.list'].create({
            'partner_id': self.partner.id,
        })

        # Add product first time
        result1 = compare_list.add_product(self.products[0].id)
        self.assertIn('success', result1)

        # Try to add same product again
        result2 = compare_list.add_product(self.products[0].id)
        self.assertIn('error', result2)
        self.assertEqual(compare_list.item_count, 1)

    def test_05_remove_product_from_compare(self):
        """Test removing product from compare list"""
        compare_list = self.env['line.compare.list'].create({
            'partner_id': self.partner.id,
        })

        compare_list.add_product(self.products[0].id)
        compare_list.add_product(self.products[1].id)
        self.assertEqual(compare_list.item_count, 2)

        result = compare_list.remove_product(self.products[0].id)

        self.assertIn('success', result)
        self.assertEqual(compare_list.item_count, 1)

    def test_06_remove_nonexistent_product(self):
        """Test removing product not in compare list"""
        compare_list = self.env['line.compare.list'].create({
            'partner_id': self.partner.id,
        })

        result = compare_list.remove_product(self.products[0].id)

        self.assertIn('error', result)

    def test_07_clear_compare_list(self):
        """Test clearing entire compare list"""
        compare_list = self.env['line.compare.list'].create({
            'partner_id': self.partner.id,
        })

        for i in range(3):
            compare_list.add_product(self.products[i].id)

        self.assertEqual(compare_list.item_count, 3)

        result = compare_list.clear()

        self.assertIn('success', result)
        self.assertEqual(compare_list.item_count, 0)

    def test_08_compare_item_related_fields(self):
        """Test compare item related fields"""
        compare_list = self.env['line.compare.list'].create({
            'partner_id': self.partner.id,
        })

        compare_list.add_product(self.products[0].id)
        item = compare_list.item_ids[0]

        self.assertEqual(item.product_name, 'Compare Product 1')
        self.assertEqual(item.product_price, 100.0)
        self.assertEqual(item.category_id, self.category)

    def test_09_compute_name(self):
        """Test computed name field"""
        compare_list = self.env['line.compare.list'].create({
            'partner_id': self.partner.id,
        })

        self.assertIn('Test Customer', compare_list.name)

    def test_10_item_count_computation(self):
        """Test item count computation"""
        compare_list = self.env['line.compare.list'].create({
            'partner_id': self.partner.id,
        })

        self.assertEqual(compare_list.item_count, 0)

        compare_list.add_product(self.products[0].id)
        self.assertEqual(compare_list.item_count, 1)

        compare_list.add_product(self.products[1].id)
        self.assertEqual(compare_list.item_count, 2)

    def test_11_max_items_constant(self):
        """Test MAX_ITEMS constant"""
        compare_list = self.env['line.compare.list'].create({
            'partner_id': self.partner.id,
        })

        self.assertEqual(compare_list.MAX_ITEMS, 4)

    def test_12_item_sequence(self):
        """Test item sequence field"""
        compare_list = self.env['line.compare.list'].create({
            'partner_id': self.partner.id,
        })

        compare_list.add_product(self.products[0].id)
        item = compare_list.item_ids[0]

        self.assertEqual(item.sequence, 10)  # Default sequence
