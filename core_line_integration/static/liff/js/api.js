/**
 * API Client for LINE Marketplace
 */
const API = {
    accessToken: null,
    lineUserId: null,

    /**
     * Set authentication credentials
     */
    setAuth(accessToken, lineUserId) {
        this.accessToken = accessToken;
        this.lineUserId = lineUserId;
    },

    /**
     * Get headers for API requests
     */
    getHeaders() {
        const headers = {
            'Content-Type': 'application/json',
            'X-Channel-Code': Config.CHANNEL_CODE,
        };

        if (Config.MOCK_MODE) {
            // Mock mode uses X-Line-User-Id
            headers['X-Line-User-Id'] = this.lineUserId;
        } else {
            // Production mode uses Bearer token
            headers['Authorization'] = `Bearer ${this.accessToken}`;
        }

        return headers;
    },

    /**
     * Make API request
     */
    async request(endpoint, options = {}) {
        const url = `${Config.API_BASE_URL}/api/line-buyer${endpoint}`;

        const response = await fetch(url, {
            ...options,
            headers: {
                ...this.getHeaders(),
                ...options.headers,
            },
        });

        const data = await response.json();

        if (!data.success) {
            throw new Error(data.error?.message || 'API request failed');
        }

        return data.data;
    },

    // ==================== Health Check ====================

    async healthCheck() {
        return this.request('/health');
    },

    // ==================== Products ====================

    async getProducts(params = {}) {
        const query = new URLSearchParams();

        if (params.page) query.set('page', params.page);
        if (params.limit) query.set('limit', params.limit);
        if (params.category) query.set('category', params.category);
        if (params.search) query.set('search', params.search);
        if (params.sort) query.set('sort', params.sort);

        const queryStr = query.toString();
        return this.request(`/products${queryStr ? '?' + queryStr : ''}`);
    },

    async getProduct(productId) {
        return this.request(`/products/${productId}`);
    },

    async getCategories() {
        return this.request('/categories');
    },

    async getFeaturedProducts(limit = 8) {
        return this.request(`/products?limit=${limit}&sort=-id`);
    },

    // ==================== Cart ====================

    async getCart() {
        return this.request('/cart');
    },

    async addToCart(productId, quantity = 1) {
        return this.request('/cart/add', {
            method: 'POST',
            body: JSON.stringify({ product_id: productId, quantity }),
        });
    },

    async updateCartLine(lineId, quantity) {
        return this.request('/cart/update', {
            method: 'POST',
            body: JSON.stringify({ line_id: lineId, quantity }),
        });
    },

    async removeFromCart(lineId) {
        return this.request('/cart/remove', {
            method: 'POST',
            body: JSON.stringify({ line_id: lineId }),
        });
    },

    async clearCart() {
        return this.request('/cart/clear', {
            method: 'POST',
        });
    },

    // ==================== Checkout ====================

    async getShippingAddresses() {
        return this.request('/checkout/shipping-addresses');
    },

    async saveShippingAddress(address) {
        return this.request('/checkout/shipping-address', {
            method: 'POST',
            body: JSON.stringify(address),
        });
    },

    async confirmOrder(shippingAddressId = null, note = '') {
        return this.request('/checkout/confirm', {
            method: 'POST',
            body: JSON.stringify({
                shipping_address_id: shippingAddressId,
                note: note,
            }),
        });
    },

    // ==================== Orders ====================

    async getOrders(params = {}) {
        const query = new URLSearchParams();

        if (params.page) query.set('page', params.page);
        if (params.limit) query.set('limit', params.limit);
        if (params.state) query.set('state', params.state);

        const queryStr = query.toString();
        return this.request(`/orders${queryStr ? '?' + queryStr : ''}`);
    },

    async getOrder(orderId) {
        return this.request(`/orders/${orderId}`);
    },

    async cancelOrder(orderId) {
        return this.request(`/orders/${orderId}/cancel`, {
            method: 'POST',
        });
    },

    async reorder(orderId) {
        return this.request(`/orders/${orderId}/reorder`, {
            method: 'POST',
        });
    },

    // ==================== Profile ====================

    async getProfile() {
        return this.request('/profile');
    },

    async updateProfile(data) {
        return this.request('/profile', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    },

    // ==================== Addresses ====================

    async getAddresses() {
        return this.request('/addresses');
    },

    async createAddress(address) {
        return this.request('/addresses', {
            method: 'POST',
            body: JSON.stringify(address),
        });
    },

    async updateAddress(addressId, address) {
        return this.request(`/addresses/${addressId}`, {
            method: 'PUT',
            body: JSON.stringify(address),
        });
    },

    async deleteAddress(addressId) {
        return this.request(`/addresses/${addressId}`, {
            method: 'DELETE',
        });
    },

    async setDefaultAddress(addressId) {
        return this.request(`/addresses/${addressId}/set-default`, {
            method: 'POST',
        });
    },

    async getProvinces() {
        return this.request('/provinces');
    },

    async calculateShippingCost(addressId, orderTotal) {
        return this.request('/shipping-cost', {
            method: 'POST',
            body: JSON.stringify({
                address_id: addressId,
                order_total: orderTotal,
            }),
        });
    },

    // ==================== Seller Application ====================

    async getSellerStatus() {
        return this.request('/seller/status');
    },

    async applyAsSeller(shopName = '') {
        return this.request('/seller/apply', {
            method: 'POST',
            body: JSON.stringify({ shop_name: shopName }),
        });
    },
};
