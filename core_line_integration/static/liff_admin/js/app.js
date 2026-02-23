/**
 * Admin LIFF App - Main Application Logic
 */
const AdminApp = {
    user: null,
    currentPage: 'dashboard',
    membersPage: 1,
    ordersPage: 1,
    notificationsPage: 1,
    withdrawalsPage: 1,
    currentMemberSearch: '',
    currentOrderFilter: 'all',
    currentSellerFilter: 'all',
    currentWithdrawalFilter: 'all',
    currentMessageType: 'text',
    viewMode: 'members', // 'members' or 'sellers' on members page
    isManager: false,
    currentTeamFilter: 'active',
    teamPage: 1,

    // ==================== Initialization ====================

    async init() {
        // Deep-link: LIFF SDK loads page twice — first with liff.state, then reloads with empty params.
        // Save target page to sessionStorage on first load so it survives the reload.
        const _initParams = new URLSearchParams(window.location.search);
        let _targetPage = _initParams.get('page') || null;
        if (!_targetPage) {
            const _liffState = _initParams.get('liff.state');
            if (_liffState) {
                const _stateParams = new URLSearchParams(_liffState.replace(/^\?/, ''));
                _targetPage = _stateParams.get('page') || null;
            }
        }
        if (_targetPage) {
            sessionStorage.setItem('liff_deep_link', _targetPage);
        }
        console.log('Deep-link target:', _targetPage, 'stored:', sessionStorage.getItem('liff_deep_link'), 'URL:', window.location.href);

        try {
            if (Config.MOCK_MODE) {
                await this.initMockMode();
            } else {
                await this.initLiff();
            }
            this.setupEventListeners();
            await Promise.all([
                this.loadDashboard(),
                this.checkManagerStatus(),
            ]);

            // Deep-link routing (read from sessionStorage to survive LIFF reload)
            const _deepLink = sessionStorage.getItem('liff_deep_link');
            if (_deepLink) {
                sessionStorage.removeItem('liff_deep_link');
                if (document.getElementById(`page-${_deepLink}`)) {
                    this.showPage(_deepLink);
                }
            }
        } catch (error) {
            console.error('Init error:', error);
            this.showToast('Failed to initialize app', 'error');
        } finally {
            document.getElementById('loading').classList.add('hidden');
            document.getElementById('app').classList.remove('hidden');
        }
    },

    async initLiff() {
        await liff.init({ liffId: Config.LIFF_ID });
        if (!liff.isLoggedIn()) {
            liff.login();
            return;
        }
        const profile = await liff.getProfile();
        const accessToken = liff.getAccessToken();
        this.user = {
            userId: profile.userId,
            displayName: profile.displayName,
            pictureUrl: profile.pictureUrl || Config.DEFAULT_AVATAR,
        };
        AdminAPI.setAuth(accessToken, profile.userId);
        this.updateUserUI();
    },

    async initMockMode() {
        this.user = Config.MOCK_USER;
        this.user.pictureUrl = this.user.pictureUrl || Config.DEFAULT_AVATAR;
        AdminAPI.setAuth(null, this.user.userId);
        this.updateUserUI();
    },

    updateUserUI() {
        document.getElementById('adminName').textContent = this.user.displayName;
    },

    setupEventListeners() {
        // Bottom navigation
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.addEventListener('click', () => this.showPage(btn.dataset.page));
        });

        // Message type buttons
        document.querySelectorAll('.msg-type-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.msg-type-btn').forEach(b => {
                    b.classList.remove('active', 'admin-blue', 'text-white');
                });
                btn.classList.add('active', 'admin-blue', 'text-white');
                this.currentMessageType = btn.dataset.type;
            });
        });

        // Member search with debounce
        let searchTimer;
        const searchInput = document.getElementById('memberSearch');
        if (searchInput) {
            searchInput.addEventListener('input', () => {
                clearTimeout(searchTimer);
                searchTimer = setTimeout(() => {
                    this.currentMemberSearch = searchInput.value;
                    this.membersPage = 1;
                    if (this.viewMode === 'members') {
                        this.loadMembers();
                    } else {
                        this.loadSellers();
                    }
                }, 300);
            });
        }
    },

    // ==================== Page Navigation ====================

    showPage(pageName) {
        document.querySelectorAll('.page').forEach(p => p.classList.add('hidden'));
        const page = document.getElementById(`page-${pageName}`);
        if (page) page.classList.remove('hidden');

        document.querySelectorAll('.nav-btn').forEach(btn => {
            const isActive = btn.dataset.page === pageName;
            btn.classList.toggle('active', isActive);
            btn.classList.toggle('admin-blue-text', isActive);
        });

        this.currentPage = pageName;

        switch (pageName) {
            case 'dashboard': this.loadDashboard(); break;
            case 'members': this.loadMembersPage(); break;
            case 'orders': this.loadOrdersPage(); break;
            case 'withdrawals': this.loadWithdrawals(); break;
            case 'notifications': this.loadNotificationHistory(); break;
            case 'team': this.loadTeam(); break;
            case 'settings': this.loadSettings(); break;
        }
    },

    // ==================== Dashboard ====================

    async loadDashboard() {
        try {
            const data = await AdminAPI.getDashboard();
            const stats = data.stats;

            document.getElementById('stat-members').textContent = this.formatNumber(stats.total_members);
            document.getElementById('stat-orders').textContent = this.formatNumber(stats.today_orders);
            document.getElementById('stat-sellers').textContent = this.formatNumber(stats.active_sellers);
            document.getElementById('stat-revenue').textContent = `${stats.currency}${this.formatNumber(stats.today_revenue)}`;

            this.renderAlerts(data.alerts || []);
        } catch (error) {
            console.error('Dashboard error:', error);
            this.showToast('Failed to load dashboard', 'error');
        }
    },

    renderAlerts(alerts) {
        const container = document.getElementById('alerts-container');
        if (!alerts.length) {
            container.innerHTML = '<div class="text-center text-gray-400 py-4">No alerts</div>';
            return;
        }
        const typeStyles = {
            warning: { bg: 'bg-yellow-50', border: 'border-yellow-400', icon: 'text-yellow-400', title: 'text-yellow-800', sub: 'text-yellow-600' },
            info: { bg: 'bg-blue-50', border: 'border-blue-400', icon: 'text-blue-400', title: 'text-blue-800', sub: 'text-blue-600' },
            error: { bg: 'bg-red-50', border: 'border-red-400', icon: 'text-red-400', title: 'text-red-800', sub: 'text-red-600' },
        };
        container.innerHTML = alerts.map(alert => {
            const s = typeStyles[alert.type] || typeStyles.info;
            return `
                <div class="${s.bg} border-l-4 ${s.border} p-4 rounded-r-lg">
                    <div class="flex items-center">
                        <i class="fas ${alert.icon} ${s.icon} mr-3"></i>
                        <div>
                            <p class="font-medium ${s.title}">${this.escapeHtml(alert.title)}</p>
                            <p class="text-sm ${s.sub}">${this.escapeHtml(alert.subtitle)}</p>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    },

    // ==================== Members Page ====================

    loadMembersPage() {
        if (this.viewMode === 'sellers') {
            this.loadSellers();
        } else {
            this.loadMembers();
        }
    },

    switchMemberView(mode) {
        this.viewMode = mode;
        this.membersPage = 1;

        // Update tab buttons
        document.getElementById('tab-members').classList.toggle('admin-blue', mode === 'members');
        document.getElementById('tab-members').classList.toggle('text-white', mode === 'members');
        document.getElementById('tab-members').classList.toggle('bg-gray-200', mode !== 'members');
        document.getElementById('tab-sellers').classList.toggle('admin-blue', mode === 'sellers');
        document.getElementById('tab-sellers').classList.toggle('text-white', mode === 'sellers');
        document.getElementById('tab-sellers').classList.toggle('bg-gray-200', mode !== 'sellers');

        // Show/hide seller filters
        const sellerFilters = document.getElementById('seller-filters');
        if (sellerFilters) {
            sellerFilters.classList.toggle('hidden', mode !== 'sellers');
        }

        this.loadMembersPage();
    },

    async loadMembers() {
        const container = document.getElementById('member-list');
        container.innerHTML = '<div class="text-center py-8"><div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div></div>';

        try {
            const data = await AdminAPI.getMembers({
                page: this.membersPage,
                limit: Config.MEMBERS_PER_PAGE,
                search: this.currentMemberSearch,
            });

            document.getElementById('member-count').textContent = `${data.pagination.total} members`;
            this.renderMemberList(data.members || []);
            this.renderPagination(container, data.pagination, (page) => {
                this.membersPage = page;
                this.loadMembers();
            });
        } catch (error) {
            console.error('Members error:', error);
            container.innerHTML = '<div class="text-center text-red-500 py-8">Failed to load members</div>';
        }
    },

    renderMemberList(members) {
        const container = document.getElementById('member-list');
        if (!members.length) {
            container.innerHTML = '<div class="text-center text-gray-400 py-8">No members found</div>';
            return;
        }
        container.innerHTML = members.map(m => `
            <div class="bg-white rounded-xl p-4 shadow flex items-center justify-between cursor-pointer" onclick="AdminApp.showMemberDetail(${m.id})">
                <div class="flex items-center space-x-3">
                    <div class="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center overflow-hidden">
                        ${m.picture_url
                            ? `<img src="${m.picture_url}" class="w-full h-full object-cover">`
                            : '<i class="fas fa-user text-gray-400"></i>'}
                    </div>
                    <div>
                        <p class="font-medium">${this.escapeHtml(m.display_name)}</p>
                        <p class="text-xs text-gray-500">${m.order_count} orders | ${m.is_following ? 'Following' : 'Unfollowed'}</p>
                    </div>
                </div>
                <span class="px-2 py-1 rounded-full text-xs ${m.is_following ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}">
                    ${m.member_type || 'buyer'}
                </span>
            </div>
        `).join('');
    },

    async showMemberDetail(memberId) {
        try {
            const data = await AdminAPI.getMemberDetail(memberId);

            const ordersHtml = (data.recent_orders || []).map(o => `
                <div class="flex justify-between items-center py-2 border-b last:border-0">
                    <div>
                        <p class="text-sm font-medium">${this.escapeHtml(o.name)}</p>
                        <p class="text-xs text-gray-400">${this.formatDate(o.date)}</p>
                    </div>
                    <span class="font-semibold text-green-600">${o.currency}${this.formatNumber(o.total)}</span>
                </div>
            `).join('') || '<p class="text-gray-400 text-sm">No orders</p>';

            const sellerHtml = data.seller_info ? `
                <div class="mt-4 p-3 bg-purple-50 rounded-lg">
                    <p class="font-medium text-purple-800">Seller: ${this.escapeHtml(data.seller_info.name)}</p>
                    <p class="text-sm text-purple-600">Status: ${data.seller_info.state} | Products: ${data.seller_info.product_count}</p>
                </div>
            ` : '';

            this.showModal('member-detail-modal', `
                <div class="flex items-center space-x-4 mb-4">
                    <div class="w-16 h-16 rounded-full bg-gray-200 flex items-center justify-center overflow-hidden">
                        ${data.picture_url
                            ? `<img src="${data.picture_url}" class="w-full h-full object-cover">`
                            : '<i class="fas fa-user text-2xl text-gray-400"></i>'}
                    </div>
                    <div>
                        <h3 class="text-lg font-bold">${this.escapeHtml(data.display_name)}</h3>
                        <p class="text-sm text-gray-500">${data.member_type || 'buyer'} | ${data.is_following ? 'Following' : 'Unfollowed'}</p>
                    </div>
                </div>

                ${data.partner ? `
                    <div class="mb-4">
                        <h4 class="font-semibold text-sm mb-2">Contact</h4>
                        <p class="text-sm text-gray-600">${this.escapeHtml(data.partner.name)}</p>
                        <p class="text-sm text-gray-600">${this.escapeHtml(data.partner.email)} | ${this.escapeHtml(data.partner.phone)}</p>
                    </div>
                ` : ''}

                <div class="mb-4">
                    <div class="flex justify-between mb-2">
                        <span class="text-sm text-gray-500">Orders</span>
                        <span class="font-semibold">${data.order_count}</span>
                    </div>
                    <div class="flex justify-between mb-2">
                        <span class="text-sm text-gray-500">Total Spent</span>
                        <span class="font-semibold text-green-600">฿${this.formatNumber(data.total_spent)}</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-sm text-gray-500">Joined</span>
                        <span class="text-sm">${this.formatDate(data.follow_date)}</span>
                    </div>
                </div>

                ${sellerHtml}

                <div class="mt-4">
                    <h4 class="font-semibold text-sm mb-2">Recent Orders</h4>
                    ${ordersHtml}
                </div>
            `);
        } catch (error) {
            console.error('Member detail error:', error);
            this.showToast('Failed to load member details', 'error');
        }
    },

    // ==================== Sellers ====================

    async loadSellers(state) {
        if (state !== undefined) {
            this.currentSellerFilter = state;
        }
        const container = document.getElementById('member-list');
        container.innerHTML = '<div class="text-center py-8"><div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div></div>';

        try {
            const data = await AdminAPI.getSellers({
                page: this.membersPage,
                limit: Config.MEMBERS_PER_PAGE,
                state: this.currentSellerFilter,
                search: this.currentMemberSearch,
            });

            // Update state counts
            const counts = data.state_counts || {};
            const countEl = document.getElementById('member-count');
            if (countEl) {
                countEl.textContent = `${data.pagination.total} sellers (${counts.pending || 0} pending)`;
            }

            this.renderSellerList(data.sellers || []);
            this.renderPagination(container, data.pagination, (page) => {
                this.membersPage = page;
                this.loadSellers();
            });
        } catch (error) {
            console.error('Sellers error:', error);
            container.innerHTML = '<div class="text-center text-red-500 py-8">Failed to load sellers</div>';
        }
    },

    renderSellerList(sellers) {
        const container = document.getElementById('member-list');
        if (!sellers.length) {
            container.innerHTML = '<div class="text-center text-gray-400 py-8">No sellers found</div>';
            return;
        }
        container.innerHTML = sellers.map(s => `
            <div class="bg-white rounded-xl p-4 shadow cursor-pointer" onclick="AdminApp.showSellerDetail(${s.id})">
                <div class="flex items-center justify-between">
                    <div class="flex items-center space-x-3">
                        <div class="w-10 h-10 rounded-full bg-purple-100 flex items-center justify-center">
                            <i class="fas fa-store text-purple-500"></i>
                        </div>
                        <div>
                            <p class="font-medium">${this.escapeHtml(s.name)}</p>
                            <p class="text-xs text-gray-500">${s.product_count} products${s.shop ? ' | ' + this.escapeHtml(s.shop.name) : ''}</p>
                        </div>
                    </div>
                    <span class="px-2 py-1 rounded-full text-xs ${this.getSellerStateClass(s.state)}">${s.state}</span>
                </div>
                ${s.state === 'pending' ? `
                    <div class="flex space-x-2 mt-3">
                        <button onclick="event.stopPropagation(); AdminApp.approveSeller(${s.id})" class="flex-1 bg-green-500 text-white py-2 rounded-lg text-sm font-medium">Approve</button>
                        <button onclick="event.stopPropagation(); AdminApp.denySeller(${s.id})" class="flex-1 bg-red-500 text-white py-2 rounded-lg text-sm font-medium">Deny</button>
                    </div>
                ` : ''}
            </div>
        `).join('');
    },

    async showSellerDetail(sellerId) {
        try {
            const data = await AdminAPI.getSellerDetail(sellerId);

            const productsHtml = (data.products || []).map(p => `
                <div class="flex justify-between items-center py-2 border-b last:border-0">
                    <div>
                        <p class="text-sm font-medium">${this.escapeHtml(p.name)}</p>
                        <span class="px-2 py-0.5 rounded-full text-xs ${this.getProductStatusClass(p.status)}">${p.status}</span>
                    </div>
                    <span class="font-semibold">฿${this.formatNumber(p.price)}</span>
                </div>
            `).join('') || '<p class="text-gray-400 text-sm">No products</p>';

            const actionsHtml = data.state === 'pending' ? `
                <div class="flex space-x-3 mt-6">
                    <button onclick="AdminApp.approveSeller(${data.id}); AdminApp.closeModal('member-detail-modal');" class="flex-1 bg-green-500 text-white py-3 rounded-lg font-semibold">Approve</button>
                    <button onclick="AdminApp.denySeller(${data.id}); AdminApp.closeModal('member-detail-modal');" class="flex-1 bg-red-500 text-white py-3 rounded-lg font-semibold">Deny</button>
                </div>
            ` : '';

            this.showModal('member-detail-modal', `
                <div class="flex items-center space-x-4 mb-4">
                    <div class="w-16 h-16 rounded-full bg-purple-100 flex items-center justify-center">
                        <i class="fas fa-store text-2xl text-purple-500"></i>
                    </div>
                    <div>
                        <h3 class="text-lg font-bold">${this.escapeHtml(data.name)}</h3>
                        <span class="px-2 py-1 rounded-full text-xs ${this.getSellerStateClass(data.state)}">${data.state}</span>
                    </div>
                </div>

                <div class="mb-4 space-y-2">
                    <div class="flex justify-between"><span class="text-sm text-gray-500">Email</span><span class="text-sm">${this.escapeHtml(data.email)}</span></div>
                    <div class="flex justify-between"><span class="text-sm text-gray-500">Phone</span><span class="text-sm">${this.escapeHtml(data.phone)}</span></div>
                    <div class="flex justify-between"><span class="text-sm text-gray-500">Products</span><span class="text-sm">${data.product_count}</span></div>
                    ${data.shop ? `<div class="flex justify-between"><span class="text-sm text-gray-500">Shop</span><span class="text-sm">${this.escapeHtml(data.shop.name)}</span></div>` : ''}
                    <div class="flex justify-between"><span class="text-sm text-gray-500">Joined</span><span class="text-sm">${this.formatDate(data.create_date)}</span></div>
                </div>

                <div class="mt-4">
                    <h4 class="font-semibold text-sm mb-2">Products</h4>
                    ${productsHtml}
                </div>

                ${actionsHtml}
            `);
        } catch (error) {
            console.error('Seller detail error:', error);
            this.showToast('Failed to load seller details', 'error');
        }
    },

    async approveSeller(sellerId) {
        try {
            await AdminAPI.approveSeller(sellerId);
            this.showToast('Seller approved successfully', 'success');
            this.loadSellers();
        } catch (error) {
            console.error('Approve seller error:', error);
            this.showToast(error.message || 'Failed to approve seller', 'error');
        }
    },

    async denySeller(sellerId) {
        try {
            await AdminAPI.denySeller(sellerId);
            this.showToast('Seller denied', 'success');
            this.loadSellers();
        } catch (error) {
            console.error('Deny seller error:', error);
            this.showToast(error.message || 'Failed to deny seller', 'error');
        }
    },

    // ==================== Orders ====================

    async loadOrdersPage() {
        await Promise.all([
            this.loadOrderStats(),
            this.loadOrders(),
        ]);
    },

    async loadOrderStats() {
        try {
            const stats = await AdminAPI.getOrderStats();
            document.getElementById('orders-pending').textContent = this.formatNumber(stats.draft + stats.sent);
            document.getElementById('orders-confirmed').textContent = this.formatNumber(stats.sale);
            document.getElementById('orders-shipped').textContent = '0'; // No shipped state in sale.order
            document.getElementById('orders-completed').textContent = this.formatNumber(stats.done);
        } catch (error) {
            console.error('Order stats error:', error);
        }
    },

    async loadOrders(status) {
        if (status !== undefined) {
            this.currentOrderFilter = status;
        }
        const container = document.getElementById('order-list');
        container.innerHTML = '<div class="text-center py-8"><div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div></div>';

        try {
            const data = await AdminAPI.getOrders({
                page: this.ordersPage,
                limit: Config.ORDERS_PER_PAGE,
                status: this.currentOrderFilter,
            });

            this.renderOrderList(data.orders || []);
            this.renderPagination(container, data.pagination, (page) => {
                this.ordersPage = page;
                this.loadOrders();
            });
        } catch (error) {
            console.error('Orders error:', error);
            container.innerHTML = '<div class="text-center text-red-500 py-8">Failed to load orders</div>';
        }
    },

    renderOrderList(orders) {
        const container = document.getElementById('order-list');
        if (!orders.length) {
            container.innerHTML = '<div class="text-center text-gray-400 py-8">No orders found</div>';
            return;
        }
        container.innerHTML = orders.map(o => `
            <div class="bg-white rounded-xl p-4 shadow cursor-pointer" onclick="AdminApp.showOrderDetail(${o.id})">
                <div class="flex justify-between items-start mb-2">
                    <div>
                        <p class="font-semibold">${this.escapeHtml(o.name)}</p>
                        <p class="text-sm text-gray-500">${this.escapeHtml(o.customer.name)}</p>
                    </div>
                    <span class="px-2 py-1 rounded-full text-xs ${this.getOrderStateClass(o.state)}">${this.escapeHtml(o.state_display)}</span>
                </div>
                <div class="flex justify-between items-center">
                    <span class="text-green-600 font-semibold">${o.currency}${this.formatNumber(o.total)}</span>
                    <span class="text-xs text-gray-400">${this.formatDate(o.date)}</span>
                </div>
            </div>
        `).join('');
    },

    async showOrderDetail(orderId) {
        try {
            const data = await AdminAPI.getOrderDetail(orderId);

            const linesHtml = (data.lines || []).map(l => `
                <div class="flex justify-between items-center py-2 border-b last:border-0">
                    <div class="flex items-center space-x-3">
                        <img src="${l.product.image_url || Config.DEFAULT_AVATAR}" class="w-10 h-10 rounded object-cover">
                        <div>
                            <p class="text-sm font-medium">${this.escapeHtml(l.product.name)}</p>
                            <p class="text-xs text-gray-400">x${l.quantity} @ ${data.currency}${this.formatNumber(l.price_unit)}</p>
                            ${l.seller ? `<p class="text-xs text-purple-500">Seller: ${this.escapeHtml(l.seller.name)}</p>` : ''}
                        </div>
                    </div>
                    <p class="font-semibold">${data.currency}${this.formatNumber(l.total)}</p>
                </div>
            `).join('');

            const addr = data.shipping_address;
            const addrHtml = addr ? `
                <div class="mt-4">
                    <h4 class="font-semibold text-sm mb-2">Shipping Address</h4>
                    <p class="text-sm text-gray-600">${this.escapeHtml(addr.name)} | ${this.escapeHtml(addr.phone)}</p>
                    <p class="text-sm text-gray-600">${this.escapeHtml(addr.street)} ${this.escapeHtml(addr.street2 || '')}</p>
                    <p class="text-sm text-gray-600">${this.escapeHtml(addr.city)} ${this.escapeHtml(addr.state)} ${this.escapeHtml(addr.zip)}</p>
                </div>
            ` : '';

            this.showModal('order-detail-modal', `
                <div class="flex justify-between items-center mb-4">
                    <h3 class="text-lg font-bold">${this.escapeHtml(data.name)}</h3>
                    <span class="px-3 py-1 rounded-full text-sm ${this.getOrderStateClass(data.state)}">${this.escapeHtml(data.state_display)}</span>
                </div>

                <div class="mb-4">
                    <h4 class="font-semibold text-sm mb-2">Customer</h4>
                    <p class="text-sm text-gray-600">${this.escapeHtml(data.customer.name)}</p>
                    <p class="text-sm text-gray-600">${this.escapeHtml(data.customer.email)} | ${this.escapeHtml(data.customer.phone)}</p>
                </div>

                <div class="mb-4">
                    <h4 class="font-semibold text-sm mb-2">Items (${data.item_count})</h4>
                    ${linesHtml}
                </div>

                <div class="flex justify-between font-bold text-lg mb-4">
                    <span>Total</span>
                    <span class="text-green-600">${data.currency}${this.formatNumber(data.total)}</span>
                </div>

                ${addrHtml}
            `);
        } catch (error) {
            console.error('Order detail error:', error);
            this.showToast('Failed to load order detail', 'error');
        }
    },

    // ==================== Withdrawals ====================

    async loadWithdrawals(state) {
        if (state !== undefined) {
            this.currentWithdrawalFilter = state;
            this.withdrawalsPage = 1;
        }
        const container = document.getElementById('withdrawal-list');
        container.innerHTML = '<div class="text-center py-8"><div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div></div>';

        // Update active filter button
        document.querySelectorAll('.wd-filter-btn').forEach(btn => {
            const isActive = btn.dataset.state === this.currentWithdrawalFilter;
            btn.classList.toggle('admin-blue', isActive);
            btn.classList.toggle('text-white', isActive);
            btn.classList.toggle('bg-gray-200', !isActive);
        });

        try {
            const data = await AdminAPI.getWithdrawals({
                page: this.withdrawalsPage,
                limit: 20,
                state: this.currentWithdrawalFilter === 'all' ? undefined : this.currentWithdrawalFilter,
            });

            document.getElementById('withdrawal-count').textContent = `${data.pagination.total} requests`;
            this.renderWithdrawalList(data.withdrawals || []);
            this.renderPagination(container, data.pagination, (page) => {
                this.withdrawalsPage = page;
                this.loadWithdrawals();
            });
        } catch (error) {
            console.error('Withdrawals error:', error);
            container.innerHTML = '<div class="text-center text-red-500 py-8">Failed to load withdrawals</div>';
        }
    },

    renderWithdrawalList(withdrawals) {
        const container = document.getElementById('withdrawal-list');
        if (!withdrawals.length) {
            container.innerHTML = '<div class="text-center text-gray-400 py-8">No withdrawal requests found</div>';
            return;
        }
        container.innerHTML = withdrawals.map(w => `
            <div class="bg-white rounded-xl p-4 shadow cursor-pointer" onclick="AdminApp.showWithdrawalDetail(${w.id})">
                <div class="flex justify-between items-start mb-2">
                    <div>
                        <p class="font-semibold">${this.escapeHtml(w.name)}</p>
                        <p class="text-sm text-gray-500">${this.escapeHtml(w.seller_name)}</p>
                    </div>
                    <span class="px-2 py-1 rounded-full text-xs ${this.getWithdrawalStateClass(w.state)}">${w.state}</span>
                </div>
                <div class="flex justify-between items-center">
                    <span class="text-green-600 font-bold text-lg">${w.currency}${this.formatNumber(w.amount)}</span>
                    <span class="text-xs text-gray-400">${this.formatDate(w.request_date || w.create_date)}</span>
                </div>
                ${w.state === 'pending' ? `
                    <div class="flex space-x-2 mt-3">
                        <button onclick="event.stopPropagation(); AdminApp.approveWithdrawal(${w.id})" class="flex-1 bg-green-500 text-white py-2 rounded-lg text-sm font-medium">
                            <i class="fas fa-check mr-1"></i> Approve
                        </button>
                        <button onclick="event.stopPropagation(); AdminApp.showRejectModal(${w.id})" class="flex-1 bg-red-500 text-white py-2 rounded-lg text-sm font-medium">
                            <i class="fas fa-times mr-1"></i> Reject
                        </button>
                    </div>
                ` : ''}
                ${w.state === 'approved' || w.state === 'processing' ? `
                    <div class="mt-3">
                        <button onclick="event.stopPropagation(); AdminApp.completeWithdrawal(${w.id})" class="w-full bg-blue-600 text-white py-2 rounded-lg text-sm font-medium">
                            <i class="fas fa-check-double mr-1"></i> Mark Completed
                        </button>
                    </div>
                ` : ''}
            </div>
        `).join('');
    },

    async showWithdrawalDetail(withdrawalId) {
        try {
            const data = await AdminAPI.getWalletDetail(withdrawalId).catch(() => null);

            // Get withdrawal from list or fetch wallet detail
            // We'll use the withdrawals endpoint to get individual data
            const withdrawals = await AdminAPI.getWithdrawals({ limit: 100 });
            const w = (withdrawals.withdrawals || []).find(wd => wd.id === withdrawalId);
            if (!w) {
                this.showToast('Withdrawal not found', 'error');
                return;
            }

            const actionsHtml = this.getWithdrawalActionsHtml(w);

            this.showModal('withdrawal-detail-modal', `
                <div class="flex justify-between items-center mb-4">
                    <h3 class="text-lg font-bold">${this.escapeHtml(w.name)}</h3>
                    <span class="px-3 py-1 rounded-full text-sm ${this.getWithdrawalStateClass(w.state)}">${w.state}</span>
                </div>

                <div class="bg-green-50 rounded-xl p-4 mb-4 text-center">
                    <p class="text-sm text-gray-500">Withdrawal Amount</p>
                    <p class="text-3xl font-bold text-green-600">${w.currency}${this.formatNumber(w.amount)}</p>
                </div>

                <div class="space-y-2 mb-4">
                    <div class="flex justify-between">
                        <span class="text-sm text-gray-500">Seller</span>
                        <span class="text-sm font-medium">${this.escapeHtml(w.seller_name)}</span>
                    </div>
                    ${w.payment_method ? `
                    <div class="flex justify-between">
                        <span class="text-sm text-gray-500">Payment Method</span>
                        <span class="text-sm">${this.escapeHtml(w.payment_method)}</span>
                    </div>` : ''}
                    ${w.bank_name ? `
                    <div class="flex justify-between">
                        <span class="text-sm text-gray-500">Bank</span>
                        <span class="text-sm">${this.escapeHtml(w.bank_name)}</span>
                    </div>` : ''}
                    ${w.account_name ? `
                    <div class="flex justify-between">
                        <span class="text-sm text-gray-500">Account Name</span>
                        <span class="text-sm">${this.escapeHtml(w.account_name)}</span>
                    </div>` : ''}
                    ${w.account_number ? `
                    <div class="flex justify-between">
                        <span class="text-sm text-gray-500">Account Number</span>
                        <span class="text-sm font-mono">${this.escapeHtml(w.account_number)}</span>
                    </div>` : ''}
                    <div class="flex justify-between">
                        <span class="text-sm text-gray-500">Request Date</span>
                        <span class="text-sm">${this.formatDate(w.request_date || w.create_date)}</span>
                    </div>
                    ${w.rejection_reason ? `
                    <div class="mt-3 p-3 bg-red-50 rounded-lg">
                        <p class="text-sm font-medium text-red-800">Rejection Reason</p>
                        <p class="text-sm text-red-600">${this.escapeHtml(w.rejection_reason)}</p>
                    </div>` : ''}
                </div>

                ${actionsHtml}
            `);
        } catch (error) {
            console.error('Withdrawal detail error:', error);
            this.showToast('Failed to load withdrawal details', 'error');
        }
    },

    getWithdrawalActionsHtml(w) {
        if (w.state === 'pending') {
            return `
                <div class="flex space-x-3 mt-4">
                    <button onclick="AdminApp.approveWithdrawal(${w.id}); AdminApp.closeModal('withdrawal-detail-modal');" class="flex-1 bg-green-500 text-white py-3 rounded-lg font-semibold">
                        <i class="fas fa-check mr-1"></i> Approve
                    </button>
                    <button onclick="AdminApp.closeModal('withdrawal-detail-modal'); AdminApp.showRejectModal(${w.id});" class="flex-1 bg-red-500 text-white py-3 rounded-lg font-semibold">
                        <i class="fas fa-times mr-1"></i> Reject
                    </button>
                </div>
            `;
        }
        if (w.state === 'approved' || w.state === 'processing') {
            return `
                <div class="mt-4">
                    <button onclick="AdminApp.completeWithdrawal(${w.id}); AdminApp.closeModal('withdrawal-detail-modal');" class="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold">
                        <i class="fas fa-check-double mr-1"></i> Mark Completed
                    </button>
                </div>
            `;
        }
        return '';
    },

    async approveWithdrawal(id) {
        try {
            await AdminAPI.approveWithdrawal(id);
            this.showToast('Withdrawal approved', 'success');
            this.loadWithdrawals();
        } catch (error) {
            console.error('Approve withdrawal error:', error);
            this.showToast(error.message || 'Failed to approve withdrawal', 'error');
        }
    },

    showRejectModal(withdrawalId) {
        this.showModal('reject-modal', `
            <h3 class="text-lg font-bold mb-4">Reject Withdrawal</h3>
            <div class="mb-4">
                <label class="block text-sm font-medium mb-2">Reason for rejection</label>
                <textarea id="rejectReason" rows="3" class="w-full px-3 py-2 border rounded-lg resize-none"
                          placeholder="Enter reason..."></textarea>
            </div>
            <div class="flex space-x-3">
                <button onclick="AdminApp.closeModal('reject-modal')" class="flex-1 bg-gray-200 py-3 rounded-lg font-medium">Cancel</button>
                <button onclick="AdminApp.rejectWithdrawal(${withdrawalId})" class="flex-1 bg-red-500 text-white py-3 rounded-lg font-semibold">Reject</button>
            </div>
        `);
    },

    async rejectWithdrawal(id) {
        const reason = document.getElementById('rejectReason')?.value?.trim() || '';
        try {
            await AdminAPI.rejectWithdrawal(id, reason);
            this.closeModal('reject-modal');
            this.showToast('Withdrawal rejected', 'success');
            this.loadWithdrawals();
        } catch (error) {
            console.error('Reject withdrawal error:', error);
            this.showToast(error.message || 'Failed to reject withdrawal', 'error');
        }
    },

    async completeWithdrawal(id) {
        try {
            await AdminAPI.completeWithdrawal(id);
            this.showToast('Withdrawal completed', 'success');
            this.loadWithdrawals();
        } catch (error) {
            console.error('Complete withdrawal error:', error);
            this.showToast(error.message || 'Failed to complete withdrawal', 'error');
        }
    },

    getWithdrawalStateClass(state) {
        const classes = {
            'draft': 'bg-gray-100 text-gray-800',
            'pending': 'bg-yellow-100 text-yellow-800',
            'approved': 'bg-blue-100 text-blue-800',
            'processing': 'bg-purple-100 text-purple-800',
            'completed': 'bg-green-100 text-green-800',
            'rejected': 'bg-red-100 text-red-800',
            'cancelled': 'bg-gray-100 text-gray-600',
        };
        return classes[state] || 'bg-gray-100 text-gray-800';
    },

    // ==================== Admin Team ====================

    async checkManagerStatus() {
        try {
            const data = await AdminAPI.getMyManagerStatus();
            this.isManager = data.is_manager;
            const navTeam = document.getElementById('nav-team');
            if (navTeam) {
                navTeam.classList.toggle('hidden', !this.isManager);
            }
        } catch (error) {
            console.error('Check manager status error:', error);
            this.isManager = false;
        }
    },

    async loadTeam(state) {
        if (state !== undefined) {
            this.currentTeamFilter = state;
            this.teamPage = 1;
        }
        const container = document.getElementById('team-list');
        if (!container) return;
        container.innerHTML = '<div class="text-center py-8"><div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div></div>';

        // Update active filter button
        document.querySelectorAll('.team-filter-btn').forEach(btn => {
            const isActive = btn.dataset.state === this.currentTeamFilter;
            btn.classList.toggle('admin-blue', isActive);
            btn.classList.toggle('text-white', isActive);
            btn.classList.toggle('bg-gray-200', !isActive);
        });

        try {
            const data = await AdminAPI.getTeam({
                state: this.currentTeamFilter === 'all' ? undefined : this.currentTeamFilter,
                page: this.teamPage,
                limit: 20,
            });

            const countEl = document.getElementById('team-count');
            if (countEl) {
                countEl.textContent = `${data.counts.active} active, ${data.counts.revoked} revoked`;
            }

            this.renderTeamList(data.members || []);
            this.renderPagination(container, data.pagination, (page) => {
                this.teamPage = page;
                this.loadTeam();
            });
        } catch (error) {
            console.error('Load team error:', error);
            container.innerHTML = '<div class="text-center text-red-500 py-8">Failed to load team</div>';
        }
    },

    renderTeamList(members) {
        const container = document.getElementById('team-list');
        if (!members.length) {
            container.innerHTML = '<div class="text-center text-gray-400 py-8">No team members found</div>';
            return;
        }
        container.innerHTML = members.map(m => `
            <div class="bg-white rounded-xl p-4 shadow">
                <div class="flex items-center justify-between">
                    <div class="flex items-center space-x-3">
                        <div class="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center overflow-hidden">
                            ${m.picture_url
                                ? `<img src="${m.picture_url}" class="w-full h-full object-cover">`
                                : '<i class="fas fa-user-shield text-blue-500"></i>'}
                        </div>
                        <div>
                            <p class="font-medium">${this.escapeHtml(m.name)}</p>
                            <p class="text-xs text-gray-500">${this.escapeHtml(m.line_display_name)} | ${m.role}</p>
                        </div>
                    </div>
                    <span class="px-2 py-1 rounded-full text-xs ${m.state === 'active' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}">${m.state}</span>
                </div>
                <div class="mt-2 text-xs text-gray-400">
                    เชิญโดย ${this.escapeHtml(m.invited_by_name)} | ${this.formatDate(m.invite_date)}
                    ${m.invite_notes ? ` | ${this.escapeHtml(m.invite_notes)}` : ''}
                </div>
                ${m.state === 'revoked' ? `
                    <div class="mt-2 p-2 bg-red-50 rounded text-xs text-red-600">
                        เพิกถอนโดย ${this.escapeHtml(m.revoked_by_name)} | ${this.formatDate(m.revoke_date)}
                        ${m.revoke_reason ? `<br>เหตุผล: ${this.escapeHtml(m.revoke_reason)}` : ''}
                    </div>
                ` : `
                    <div class="mt-3">
                        <button onclick="AdminApp.showRevokeModal(${m.id}, '${this.escapeHtml(m.name).replace(/'/g, "\\'")}')" class="w-full bg-red-50 text-red-600 py-2 rounded-lg text-sm font-medium border border-red-200">
                            <i class="fas fa-user-minus mr-1"></i> เพิกถอนสิทธิ์
                        </button>
                    </div>
                `}
            </div>
        `).join('');
    },

    showInviteModal() {
        this.showModal('invite-modal', `
            <h3 class="text-lg font-bold mb-4"><i class="fas fa-user-plus mr-2 text-blue-600"></i>เชิญแอดมินใหม่</h3>
            <div class="mb-4">
                <label class="block text-sm font-medium mb-2">ค้นหา LINE Member</label>
                <div class="flex space-x-2">
                    <input type="text" id="candidateSearch" placeholder="พิมพ์ชื่อ (อย่างน้อย 2 ตัวอักษร)..."
                           class="flex-1 px-3 py-2 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
                    <button onclick="AdminApp.searchCandidates()" class="admin-blue text-white px-4 rounded-lg">
                        <i class="fas fa-search"></i>
                    </button>
                </div>
            </div>
            <div id="candidate-list" class="space-y-2 max-h-64 overflow-y-auto">
                <p class="text-center text-gray-400 text-sm py-4">ค้นหาชื่อเพื่อแสดงรายการ</p>
            </div>
        `);

        // Add enter key handler
        setTimeout(() => {
            const input = document.getElementById('candidateSearch');
            if (input) {
                input.focus();
                input.addEventListener('keyup', (e) => {
                    if (e.key === 'Enter') this.searchCandidates();
                });
            }
        }, 100);
    },

    async searchCandidates() {
        const search = document.getElementById('candidateSearch')?.value?.trim();
        const container = document.getElementById('candidate-list');
        if (!container) return;

        if (!search || search.length < 2) {
            container.innerHTML = '<p class="text-center text-gray-400 text-sm py-4">พิมพ์อย่างน้อย 2 ตัวอักษร</p>';
            return;
        }

        container.innerHTML = '<div class="text-center py-4"><div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500 mx-auto"></div></div>';

        try {
            const data = await AdminAPI.getTeamCandidates(search);
            const candidates = data.candidates || [];

            if (!candidates.length) {
                container.innerHTML = '<p class="text-center text-gray-400 text-sm py-4">ไม่พบผู้ใช้ที่ตรงกัน</p>';
                return;
            }

            container.innerHTML = candidates.map(c => `
                <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div class="flex items-center space-x-3">
                        <div class="w-9 h-9 rounded-full bg-gray-200 flex items-center justify-center overflow-hidden">
                            ${c.picture_url
                                ? `<img src="${c.picture_url}" class="w-full h-full object-cover">`
                                : '<i class="fas fa-user text-gray-400 text-sm"></i>'}
                        </div>
                        <div>
                            <p class="font-medium text-sm">${this.escapeHtml(c.name)}</p>
                            <p class="text-xs text-gray-500">${this.escapeHtml(c.phone)}${c.is_seller ? ' | Seller' : ''}</p>
                            ${!c.has_profile ? '<p class="text-xs text-red-500">ยังไม่มีชื่อ/เบอร์</p>' : ''}
                        </div>
                    </div>
                    <button onclick="AdminApp.confirmInvite(${c.partner_id}, '${this.escapeHtml(c.name).replace(/'/g, "\\'")}')"
                            class="admin-blue text-white px-3 py-1.5 rounded-lg text-xs font-medium ${!c.has_profile ? 'opacity-50 cursor-not-allowed' : ''}"
                            ${!c.has_profile ? 'disabled' : ''}>
                        <i class="fas fa-plus mr-1"></i>เชิญ
                    </button>
                </div>
            `).join('');
        } catch (error) {
            console.error('Search candidates error:', error);
            container.innerHTML = '<p class="text-center text-red-500 text-sm py-4">เกิดข้อผิดพลาด</p>';
        }
    },

    confirmInvite(partnerId, name) {
        this.closeModal('invite-modal');
        this.showModal('confirm-invite-modal', `
            <h3 class="text-lg font-bold mb-4">ยืนยันเชิญแอดมิน</h3>
            <p class="text-sm text-gray-600 mb-4">เชิญ <strong>${this.escapeHtml(name)}</strong> เป็น Officer?</p>
            <div class="mb-4">
                <label class="block text-sm font-medium mb-2">หมายเหตุ (ไม่บังคับ)</label>
                <input type="text" id="inviteNotes" placeholder="เหตุผลในการเชิญ..."
                       class="w-full px-3 py-2 border rounded-lg text-sm">
            </div>
            <div class="flex space-x-3">
                <button onclick="AdminApp.closeModal('confirm-invite-modal'); AdminApp.showInviteModal();" class="flex-1 bg-gray-200 py-3 rounded-lg font-medium">ยกเลิก</button>
                <button onclick="AdminApp.inviteAdmin(${partnerId})" class="flex-1 admin-blue text-white py-3 rounded-lg font-semibold">
                    <i class="fas fa-check mr-1"></i> ยืนยัน
                </button>
            </div>
        `);
    },

    async inviteAdmin(partnerId) {
        const notes = document.getElementById('inviteNotes')?.value?.trim() || '';
        try {
            const data = await AdminAPI.inviteAdmin(partnerId, notes);
            this.closeModal('confirm-invite-modal');
            this.showToast(data.message || 'เชิญสำเร็จ', 'success');
            this.loadTeam();
        } catch (error) {
            console.error('Invite admin error:', error);
            this.showToast(error.message || 'เกิดข้อผิดพลาดในการเชิญ', 'error');
        }
    },

    showRevokeModal(memberId, name) {
        this.showModal('revoke-modal', `
            <h3 class="text-lg font-bold mb-4 text-red-600"><i class="fas fa-user-minus mr-2"></i>เพิกถอนสิทธิ์แอดมิน</h3>
            <p class="text-sm text-gray-600 mb-4">เพิกถอนสิทธิ์ Officer ของ <strong>${this.escapeHtml(name)}</strong>?</p>
            <div class="mb-4">
                <label class="block text-sm font-medium mb-2">เหตุผล (ไม่บังคับ)</label>
                <textarea id="revokeReason" rows="3" class="w-full px-3 py-2 border rounded-lg resize-none text-sm"
                          placeholder="ระบุเหตุผลในการเพิกถอน..."></textarea>
            </div>
            <div class="flex space-x-3">
                <button onclick="AdminApp.closeModal('revoke-modal')" class="flex-1 bg-gray-200 py-3 rounded-lg font-medium">ยกเลิก</button>
                <button onclick="AdminApp.revokeAdmin(${memberId})" class="flex-1 bg-red-500 text-white py-3 rounded-lg font-semibold">
                    <i class="fas fa-ban mr-1"></i> เพิกถอน
                </button>
            </div>
        `);
    },

    async revokeAdmin(memberId) {
        const reason = document.getElementById('revokeReason')?.value?.trim() || '';
        try {
            const data = await AdminAPI.revokeAdmin(memberId, reason);
            this.closeModal('revoke-modal');
            this.showToast(data.message || 'เพิกถอนสำเร็จ', 'success');
            this.loadTeam();
        } catch (error) {
            console.error('Revoke admin error:', error);
            this.showToast(error.message || 'เกิดข้อผิดพลาดในการเพิกถอน', 'error');
        }
    },

    // ==================== Notifications ====================

    async sendNotification() {
        const target = document.getElementById('notifyTarget').value;
        const message = document.getElementById('notifyMessage').value.trim();

        if (!message) {
            this.showToast('Please enter a message', 'error');
            return;
        }

        const sendBtn = document.querySelector('#page-notifications button[onclick*="sendNotification"]');
        if (sendBtn) {
            sendBtn.disabled = true;
            sendBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Sending...';
        }

        try {
            const data = await AdminAPI.sendNotification({
                target,
                message_type: this.currentMessageType,
                message,
            });

            this.showToast(`Sent to ${data.sent_count} members`, 'success');
            document.getElementById('notifyMessage').value = '';
            this.loadNotificationHistory();
        } catch (error) {
            console.error('Send notification error:', error);
            this.showToast(error.message || 'Failed to send notification', 'error');
        } finally {
            if (sendBtn) {
                sendBtn.disabled = false;
                sendBtn.innerHTML = '<i class="fas fa-paper-plane mr-2"></i> Send Notification';
            }
        }
    },

    async loadNotificationHistory() {
        const container = document.getElementById('notification-history');
        if (!container) return;

        try {
            const data = await AdminAPI.getNotificationHistory({
                page: this.notificationsPage,
                limit: Config.NOTIFICATIONS_PER_PAGE,
            });

            this.renderNotificationHistory(data.notifications || []);
        } catch (error) {
            console.error('Notification history error:', error);
            container.innerHTML = '<div class="text-center text-gray-400 py-4">Failed to load history</div>';
        }
    },

    renderNotificationHistory(notifications) {
        const container = document.getElementById('notification-history');
        if (!notifications.length) {
            container.innerHTML = '<div class="text-center text-gray-400 py-4">No notifications sent yet</div>';
            return;
        }
        container.innerHTML = notifications.map(n => `
            <div class="bg-white rounded-xl p-4 shadow">
                <div class="flex justify-between items-start mb-1">
                    <p class="text-sm font-medium">${this.escapeHtml(n.target_name)}</p>
                    <span class="px-2 py-0.5 rounded-full text-xs ${n.state === 'sent' ? 'bg-green-100 text-green-800' : n.state === 'failed' ? 'bg-red-100 text-red-800' : 'bg-yellow-100 text-yellow-800'}">${n.state}</span>
                </div>
                <p class="text-sm text-gray-600 truncate">${this.escapeHtml(n.message)}</p>
                <div class="flex justify-between items-center mt-2">
                    <span class="text-xs text-gray-400">${n.notify_type} / ${n.message_type}</span>
                    <span class="text-xs text-gray-400">${this.formatDate(n.sent_date || n.create_date)}</span>
                </div>
            </div>
        `).join('');
    },

    // ==================== Settings ====================

    async loadSettings() {
        try {
            const data = await AdminAPI.getSettings();

            // Channel info
            document.getElementById('channel-id').textContent = data.channel.code || '-';

            // Notification toggles
            const orderToggle = document.getElementById('toggle-notify-order');
            const shippingToggle = document.getElementById('toggle-notify-shipping');
            if (orderToggle) orderToggle.checked = data.settings.auto_notify_new_order;
            if (shippingToggle) shippingToggle.checked = data.settings.auto_notify_shipping;

            // LIFF apps
            const appsContainer = document.getElementById('liff-apps-list');
            if (data.liff_apps && data.liff_apps.length) {
                appsContainer.innerHTML = data.liff_apps.map(app => `
                    <div class="flex justify-between items-center py-1">
                        <span class="text-gray-600">${this.escapeHtml(app.name)}</span>
                        <span class="text-xs text-gray-400">${this.escapeHtml(app.liff_id || '')}</span>
                    </div>
                `).join('');
            } else {
                appsContainer.innerHTML = '<p class="text-gray-400 text-sm">No LIFF apps configured</p>';
            }
        } catch (error) {
            console.error('Settings error:', error);
            this.showToast('Failed to load settings', 'error');
        }
    },

    async updateSetting(key, value) {
        try {
            await AdminAPI.updateSettings({ [key]: value });
            this.showToast('Setting updated', 'success');
        } catch (error) {
            console.error('Update setting error:', error);
            this.showToast('Failed to update setting', 'error');
        }
    },

    // ==================== UI Helpers ====================

    showModal(modalId, contentHtml) {
        let modal = document.getElementById(modalId);
        if (!modal) {
            // Create modal dynamically
            modal = document.createElement('div');
            modal.id = modalId;
            modal.className = 'fixed inset-0 bg-black/50 flex items-end justify-center z-50';
            modal.innerHTML = `
                <div class="bg-white rounded-t-2xl w-full max-h-[85vh] overflow-y-auto p-6">
                    <div class="flex justify-between items-center mb-4">
                        <div></div>
                        <button onclick="AdminApp.closeModal('${modalId}')" class="text-gray-400 text-xl"><i class="fas fa-times"></i></button>
                    </div>
                    <div id="${modalId}-content"></div>
                </div>
            `;
            document.body.appendChild(modal);
        }

        const contentContainer = document.getElementById(`${modalId}-content`);
        if (contentContainer) {
            contentContainer.innerHTML = contentHtml;
        }
        modal.classList.remove('hidden');
    },

    closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) modal.classList.add('hidden');
    },

    renderPagination(container, pagination, onPageClick) {
        if (!pagination || pagination.pages <= 1) return;

        const paginationHtml = document.createElement('div');
        paginationHtml.className = 'flex justify-center items-center space-x-2 mt-4';

        if (pagination.page > 1) {
            const prev = document.createElement('button');
            prev.className = 'px-3 py-1 bg-gray-200 rounded text-sm';
            prev.textContent = 'Prev';
            prev.addEventListener('click', () => onPageClick(pagination.page - 1));
            paginationHtml.appendChild(prev);
        }

        const info = document.createElement('span');
        info.className = 'text-sm text-gray-500';
        info.textContent = `${pagination.page} / ${pagination.pages}`;
        paginationHtml.appendChild(info);

        if (pagination.page < pagination.pages) {
            const next = document.createElement('button');
            next.className = 'px-3 py-1 bg-gray-200 rounded text-sm';
            next.textContent = 'Next';
            next.addEventListener('click', () => onPageClick(pagination.page + 1));
            paginationHtml.appendChild(next);
        }

        container.appendChild(paginationHtml);
    },

    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        const colors = {
            success: 'bg-green-500',
            error: 'bg-red-500',
            info: 'bg-blue-500',
        };
        toast.className = `fixed top-4 left-1/2 transform -translate-x-1/2 ${colors[type] || colors.info} text-white px-6 py-3 rounded-lg shadow-lg z-[60] transition-opacity duration-300`;
        toast.textContent = message;
        document.body.appendChild(toast);
        setTimeout(() => {
            toast.classList.add('opacity-0');
            setTimeout(() => toast.remove(), 300);
        }, 2500);
    },

    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },

    formatNumber(num) {
        if (num === null || num === undefined) return '0';
        return Number(num).toLocaleString('th-TH', { maximumFractionDigits: 2 });
    },

    formatDate(dateStr) {
        if (!dateStr) return '';
        try {
            const d = new Date(dateStr);
            return d.toLocaleDateString('th-TH', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' });
        } catch (e) {
            return dateStr;
        }
    },

    getOrderStateClass(state) {
        const classes = {
            'draft': 'bg-gray-100 text-gray-800',
            'sent': 'bg-yellow-100 text-yellow-800',
            'sale': 'bg-blue-100 text-blue-800',
            'done': 'bg-green-100 text-green-800',
            'cancel': 'bg-red-100 text-red-800',
        };
        return classes[state] || 'bg-gray-100 text-gray-800';
    },

    getSellerStateClass(state) {
        const classes = {
            'new': 'bg-gray-100 text-gray-800',
            'pending': 'bg-yellow-100 text-yellow-800',
            'approved': 'bg-green-100 text-green-800',
            'denied': 'bg-red-100 text-red-800',
        };
        return classes[state] || 'bg-gray-100 text-gray-800';
    },

    getProductStatusClass(status) {
        const classes = {
            'draft': 'bg-gray-100 text-gray-800',
            'pending': 'bg-yellow-100 text-yellow-800',
            'approved': 'bg-green-100 text-green-800',
            'rejected': 'bg-red-100 text-red-800',
        };
        return classes[status] || 'bg-gray-100 text-gray-800';
    },
};

// Global function bindings for onclick handlers in HTML
function showPage(page) { AdminApp.showPage(page); }
function refreshData() { AdminApp.loadDashboard(); }
function showSettings() { AdminApp.showPage('settings'); }
function searchMembers() {
    AdminApp.currentMemberSearch = document.getElementById('memberSearch').value;
    AdminApp.membersPage = 1;
    AdminApp.loadMembersPage();
}
function sendNotification() { AdminApp.sendNotification(); }
function openOdooBackend() { window.open(Config.API_BASE_URL + '/web', '_blank'); }

document.addEventListener('DOMContentLoaded', () => AdminApp.init());
