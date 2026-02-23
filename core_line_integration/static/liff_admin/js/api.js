/**
 * Admin LIFF API Client
 * Communicates with /api/line-admin/ endpoints
 */
const AdminAPI = {
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
        const url = `${Config.API_BASE_URL}/api/line-admin${endpoint}`;
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

    // ==================== Members ====================

    async getMembers(params = {}) {
        const query = new URLSearchParams();
        if (params.page) query.set('page', params.page);
        if (params.limit) query.set('limit', params.limit);
        if (params.search) query.set('search', params.search);
        if (params.type && params.type !== 'all') query.set('type', params.type);
        const qs = query.toString();
        return this.request(`/members${qs ? '?' + qs : ''}`);
    },

    async getMemberDetail(memberId) {
        return this.request(`/members/${memberId}`);
    },

    // ==================== Sellers ====================

    async getSellers(params = {}) {
        const query = new URLSearchParams();
        if (params.page) query.set('page', params.page);
        if (params.limit) query.set('limit', params.limit);
        if (params.state && params.state !== 'all') query.set('state', params.state);
        if (params.search) query.set('search', params.search);
        const qs = query.toString();
        return this.request(`/sellers${qs ? '?' + qs : ''}`);
    },

    async getSellerDetail(sellerId) {
        return this.request(`/sellers/${sellerId}`);
    },

    async approveSeller(sellerId) {
        return this.request(`/sellers/${sellerId}/approve`, { method: 'POST' });
    },

    async denySeller(sellerId) {
        return this.request(`/sellers/${sellerId}/deny`, { method: 'POST' });
    },

    // ==================== Orders ====================

    async getOrders(params = {}) {
        const query = new URLSearchParams();
        if (params.page) query.set('page', params.page);
        if (params.limit) query.set('limit', params.limit);
        if (params.status && params.status !== 'all') query.set('status', params.status);
        if (params.search) query.set('search', params.search);
        const qs = query.toString();
        return this.request(`/orders${qs ? '?' + qs : ''}`);
    },

    async getOrderDetail(orderId) {
        return this.request(`/orders/${orderId}`);
    },

    async getOrderStats() {
        return this.request('/orders/stats');
    },

    // ==================== Notifications ====================

    async sendNotification(data) {
        return this.request('/notifications/send', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    },

    async getNotificationHistory(params = {}) {
        const query = new URLSearchParams();
        if (params.page) query.set('page', params.page);
        if (params.limit) query.set('limit', params.limit);
        if (params.type) query.set('type', params.type);
        const qs = query.toString();
        return this.request(`/notifications/history${qs ? '?' + qs : ''}`);
    },

    // ==================== Settings ====================

    async getSettings() {
        return this.request('/settings');
    },

    async updateSettings(data) {
        return this.request('/settings', {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    },

    // ==================== Wallets ====================

    async getWallets(params = {}) {
        const query = new URLSearchParams();
        if (params.page) query.set('page', params.page);
        if (params.limit) query.set('limit', params.limit);
        if (params.search) query.set('search', params.search);
        const qs = query.toString();
        return this.request(`/wallets${qs ? '?' + qs : ''}`);
    },

    async getWalletDetail(walletId) {
        return this.request(`/wallets/${walletId}`);
    },

    async getWithdrawals(params = {}) {
        const query = new URLSearchParams();
        if (params.page) query.set('page', params.page);
        if (params.limit) query.set('limit', params.limit);
        if (params.state) query.set('state', params.state);
        const qs = query.toString();
        return this.request(`/withdrawals${qs ? '?' + qs : ''}`);
    },

    async approveWithdrawal(id) {
        return this.request(`/withdrawals/${id}/approve`, { method: 'POST' });
    },

    async rejectWithdrawal(id, reason = '') {
        return this.request(`/withdrawals/${id}/reject`, {
            method: 'POST',
            body: JSON.stringify({ reason }),
        });
    },

    async completeWithdrawal(id) {
        return this.request(`/withdrawals/${id}/complete`, { method: 'POST' });
    },

    // ==================== Admin Team ====================

    async getMyManagerStatus() {
        return this.request('/team/my-status');
    },

    async getTeam(params = {}) {
        const query = new URLSearchParams();
        if (params.state) query.set('state', params.state);
        if (params.page) query.set('page', params.page);
        if (params.limit) query.set('limit', params.limit);
        const qs = query.toString();
        return this.request(`/team${qs ? '?' + qs : ''}`);
    },

    async getTeamCandidates(search) {
        const query = new URLSearchParams();
        if (search) query.set('search', search);
        query.set('limit', '20');
        return this.request(`/team/candidates?${query.toString()}`);
    },

    async inviteAdmin(partnerId, notes = '') {
        return this.request('/team/invite', {
            method: 'POST',
            body: JSON.stringify({ partner_id: partnerId, notes }),
        });
    },

    async revokeAdmin(memberId, reason = '') {
        return this.request(`/team/${memberId}/revoke`, {
            method: 'POST',
            body: JSON.stringify({ reason }),
        });
    },
};
