/**
 * Seller LIFF API Client
 * Communicates with /api/line-seller/ endpoints
 */
const SellerAPI = {
    accessToken: null,
    lineUserId: null,

    setAuth(accessToken, lineUserId) {
        this.accessToken = accessToken;
        this.lineUserId = lineUserId;
    },

    getHeaders() {
        const headers = {
            'Content-Type': 'application/json',
            'X-Channel-Code': Config.CHANNEL_CODE,
        };
        if (Config.MOCK_MODE) {
            headers['X-Line-User-Id'] = this.lineUserId;
        } else if (this.accessToken) {
            headers['Authorization'] = `Bearer ${this.accessToken}`;
        }
        return headers;
    },

    async request(endpoint, options = {}) {
        const url = `${Config.API_BASE_URL}/api/line-seller${endpoint}`;
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

    // ==================== Dashboard ====================

    async getDashboard() {
        return this.request('/dashboard');
    },

    async getReports(period = 'today') {
        return this.request(`/reports?period=${period}`);
    },

    // ==================== Orders ====================

    async getOrders(params = {}) {
        const query = new URLSearchParams();
        if (params.page) query.set('page', params.page);
        if (params.limit) query.set('limit', params.limit);
        if (params.status && params.status !== 'all') query.set('status', params.status);
        const qs = query.toString();
        return this.request(`/orders${qs ? '?' + qs : ''}`);
    },

    async getOrderDetail(lineId) {
        return this.request(`/orders/${lineId}`);
    },

    async approveOrder(lineId) {
        return this.request(`/orders/${lineId}/approve`, { method: 'POST' });
    },

    async shipOrder(lineId) {
        return this.request(`/orders/${lineId}/ship`, { method: 'POST' });
    },

    async markOrderDone(lineId) {
        return this.request(`/orders/${lineId}/done`, { method: 'POST' });
    },

    async cancelOrder(lineId) {
        return this.request(`/orders/${lineId}/cancel`, { method: 'POST' });
    },

    // ==================== Products ====================

    async getProducts(params = {}) {
        const query = new URLSearchParams();
        if (params.page) query.set('page', params.page);
        if (params.limit) query.set('limit', params.limit);
        if (params.status && params.status !== 'all') query.set('status', params.status);
        if (params.search) query.set('search', params.search);
        const qs = query.toString();
        return this.request(`/products${qs ? '?' + qs : ''}`);
    },

    async getProduct(productId) {
        return this.request(`/products/${productId}`);
    },

    async createProduct(data) {
        return this.request('/products', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    },

    async updateProduct(productId, data) {
        return this.request(`/products/${productId}`, {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    },

    async submitProduct(productId) {
        return this.request(`/products/${productId}/submit`, { method: 'POST' });
    },

    async getCategories() {
        return this.request('/categories');
    },

    // ==================== Product Images ====================

    async getProductImages(productId) {
        return this.request(`/products/${productId}/images`);
    },

    async uploadProductImages(productId, images) {
        return this.request(`/products/${productId}/images`, {
            method: 'POST',
            body: JSON.stringify({ images }),
        });
    },

    async deleteProductImage(productId, imageId) {
        return this.request(`/products/${productId}/images/${imageId}`, {
            method: 'DELETE',
        });
    },

    async reorderProductImages(productId, imageIds) {
        return this.request(`/products/${productId}/images/reorder`, {
            method: 'PUT',
            body: JSON.stringify({ image_ids: imageIds }),
        });
    },

    // ==================== Profile & Shop ====================

    async getProfile() {
        return this.request('/profile');
    },

    async updateProfile(data) {
        return this.request('/profile', {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    },

    async getShop() {
        return this.request('/shop');
    },

    async updateShop(data) {
        return this.request('/shop', {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    },

    async getEarnings(params = {}) {
        const query = new URLSearchParams();
        if (params.page) query.set('page', params.page);
        if (params.limit) query.set('limit', params.limit);
        const qs = query.toString();
        return this.request(`/earnings${qs ? '?' + qs : ''}`);
    },

    // ==================== Wallet ====================

    async getWallet() {
        return this.request('/wallet');
    },

    async getWalletTransactions(params = {}) {
        const query = new URLSearchParams();
        if (params.page) query.set('page', params.page);
        if (params.limit) query.set('limit', params.limit);
        if (params.type && params.type !== 'all') query.set('type', params.type);
        const qs = query.toString();
        return this.request(`/wallet/transactions${qs ? '?' + qs : ''}`);
    },

    async getWalletTransaction(id) {
        return this.request(`/wallet/transactions/${id}`);
    },

    async requestWithdrawal(data) {
        return this.request('/wallet/withdraw', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    },

    async getWithdrawals(params = {}) {
        const query = new URLSearchParams();
        if (params.page) query.set('page', params.page);
        if (params.limit) query.set('limit', params.limit);
        if (params.state) query.set('state', params.state);
        const qs = query.toString();
        return this.request(`/wallet/withdrawals${qs ? '?' + qs : ''}`);
    },

    async getWithdrawal(id) {
        return this.request(`/wallet/withdrawals/${id}`);
    },

    async cancelWithdrawal(id) {
        return this.request(`/wallet/withdrawals/${id}/cancel`, { method: 'POST' });
    },
};
