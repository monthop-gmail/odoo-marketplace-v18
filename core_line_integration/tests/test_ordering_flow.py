# -*- coding: utf-8 -*-
"""
Standalone integration test for LINE Marketplace ordering flow.
ทดสอบ flow การสั่งซื้อผ่าน LINE API

NOTE: This is NOT an Odoo TestCase — it uses the `requests` library to test
the REST API externally against a running Odoo instance.  It must NOT be
registered in tests/__init__.py because Odoo's test runner would fail to
import it (no TransactionCase/HttpCase base class).

Run standalone:
    python core_line_integration/tests/test_ordering_flow.py

Requires a running Odoo instance at BASE_URL below.
"""

import requests
import json
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)

# Configuration
BASE_URL = "http://localhost:8076"
API_BASE = f"{BASE_URL}/api/line-buyer"

# Test user data
TEST_USER = {
    "line_user_id": f"Utest_{datetime.now().strftime('%Y%m%d%H%M%S')}",
    "display_name": "ผู้ทดสอบ LINE",
    "channel_code": "demo_coop"
}


class LineOrderingTest:
    """Test class for LINE ordering flow"""

    def __init__(self):
        self.session_token = None
        self.line_user_id = None
        self.channel_code = None
        self.cart = None
        self.order = None
        self.shipping_address_id = None

    def log(self, message, level="INFO"):
        """Print formatted log message"""
        print(f"[{level}] {datetime.now().strftime('%H:%M:%S')} - {message}")

    def api_call(self, method, endpoint, data=None, params=None):
        """Make API call with LINE User ID header (mock mode)"""
        url = f"{API_BASE}{endpoint}"
        headers = {
            "Content-Type": "application/json",
        }

        # Use X-Line-User-Id header for mock authentication
        if self.line_user_id:
            headers["X-Line-User-Id"] = self.line_user_id
            headers["X-Channel-Code"] = self.channel_code or "demo_coop"

        if self.session_token:
            headers["X-Session-Token"] = self.session_token

        try:
            if method == "GET":
                response = requests.get(url, headers=headers, params=params, timeout=30)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data, timeout=30)
            elif method == "PUT":
                response = requests.put(url, headers=headers, json=data, timeout=30)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers, timeout=30)
            else:
                raise ValueError(f"Unknown method: {method}")

            return response.json() if response.content else {}
        except requests.exceptions.ConnectionError:
            self.log(f"Connection error to {url}", "ERROR")
            return {"success": False, "error": {"message": "Connection error"}}
        except Exception as e:
            self.log(f"API call error: {e}", "ERROR")
            return {"success": False, "error": {"message": str(e)}}

    # ==========================================
    # Step 1: Authentication
    # ==========================================
    def test_login(self):
        """Test mock login"""
        self.log("=" * 50)
        self.log("Step 1: Mock Login (เข้าสู่ระบบ)")
        self.log("=" * 50)

        response = self.api_call("POST", "/auth/mock/login", data=TEST_USER)

        # Handle nested data structure
        data = response.get("data", response)

        if response.get("success") or data.get("session_token"):
            self.session_token = data.get("session_token")
            self.line_user_id = data.get('line_user_id')
            channel = data.get('channel', {})
            self.channel_code = channel.get('code', 'demo_coop')

            self.log(f"Login successful!")
            self.log(f"  - LINE User ID: {self.line_user_id}")
            self.log(f"  - Display Name: {data.get('display_name')}")
            self.log(f"  - Channel: {channel.get('name', 'N/A')} ({self.channel_code})")
            if self.session_token:
                self.log(f"  - Session Token: {self.session_token[:20]}...")
            return True
        else:
            self.log(f"Login failed: {response.get('error', response)}", "ERROR")
            return False

    # ==========================================
    # Step 2: Browse Products
    # ==========================================
    def test_browse_products(self):
        """Test browsing products"""
        self.log("=" * 50)
        self.log("Step 2: Browse Products (ดูรายการสินค้า)")
        self.log("=" * 50)

        # Get categories first
        self.log("Getting categories...")
        categories = self.api_call("GET", "/categories")
        cat_data = categories.get("data", categories)
        if categories.get("success") and cat_data:
            cat_list = cat_data if isinstance(cat_data, list) else cat_data.get('items', [])
            self.log(f"  Found {len(cat_list)} categories")
            for cat in cat_list[:5]:
                self.log(f"    - {cat.get('name')} (ID: {cat.get('id')})")

        # Get products
        self.log("\nGetting products...")
        products = self.api_call("GET", "/products", params={"limit": 10})

        if products.get("success") and products.get("data"):
            data = products['data']
            # Handle both 'items' and 'products' keys
            product_list = data.get('items', data.get('products', data))
            if isinstance(product_list, list) and product_list:
                self.log(f"  Found {len(product_list)} products")
                self.products = product_list
                for prod in product_list[:5]:
                    price = prod.get('price', 0) or 0
                    self.log(f"    - {prod.get('name')} | ${price:,.2f} (ID: {prod.get('id')})")
                return True
            else:
                self.log("  No products found in list format")
        else:
            self.log(f"  Could not get products: {products.get('error', 'Unknown error')}", "WARNING")

        # Create test products if none exist
        self.log("\nNo products available. Please create some products in Odoo first.")
        self.products = []
        return False

    # ==========================================
    # Step 3: Add to Cart
    # ==========================================
    def test_add_to_cart(self):
        """Test adding products to cart"""
        self.log("=" * 50)
        self.log("Step 3: Add to Cart (เพิ่มสินค้าลงตะกร้า)")
        self.log("=" * 50)

        if not hasattr(self, 'products') or not self.products:
            self.log("No products available to add to cart", "WARNING")
            return False

        # Add first 2 products to cart
        for i, product in enumerate(self.products[:2]):
            quantity = (i + 1)  # 1 for first, 2 for second
            self.log(f"\nAdding {quantity}x '{product.get('name')}' to cart...")

            response = self.api_call("POST", "/cart/add", data={
                "product_id": product.get('id'),
                "quantity": quantity
            })

            if response.get("success"):
                self.log(f"  Added successfully!")
            else:
                self.log(f"  Failed: {response.get('error', response)}", "ERROR")

        # Get cart to verify
        self.log("\nGetting cart contents...")
        cart = self.api_call("GET", "/cart")

        if cart.get("success") and cart.get("data"):
            self.cart = cart['data']
            self.log(f"  Cart ID: {self.cart.get('id')}")
            self.log(f"  Order Name: {self.cart.get('name')}")
            self.log(f"  Items: {self.cart.get('item_count', 0)}")
            self.log(f"  Subtotal: ฿{self.cart.get('subtotal', 0):,.2f}")
            self.log(f"  Tax: ฿{self.cart.get('tax', 0):,.2f}")
            self.log(f"  Total: ฿{self.cart.get('total', 0):,.2f}")

            if self.cart.get('lines'):
                self.log("\n  Cart Lines:")
                for line in self.cart['lines']:
                    prod = line.get('product', {})
                    self.log(f"    - {prod.get('name')} x{line.get('quantity')} = ฿{line.get('subtotal', 0):,.2f}")
            return True
        else:
            self.log(f"  Could not get cart: {cart.get('error', cart)}", "ERROR")
            return False

    # ==========================================
    # Step 4: Manage Shipping Address
    # ==========================================
    def test_shipping_address(self):
        """Test shipping address management"""
        self.log("=" * 50)
        self.log("Step 4: Shipping Address (ที่อยู่จัดส่ง)")
        self.log("=" * 50)

        # Get existing addresses
        self.log("Getting existing addresses...")
        addresses = self.api_call("GET", "/checkout/shipping-addresses")

        if addresses.get("success") and addresses.get("data"):
            addr_data = addresses['data']
            # Handle both list and dict with 'items' key
            addr_list = addr_data if isinstance(addr_data, list) else addr_data.get('items', [])
            if addr_list and isinstance(addr_list, list) and len(addr_list) > 0:
                self.log(f"  Found {len(addr_list)} existing addresses")
                self.shipping_address_id = addr_list[0].get('id')
                self.log(f"  Using address ID: {self.shipping_address_id}")
                return True

        # Create new address if none exists
        self.log("\nCreating new shipping address...")
        new_address = {
            "name": "ผู้ทดสอบ LINE",
            "phone": "0812345678",
            "street": "123 ถนนทดสอบ",
            "street2": "แขวงทดสอบ เขตทดสอบ",
            "city": "กรุงเทพมหานคร",
            "zip": "10110"
        }

        response = self.api_call("POST", "/checkout/shipping-address", data=new_address)

        if response.get("success") and response.get("data"):
            self.shipping_address_id = response['data'].get('id')
            self.log(f"  Created address ID: {self.shipping_address_id}")
            self.log(f"  Name: {response['data'].get('name')}")
            self.log(f"  Address: {response['data'].get('street')}")
            return True
        else:
            self.log(f"  Failed to create address: {response.get('error', response)}", "ERROR")
            return False

    # ==========================================
    # Step 5: Checkout (Confirm Order)
    # ==========================================
    def test_checkout(self):
        """Test checkout and order confirmation"""
        self.log("=" * 50)
        self.log("Step 5: Checkout (ยืนยันคำสั่งซื้อ)")
        self.log("=" * 50)

        if not self.cart:
            self.log("No cart available for checkout", "ERROR")
            return False

        checkout_data = {
            "note": "ทดสอบการสั่งซื้อผ่าน LINE API"
        }

        if self.shipping_address_id:
            checkout_data["shipping_address_id"] = self.shipping_address_id

        self.log(f"Confirming order...")
        self.log(f"  Shipping Address ID: {self.shipping_address_id}")
        self.log(f"  Note: {checkout_data.get('note')}")

        response = self.api_call("POST", "/checkout/confirm", data=checkout_data)

        if response.get("success") and response.get("data"):
            self.order = response['data'].get('order', response['data'])
            self.log(f"\n  ORDER CONFIRMED!")
            self.log(f"  " + "=" * 40)
            self.log(f"  Order ID: {self.order.get('id')}")
            self.log(f"  Order Name: {self.order.get('name')}")
            self.log(f"  Date: {self.order.get('date')}")
            self.log(f"  State: {self.order.get('state')} ({self.order.get('state_display', '')})")
            self.log(f"  Subtotal: ฿{self.order.get('subtotal', 0):,.2f}")
            self.log(f"  Tax: ฿{self.order.get('tax', 0):,.2f}")
            self.log(f"  Total: ฿{self.order.get('total', 0):,.2f}")
            self.log(f"  Item Count: {self.order.get('item_count', 0)}")
            return True
        else:
            self.log(f"  Checkout failed: {response.get('error', response)}", "ERROR")
            return False

    # ==========================================
    # Step 6: Check Order History
    # ==========================================
    def test_order_history(self):
        """Test order history"""
        self.log("=" * 50)
        self.log("Step 6: Order History (ประวัติคำสั่งซื้อ)")
        self.log("=" * 50)

        response = self.api_call("GET", "/orders", params={"limit": 5})

        if response.get("success") and response.get("data"):
            orders = response['data'].get('orders', response['data'])
            if isinstance(orders, list):
                self.log(f"  Found {len(orders)} orders")
                for order in orders[:5]:
                    self.log(f"    - {order.get('name')} | {order.get('state')} | ฿{order.get('total', 0):,.2f} | {order.get('date', '')[:10]}")
                return True

        self.log("  No orders found or error", "WARNING")
        return False

    # ==========================================
    # Run All Tests
    # ==========================================
    def run_all_tests(self):
        """Run the complete ordering flow test"""
        self.log("\n" + "=" * 60)
        self.log("   LINE ORDERING FLOW TEST")
        self.log("   ทดสอบ flow การสั่งซื้อผ่าน LINE")
        self.log("=" * 60)
        self.log(f"API Base URL: {API_BASE}")
        self.log(f"Test User: {TEST_USER['display_name']} ({TEST_USER['line_user_id'][:20]}...)")
        self.log("")

        results = {}

        # Step 1: Login
        results['login'] = self.test_login()
        if not results['login']:
            self.log("\nLogin failed. Cannot continue.", "ERROR")
            return results

        # Step 2: Browse Products
        results['browse'] = self.test_browse_products()

        # Step 3: Add to Cart (only if products exist)
        if results['browse']:
            results['cart'] = self.test_add_to_cart()
        else:
            results['cart'] = False
            self.log("\nSkipping cart test - no products available", "WARNING")

        # Step 4: Shipping Address
        results['address'] = self.test_shipping_address()

        # Step 5: Checkout (only if cart has items)
        if results['cart']:
            results['checkout'] = self.test_checkout()
        else:
            results['checkout'] = False
            self.log("\nSkipping checkout - cart is empty", "WARNING")

        # Step 6: Order History
        results['history'] = self.test_order_history()

        # Summary
        self.log("\n" + "=" * 60)
        self.log("   TEST SUMMARY")
        self.log("=" * 60)
        for step, passed in results.items():
            status = "PASS" if passed else "FAIL"
            self.log(f"  {step.upper():12} : {status}")

        total_passed = sum(1 for v in results.values() if v)
        total_tests = len(results)
        self.log(f"\n  Total: {total_passed}/{total_tests} tests passed")

        if self.order:
            self.log(f"\n  Created Order: {self.order.get('name')}")

        return results


def main():
    """Main function to run tests"""
    tester = LineOrderingTest()
    results = tester.run_all_tests()

    # Exit with error code if any test failed
    if not all(results.values()):
        exit(1)
    exit(0)


if __name__ == "__main__":
    main()
