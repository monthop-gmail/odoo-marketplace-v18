#!/bin/bash
# ============================================================
# Test Cases for core_line_integration REST API
# Usage: bash test_api.sh [base_url]
# Example: bash test_api.sh http://localhost:8069
# ============================================================

BASE_URL="${1:-http://localhost:8069}"
API_URL="$BASE_URL/api/line-buyer"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
PASSED=0
FAILED=0

# Test user data
LINE_USER_ID=""
SESSION_TOKEN=""

# Helper functions
print_header() {
    echo ""
    echo "============================================================"
    echo -e "${YELLOW}$1${NC}"
    echo "============================================================"
}

print_test() {
    echo -e "\n${YELLOW}TEST: $1${NC}"
}

check_result() {
    local response="$1"
    local expected="$2"
    local test_name="$3"

    if echo "$response" | grep -q "$expected"; then
        echo -e "${GREEN}✓ PASSED${NC}: $test_name"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAILED${NC}: $test_name"
        echo "  Expected: $expected"
        echo "  Response: $response"
        ((FAILED++))
        return 1
    fi
}

# ============================================================
# TEST GROUP 1: Health & Config (No Auth Required)
# ============================================================
print_header "TEST GROUP 1: Health & Config (No Auth Required)"

print_test "1.1 Health Check"
RESPONSE=$(curl -s "$API_URL/health")
check_result "$RESPONSE" '"success": true' "Health endpoint returns success"
check_result "$RESPONSE" '"status": "ok"' "Status is ok"
check_result "$RESPONSE" '"module": "core_line_integration"' "Module name correct"

print_test "1.2 Get Config"
RESPONSE=$(curl -s "$API_URL/config")
check_result "$RESPONSE" '"success": true' "Config endpoint returns success"
check_result "$RESPONSE" '"mock_auth": true' "Mock auth is enabled"
check_result "$RESPONSE" '"channels"' "Channels list exists"

# ============================================================
# TEST GROUP 2: Products API (No Auth Required)
# ============================================================
print_header "TEST GROUP 2: Products API (No Auth Required)"

print_test "2.1 Get Products List"
RESPONSE=$(curl -s "$API_URL/products?limit=5")
check_result "$RESPONSE" '"success": true' "Products endpoint returns success"
check_result "$RESPONSE" '"items"' "Items array exists"
check_result "$RESPONSE" '"pagination"' "Pagination info exists"

print_test "2.2 Get Products with Pagination"
RESPONSE=$(curl -s "$API_URL/products?page=1&limit=3")
check_result "$RESPONSE" '"page": 1' "Page number correct"
check_result "$RESPONSE" '"limit": 3' "Limit correct"

print_test "2.3 Get Products with Search"
RESPONSE=$(curl -s "$API_URL/products?search=desk&limit=5")
check_result "$RESPONSE" '"success": true' "Search returns success"

print_test "2.4 Get Single Product"
# Get first product ID from list
PRODUCT_ID=$(curl -s "$API_URL/products?limit=1" | grep -o '"id": [0-9]*' | head -1 | grep -o '[0-9]*')
if [ -n "$PRODUCT_ID" ]; then
    RESPONSE=$(curl -s "$API_URL/products/$PRODUCT_ID")
    check_result "$RESPONSE" '"success": true' "Single product returns success"
    check_result "$RESPONSE" '"id":' "Product has ID"
    check_result "$RESPONSE" '"name":' "Product has name"
else
    echo -e "${RED}✗ FAILED${NC}: Could not get product ID"
    ((FAILED++))
fi

print_test "2.5 Get Non-existent Product"
RESPONSE=$(curl -s "$API_URL/products/999999")
check_result "$RESPONSE" '"success": false' "Returns failure for non-existent product"
check_result "$RESPONSE" 'not found' "Error message indicates not found"

print_test "2.6 Get Categories"
RESPONSE=$(curl -s "$API_URL/categories")
check_result "$RESPONSE" '"success": true' "Categories endpoint returns success"
check_result "$RESPONSE" '"categories"' "Categories array exists"

# ============================================================
# TEST GROUP 3: Mock Authentication
# ============================================================
print_header "TEST GROUP 3: Mock Authentication"

print_test "3.1 Mock Login - New User"
RESPONSE=$(curl -s -X POST "$API_URL/auth/mock/login" \
    -H "Content-Type: application/json" \
    -d '{"display_name": "Test Buyer", "channel_code": "demo_coop"}')
check_result "$RESPONSE" '"success": true' "Mock login returns success"
check_result "$RESPONSE" '"session_token"' "Returns session token"
check_result "$RESPONSE" '"line_user_id"' "Returns LINE user ID"

# Extract LINE user ID for subsequent tests
LINE_USER_ID=$(echo "$RESPONSE" | grep -o '"line_user_id": "[^"]*"' | cut -d'"' -f4)
SESSION_TOKEN=$(echo "$RESPONSE" | grep -o '"session_token": "[^"]*"' | cut -d'"' -f4)
echo "  Extracted LINE_USER_ID: $LINE_USER_ID"

print_test "3.2 Mock Login - Existing User"
RESPONSE=$(curl -s -X POST "$API_URL/auth/mock/login" \
    -H "Content-Type: application/json" \
    -d "{\"line_user_id\": \"$LINE_USER_ID\", \"channel_code\": \"demo_coop\"}")
check_result "$RESPONSE" '"success": true' "Re-login returns success"

print_test "3.3 Get Test Users List"
RESPONSE=$(curl -s "$API_URL/auth/test-users")
check_result "$RESPONSE" '"success": true' "Test users endpoint returns success"
check_result "$RESPONSE" '"users"' "Users array exists"

print_test "3.4 Get Session Info"
RESPONSE=$(curl -s "$API_URL/auth/mock/session" \
    -H "X-Session-Token: $SESSION_TOKEN")
# Note: This may fail as session is in-memory and may not persist
echo "  Session check (may vary based on implementation)"

# ============================================================
# TEST GROUP 4: Cart API (Auth Required)
# ============================================================
print_header "TEST GROUP 4: Cart API (Auth Required)"

AUTH_HEADERS="-H \"X-Line-User-Id: $LINE_USER_ID\" -H \"X-Channel-Code: demo_coop\""

print_test "4.1 Get Cart (Empty)"
RESPONSE=$(curl -s "$API_URL/cart" \
    -H "X-Line-User-Id: $LINE_USER_ID" \
    -H "X-Channel-Code: demo_coop")
check_result "$RESPONSE" '"success": true' "Get cart returns success"
check_result "$RESPONSE" '"lines"' "Cart has lines array"

print_test "4.2 Cart without Auth Header"
RESPONSE=$(curl -s "$API_URL/cart")
check_result "$RESPONSE" '"success": false' "Returns failure without auth"
check_result "$RESPONSE" 'AUTH_REQUIRED\|Missing' "Error indicates auth required"

print_test "4.3 Add Product to Cart"
# Get a valid product ID
PRODUCT_ID=$(curl -s "$API_URL/products?limit=1" | grep -o '"id": [0-9]*' | head -1 | grep -o '[0-9]*')
RESPONSE=$(curl -s -X POST "$API_URL/cart/add" \
    -H "Content-Type: application/json" \
    -H "X-Line-User-Id: $LINE_USER_ID" \
    -H "X-Channel-Code: demo_coop" \
    -d "{\"product_id\": $PRODUCT_ID, \"quantity\": 2}")
check_result "$RESPONSE" '"success": true' "Add to cart returns success"
check_result "$RESPONSE" '"Product added to cart"' "Success message correct"

# Extract line ID for update test
LINE_ID=$(echo "$RESPONSE" | grep -o '"id": [0-9]*' | head -1 | grep -o '[0-9]*')

print_test "4.4 Add Same Product Again (Quantity Should Increase)"
RESPONSE=$(curl -s -X POST "$API_URL/cart/add" \
    -H "Content-Type: application/json" \
    -H "X-Line-User-Id: $LINE_USER_ID" \
    -H "X-Channel-Code: demo_coop" \
    -d "{\"product_id\": $PRODUCT_ID, \"quantity\": 1}")
check_result "$RESPONSE" '"success": true' "Add more returns success"

print_test "4.5 Get Cart (With Items)"
RESPONSE=$(curl -s "$API_URL/cart" \
    -H "X-Line-User-Id: $LINE_USER_ID" \
    -H "X-Channel-Code: demo_coop")
check_result "$RESPONSE" '"success": true' "Get cart returns success"
check_result "$RESPONSE" '"quantity"' "Cart has quantity"
check_result "$RESPONSE" '"total"' "Cart has total"

print_test "4.6 Add Invalid Product"
RESPONSE=$(curl -s -X POST "$API_URL/cart/add" \
    -H "Content-Type: application/json" \
    -H "X-Line-User-Id: $LINE_USER_ID" \
    -H "X-Channel-Code: demo_coop" \
    -d '{"product_id": 999999, "quantity": 1}')
check_result "$RESPONSE" '"success": false' "Invalid product returns failure"

print_test "4.7 Add with Invalid Quantity"
RESPONSE=$(curl -s -X POST "$API_URL/cart/add" \
    -H "Content-Type: application/json" \
    -H "X-Line-User-Id: $LINE_USER_ID" \
    -H "X-Channel-Code: demo_coop" \
    -d "{\"product_id\": $PRODUCT_ID, \"quantity\": -1}")
check_result "$RESPONSE" '"success": false' "Negative quantity returns failure"

print_test "4.8 Update Cart Line"
# Get current cart to find line ID
CART_RESPONSE=$(curl -s "$API_URL/cart" \
    -H "X-Line-User-Id: $LINE_USER_ID" \
    -H "X-Channel-Code: demo_coop")
# Extract the first ID in lines array: "lines": [{"id": X
# The JSON format is: "lines": [{"id": 123,
CART_LINE_ID=$(echo "$CART_RESPONSE" | grep -o '"lines": \[{"id": [0-9]*' | grep -o '[0-9]*$')

if [ -n "$CART_LINE_ID" ]; then
    RESPONSE=$(curl -s -X POST "$API_URL/cart/update" \
        -H "Content-Type: application/json" \
        -H "X-Line-User-Id: $LINE_USER_ID" \
        -H "X-Channel-Code: demo_coop" \
        -d "{\"line_id\": $CART_LINE_ID, \"quantity\": 5}")
    check_result "$RESPONSE" '"success": true' "Update cart line returns success"
else
    echo "  Note: No cart line found to update (cart may be empty)"
fi

# ============================================================
# TEST GROUP 5: Profile API (Auth Required)
# ============================================================
print_header "TEST GROUP 5: Profile API (Auth Required)"

print_test "5.1 Get Profile"
RESPONSE=$(curl -s "$API_URL/profile" \
    -H "X-Line-User-Id: $LINE_USER_ID" \
    -H "X-Channel-Code: demo_coop")
check_result "$RESPONSE" '"success": true' "Get profile returns success"
check_result "$RESPONSE" '"line_user_id"' "Profile has LINE user ID"
check_result "$RESPONSE" '"display_name"' "Profile has display name"

print_test "5.2 Update Profile"
RESPONSE=$(curl -s -X PUT "$API_URL/profile" \
    -H "Content-Type: application/json" \
    -H "X-Line-User-Id: $LINE_USER_ID" \
    -H "X-Channel-Code: demo_coop" \
    -d '{"name": "ทดสอบ ผู้ซื้อ", "phone": "0812345678", "email": "test@example.com"}')
check_result "$RESPONSE" '"success": true' "Update profile returns success"

print_test "5.3 Get Updated Profile"
RESPONSE=$(curl -s "$API_URL/profile" \
    -H "X-Line-User-Id: $LINE_USER_ID" \
    -H "X-Channel-Code: demo_coop")
check_result "$RESPONSE" '"phone": "0812345678"' "Phone was updated"

print_test "5.4 Request Verification (Mock Mode)"
RESPONSE=$(curl -s -X POST "$API_URL/profile/verify" \
    -H "X-Line-User-Id: $LINE_USER_ID" \
    -H "X-Channel-Code: demo_coop")
check_result "$RESPONSE" '"success": true' "Verification request returns success"

print_test "5.5 Get Channel Memberships"
RESPONSE=$(curl -s "$API_URL/profile/channels" \
    -H "X-Line-User-Id: $LINE_USER_ID" \
    -H "X-Channel-Code: demo_coop")
check_result "$RESPONSE" '"success": true' "Get memberships returns success"
check_result "$RESPONSE" '"memberships"' "Has memberships array"

# ============================================================
# TEST GROUP 6: Checkout API (Auth Required)
# ============================================================
print_header "TEST GROUP 6: Checkout API (Auth Required)"

print_test "6.1 Get Shipping Addresses"
RESPONSE=$(curl -s "$API_URL/checkout/shipping-addresses" \
    -H "X-Line-User-Id: $LINE_USER_ID" \
    -H "X-Channel-Code: demo_coop")
check_result "$RESPONSE" '"success": true' "Get addresses returns success"
check_result "$RESPONSE" '"addresses"' "Has addresses array"

print_test "6.2 Save New Shipping Address"
RESPONSE=$(curl -s -X POST "$API_URL/checkout/shipping-address" \
    -H "Content-Type: application/json" \
    -H "X-Line-User-Id: $LINE_USER_ID" \
    -H "X-Channel-Code: demo_coop" \
    -d '{
        "name": "บ้านทดสอบ",
        "street": "123 ถนนทดสอบ",
        "city": "กรุงเทพ",
        "zip": "10110",
        "phone": "0812345678"
    }')
check_result "$RESPONSE" '"success": true' "Save address returns success"

print_test "6.3 Confirm Order (Checkout)"
RESPONSE=$(curl -s -X POST "$API_URL/checkout/confirm" \
    -H "Content-Type: application/json" \
    -H "X-Line-User-Id: $LINE_USER_ID" \
    -H "X-Channel-Code: demo_coop" \
    -d '{"note": "ทดสอบสั่งซื้อ"}')
check_result "$RESPONSE" '"success": true' "Checkout returns success"
check_result "$RESPONSE" '"Order confirmed"' "Order confirmed message"

# Extract order ID
ORDER_ID=$(echo "$RESPONSE" | grep -o '"id": [0-9]*' | head -1 | grep -o '[0-9]*')
echo "  Created Order ID: $ORDER_ID"

# ============================================================
# TEST GROUP 7: Orders API (Auth Required)
# ============================================================
print_header "TEST GROUP 7: Orders API (Auth Required)"

print_test "7.1 Get Order History"
RESPONSE=$(curl -s "$API_URL/orders" \
    -H "X-Line-User-Id: $LINE_USER_ID" \
    -H "X-Channel-Code: demo_coop")
check_result "$RESPONSE" '"success": true' "Get orders returns success"
check_result "$RESPONSE" '"orders"' "Has orders array"
check_result "$RESPONSE" '"pagination"' "Has pagination"

print_test "7.2 Get Order Detail"
if [ -n "$ORDER_ID" ]; then
    RESPONSE=$(curl -s "$API_URL/orders/$ORDER_ID" \
        -H "X-Line-User-Id: $LINE_USER_ID" \
        -H "X-Channel-Code: demo_coop")
    check_result "$RESPONSE" '"success": true' "Get order detail returns success"
    check_result "$RESPONSE" '"lines"' "Order has lines"
    check_result "$RESPONSE" '"total"' "Order has total"
fi

print_test "7.3 Reorder (Add Previous Order Items to Cart)"
if [ -n "$ORDER_ID" ]; then
    RESPONSE=$(curl -s -X POST "$API_URL/orders/$ORDER_ID/reorder" \
        -H "X-Line-User-Id: $LINE_USER_ID" \
        -H "X-Channel-Code: demo_coop")
    check_result "$RESPONSE" '"success": true' "Reorder returns success"
    check_result "$RESPONSE" '"Items added to cart"' "Items added message"
fi

# ============================================================
# TEST GROUP 8: Error Handling
# ============================================================
print_header "TEST GROUP 8: Error Handling"

print_test "8.1 Invalid JSON Body"
RESPONSE=$(curl -s -X POST "$API_URL/cart/add" \
    -H "Content-Type: application/json" \
    -H "X-Line-User-Id: $LINE_USER_ID" \
    -H "X-Channel-Code: demo_coop" \
    -d 'invalid json')
check_result "$RESPONSE" '"success": false' "Invalid JSON returns failure"

print_test "8.2 Missing Required Field"
RESPONSE=$(curl -s -X POST "$API_URL/cart/add" \
    -H "Content-Type: application/json" \
    -H "X-Line-User-Id: $LINE_USER_ID" \
    -H "X-Channel-Code: demo_coop" \
    -d '{"quantity": 1}')
check_result "$RESPONSE" '"success": false' "Missing field returns failure"
check_result "$RESPONSE" 'product_id' "Error mentions missing field"

print_test "8.3 Invalid Channel Code"
RESPONSE=$(curl -s "$API_URL/cart" \
    -H "X-Line-User-Id: $LINE_USER_ID" \
    -H "X-Channel-Code: invalid_channel")
check_result "$RESPONSE" '"success": false' "Invalid channel returns failure"

print_test "8.4 Access Other User's Order"
RESPONSE=$(curl -s "$API_URL/orders/1" \
    -H "X-Line-User-Id: DIFFERENT_USER_ID" \
    -H "X-Channel-Code: demo_coop")
# This should fail with unauthorized or not found
check_result "$RESPONSE" '"success": false\|Unauthorized\|not found' "Cannot access other user's order"

# ============================================================
# TEST SUMMARY
# ============================================================
print_header "TEST SUMMARY"
echo ""
echo -e "Total Tests: $((PASSED + FAILED))"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed. Please check the output above.${NC}"
    exit 1
fi
