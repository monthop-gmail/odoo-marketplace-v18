#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to create test data for LINE Marketplace module via XML-RPC
สร้างข้อมูลทดสอบสำหรับ module LINE Marketplace

Usage: python create_test_data.py
"""

import xmlrpc.client
import sys

# Odoo connection settings
ODOO_URL = "http://localhost:8076"
ODOO_DB = "odoo_coop"
ODOO_USER = "admin"
ODOO_PASSWORD = "admin"  # Change this to your admin password


def connect_odoo():
    """Connect to Odoo via XML-RPC"""
    print(f"Connecting to Odoo at {ODOO_URL}...")

    try:
        common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
        uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})

        if not uid:
            print("ERROR: Authentication failed. Check username/password.")
            return None, None

        models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
        print(f"Connected! User ID: {uid}")
        return uid, models

    except Exception as e:
        print(f"ERROR: Could not connect to Odoo: {e}")
        return None, None


def execute(models, uid, model, method, *args, **kwargs):
    """Execute Odoo model method"""
    return models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, model, method, args, kwargs)


def create_line_channel(models, uid):
    """Create demo LINE channel"""
    print("\n" + "=" * 50)
    print("Creating LINE Channel...")
    print("=" * 50)

    # Check if demo channel exists
    existing = execute(models, uid, 'line.channel', 'search', [('code', '=', 'demo_coop')])
    if existing:
        print(f"  Demo channel already exists (ID: {existing[0]})")
        return existing[0]

    channel_data = {
        'name': 'สหกรณ์ทดสอบ Demo Coop',
        'code': 'demo_coop',
        'channel_id': 'DEMO123456789',
        'channel_secret': 'demo_secret_12345678901234567890',
        'channel_access_token': 'demo_access_token_for_testing_purposes_only',
        'auto_welcome_message': True,
        'welcome_message': 'ยินดีต้อนรับสู่สหกรณ์ทดสอบ! 🎉\nพิมพ์ "สินค้า" เพื่อดูรายการสินค้า',
        'notify_on_order': True,
        'notify_on_shipping': True,
    }

    channel_id = execute(models, uid, 'line.channel', 'create', [channel_data])
    print(f"  Created LINE Channel: ID={channel_id}, Code=demo_coop")
    return channel_id


def create_product_category(models, uid):
    """Create product categories"""
    print("\n" + "=" * 50)
    print("Creating Product Categories...")
    print("=" * 50)

    categories = [
        {'name': 'อาหารและเครื่องดื่ม', 'code': 'food'},
        {'name': 'ผลิตภัณฑ์เกษตร', 'code': 'agri'},
        {'name': 'สินค้าแปรรูป', 'code': 'processed'},
    ]

    category_ids = {}
    for cat in categories:
        existing = execute(models, uid, 'product.category', 'search', [('name', '=', cat['name'])])
        if existing:
            category_ids[cat['code']] = existing[0]
            print(f"  Category '{cat['name']}' already exists (ID: {existing[0]})")
        else:
            cat_id = execute(models, uid, 'product.category', 'create', [{'name': cat['name']}])
            category_ids[cat['code']] = cat_id
            print(f"  Created category '{cat['name']}' (ID: {cat_id})")

    return category_ids


def create_products(models, uid, category_ids):
    """Create test products"""
    print("\n" + "=" * 50)
    print("Creating Test Products...")
    print("=" * 50)

    products = [
        {
            'name': 'ข้าวหอมมะลิ 5 กก.',
            'list_price': 250.00,
            'categ_id': category_ids.get('agri', 1),
            'detailed_type': 'consu',
            'sale_ok': True,
            'purchase_ok': True,
            'is_published': True,
            'description_sale': 'ข้าวหอมมะลิคุณภาพดี จากสหกรณ์การเกษตร',
        },
        {
            'name': 'น้ำผึ้งแท้ 500ml',
            'list_price': 180.00,
            'categ_id': category_ids.get('processed', 1),
            'detailed_type': 'consu',
            'sale_ok': True,
            'purchase_ok': True,
            'is_published': True,
            'description_sale': 'น้ำผึ้งแท้ 100% จากฟาร์มผึ้งธรรมชาติ',
        },
        {
            'name': 'กาแฟคั่วบด 250g',
            'list_price': 150.00,
            'categ_id': category_ids.get('food', 1),
            'detailed_type': 'consu',
            'sale_ok': True,
            'purchase_ok': True,
            'is_published': True,
            'description_sale': 'กาแฟอาราบิก้าคั่วสด บดใหม่ หอมกรุ่น',
        },
        {
            'name': 'น้ำมันมะพร้าวสกัดเย็น 500ml',
            'list_price': 220.00,
            'categ_id': category_ids.get('processed', 1),
            'detailed_type': 'consu',
            'sale_ok': True,
            'purchase_ok': True,
            'is_published': True,
            'description_sale': 'น้ำมันมะพร้าวสกัดเย็น ไม่ผ่านความร้อน',
        },
        {
            'name': 'มะม่วงน้ำดอกไม้ 1 กก.',
            'list_price': 120.00,
            'categ_id': category_ids.get('agri', 1),
            'detailed_type': 'consu',
            'sale_ok': True,
            'purchase_ok': True,
            'is_published': True,
            'description_sale': 'มะม่วงน้ำดอกไม้สุกพอดี หวานฉ่ำ',
        },
    ]

    created_ids = []
    for prod in products:
        existing = execute(models, uid, 'product.template', 'search', [('name', '=', prod['name'])])
        if existing:
            print(f"  Product '{prod['name']}' already exists (ID: {existing[0]})")
            created_ids.append(existing[0])
        else:
            prod_id = execute(models, uid, 'product.template', 'create', [prod])
            print(f"  Created product '{prod['name']}' - ฿{prod['list_price']:,.2f} (ID: {prod_id})")
            created_ids.append(prod_id)

    return created_ids


def create_line_member(models, uid, channel_id):
    """Create a test LINE member"""
    print("\n" + "=" * 50)
    print("Creating Test LINE Member...")
    print("=" * 50)

    line_user_id = "Utest_demo_user_001"

    # Check if member exists
    existing = execute(models, uid, 'line.channel.member', 'search', [
        ('line_user_id', '=', line_user_id),
        ('channel_id', '=', channel_id)
    ])
    if existing:
        print(f"  Test member already exists (ID: {existing[0]})")
        return existing[0]

    # Create partner first
    partner_data = {
        'name': 'ลูกค้าทดสอบ LINE',
        'email': 'test_line_buyer@example.com',
        'phone': '0812345678',
        'line_user_id': line_user_id,
        'line_display_name': 'ลูกค้าทดสอบ',
        'customer_rank': 1,
    }

    existing_partner = execute(models, uid, 'res.partner', 'search', [('line_user_id', '=', line_user_id)])
    if existing_partner:
        partner_id = existing_partner[0]
        print(f"  Partner already exists (ID: {partner_id})")
    else:
        partner_id = execute(models, uid, 'res.partner', 'create', [partner_data])
        print(f"  Created partner (ID: {partner_id})")

    # Create member
    member_data = {
        'line_user_id': line_user_id,
        'display_name': 'ลูกค้าทดสอบ',
        'channel_id': channel_id,
        'partner_id': partner_id,
        'is_following': True,
        'member_type': 'buyer',
        'registration_state': 'verified',
    }

    member_id = execute(models, uid, 'line.channel.member', 'create', [member_data])
    print(f"  Created LINE member (ID: {member_id})")
    return member_id


def verify_mock_auth(models, uid):
    """Verify mock authentication is enabled"""
    print("\n" + "=" * 50)
    print("Checking Mock Authentication Setting...")
    print("=" * 50)

    # Check ir.config_parameter
    param = execute(models, uid, 'ir.config_parameter', 'search_read',
                    [('key', '=', 'core_line_integration.mock_auth')],
                    {'fields': ['value']})

    if param:
        print(f"  Mock auth setting: {param[0].get('value', 'Not set')}")
    else:
        # Create the parameter
        execute(models, uid, 'ir.config_parameter', 'set_param', 'core_line_integration.mock_auth', 'True')
        print("  Enabled mock authentication")


def print_summary(channel_id, product_ids):
    """Print test summary"""
    print("\n" + "=" * 60)
    print("   TEST DATA CREATED SUCCESSFULLY!")
    print("=" * 60)
    print(f"""
  LINE Channel:
    - ID: {channel_id}
    - Code: demo_coop

  Products Created: {len(product_ids)}

  Test Credentials for API:
    - line_user_id: Utest_demo_user_001 (or any unique ID)
    - channel_code: demo_coop

  API Endpoints:
    - Base URL: {ODOO_URL}/api/line-buyer
    - Login: POST /auth/mock/login
    - Products: GET /products
    - Cart: GET/POST /cart

  To test the ordering flow, run:
    cd /opt/docker-test/odoo-co-op-v18/odoo-addons
    python core_line_integration/tests/test_ordering_flow.py
""")


def main():
    """Main function"""
    print("\n" + "=" * 60)
    print("   LINE MARKETPLACE TEST DATA CREATOR")
    print("   สร้างข้อมูลทดสอบสำหรับ LINE Marketplace")
    print("=" * 60)

    # Connect to Odoo
    uid, models = connect_odoo()
    if not uid:
        print("\nFailed to connect to Odoo. Exiting.")
        sys.exit(1)

    try:
        # Create LINE channel
        channel_id = create_line_channel(models, uid)

        # Create product categories
        category_ids = create_product_category(models, uid)

        # Create products
        product_ids = create_products(models, uid, category_ids)

        # Create test member
        create_line_member(models, uid, channel_id)

        # Verify mock auth
        verify_mock_auth(models, uid)

        # Print summary
        print_summary(channel_id, product_ids)

        print("\nDone! Test data created successfully.")

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
