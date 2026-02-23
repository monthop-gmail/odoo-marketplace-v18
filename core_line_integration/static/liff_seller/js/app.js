/**
 * Seller LIFF App - Main Application Logic
 */
const SellerApp = {
    user: null,
    currentPage: 'dashboard',
    ordersPage: 1,
    productsPage: 1,
    currentOrderFilter: 'all',
    currentReportPeriod: 'today',
    walletTxPage: 1,
    currentTxFilter: 'all',
    categories: [],
    isShopStaff: false,
    isShopOwner: true,
    staffContext: null,
    // Gallery state for product form
    existingImages: [],   // {id, name, url, thumbnail, sequence} from API
    pendingImages: [],    // {file, preview} new files not yet uploaded
    removedImageIds: [],  // IDs of existing images to delete on save
    // Quick Post state
    quickPostPhotoFile: null,
    quickPostExtraFiles: [],   // extra image Files for quick post
    lastCreatedProductId: null,
    quickPostExpanded: false,
    previousPage: 'dashboard',

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
            await this.loadStaffContext();
            await this.loadDashboard();

            // Deep-link routing (read from sessionStorage to survive LIFF reload)
            const _deepLink = sessionStorage.getItem('liff_deep_link');
            if (_deepLink) {
                sessionStorage.removeItem('liff_deep_link');
                if (_deepLink === 'quickpost') {
                    this.startQuickPost();
                } else if (document.getElementById(`page-${_deepLink}`)) {
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
        SellerAPI.setAuth(accessToken, profile.userId);
        this.updateUserUI();
    },

    async initMockMode() {
        this.user = Config.MOCK_USER;
        this.user.pictureUrl = this.user.pictureUrl || Config.DEFAULT_AVATAR;
        SellerAPI.setAuth(null, this.user.userId);
        this.updateUserUI();
    },

    updateUserUI() {
        const avatar = this.user.pictureUrl || Config.DEFAULT_AVATAR;
        document.getElementById('sellerAvatar').src = avatar;
        document.getElementById('sellerName').textContent = this.user.displayName;
        document.getElementById('profile-avatar').src = avatar;
    },

    async loadStaffContext() {
        try {
            const data = await SellerAPI.getProfile();
            this.isShopOwner = data.is_shop_owner !== false;
            this.isShopStaff = data.is_shop_staff === true;
            this.staffContext = data.staff_context || null;
            this.applyStaffRestrictions();
        } catch (error) {
            console.error('Staff context error:', error);
        }
    },

    applyStaffRestrictions() {
        if (!this.isShopStaff) return;

        // Show staff banner
        const banner = document.getElementById('staff-banner');
        if (banner) {
            const shopName = this.staffContext?.shop_name || '';
            const role = this.staffContext?.role === 'manager' ? 'Shop Manager' : 'Staff';
            banner.innerHTML = `<div class="bg-blue-50 border-l-4 border-blue-400 p-3 mb-2"><p class="text-sm text-blue-700"><i class="fas fa-user-friends mr-1"></i> ${role} &mdash; Managing: <strong>${this.escapeHtml(shopName)}</strong></p></div>`;
            banner.classList.remove('hidden');
        }

        // Hide wallet nav button (staff cannot access wallet/withdrawal)
        const walletNavBtn = document.querySelector('.nav-btn[data-page="wallet"]');
        if (walletNavBtn) walletNavBtn.classList.add('hidden');

        // Hide owner-only buttons in profile page
        const shopSettingsBtn = document.getElementById('btn-manage-shop');
        if (shopSettingsBtn) shopSettingsBtn.classList.add('hidden');
        const editProfileBtn = document.getElementById('btn-edit-profile');
        if (editProfileBtn) editProfileBtn.classList.add('hidden');
    },

    setupEventListeners() {
        // Bottom navigation
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.addEventListener('click', () => this.showPage(btn.dataset.page));
        });

        // Order filters
        document.querySelectorAll('.order-filter').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.order-filter').forEach(b => {
                    b.classList.remove('active', 'line-green', 'text-white');
                    b.classList.add('bg-gray-200');
                });
                btn.classList.add('active', 'line-green', 'text-white');
                btn.classList.remove('bg-gray-200');
                this.loadOrders(btn.dataset.status);
            });
        });

        // Report period buttons
        document.querySelectorAll('.report-period').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.report-period').forEach(b => {
                    b.classList.remove('active', 'line-green', 'text-white');
                    b.classList.add('bg-gray-200');
                });
                btn.classList.add('active', 'line-green', 'text-white');
                btn.classList.remove('bg-gray-200');
                this.loadReports(btn.dataset.period);
            });
        });

        // Product search
        let searchTimer;
        const searchInput = document.getElementById('productSearch');
        if (searchInput) {
            searchInput.addEventListener('input', () => {
                clearTimeout(searchTimer);
                searchTimer = setTimeout(() => this.loadProducts(), 300);
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
            btn.classList.toggle('line-green-text', isActive);
        });

        this.currentPage = pageName;

        switch (pageName) {
            case 'dashboard': this.loadDashboard(); break;
            case 'orders': this.loadOrders(this.currentOrderFilter); break;
            case 'products': this.loadProducts(); break;
            case 'wallet': this.loadWallet(); break;
            case 'reports': this.loadReports(this.currentReportPeriod); break;
            case 'profile': this.loadProfile(); break;
            case 'quickpost': break; // handled by startQuickPost()
        }
    },

    // ==================== Dashboard ====================

    async loadDashboard() {
        try {
            const data = await SellerAPI.getDashboard();
            const stats = data.stats;

            document.getElementById('stat-orders-today').textContent = this.formatNumber(stats.today_orders);
            document.getElementById('stat-pending').textContent = this.formatNumber(stats.pending_ship);
            document.getElementById('stat-revenue').textContent = `${stats.currency}${this.formatNumber(stats.today_revenue)}`;
            document.getElementById('stat-products').textContent = this.formatNumber(stats.active_products);

            this.renderRecentOrders(data.recent_orders || []);
        } catch (error) {
            console.error('Dashboard error:', error);
            this.showToast('Failed to load dashboard', 'error');
        }
    },

    renderRecentOrders(orders) {
        const container = document.getElementById('recent-orders');
        if (!orders.length) {
            container.innerHTML = '<div class="text-center text-gray-400 py-8">No recent orders</div>';
            return;
        }
        container.innerHTML = orders.map(order => `
            <div class="bg-white rounded-xl p-4 shadow cursor-pointer" onclick="SellerApp.showOrderDetail(${order.id})">
                <div class="flex justify-between items-start mb-2">
                    <div>
                        <p class="font-semibold">${this.escapeHtml(order.order_name)}</p>
                        <p class="text-sm text-gray-500">${this.escapeHtml(order.customer_name)}</p>
                    </div>
                    <span class="px-2 py-1 rounded-full text-xs ${this.getStatusClass(order.marketplace_state)}">${this.escapeHtml(order.marketplace_state_display)}</span>
                </div>
                <div class="flex justify-between items-center">
                    <span class="text-green-600 font-semibold">฿${this.formatNumber(order.subtotal)}</span>
                    <span class="text-xs text-gray-400">${this.formatDate(order.order_date)}</span>
                </div>
            </div>
        `).join('');
    },

    // ==================== Orders ====================

    async loadOrders(status = 'all') {
        this.currentOrderFilter = status;
        const container = document.getElementById('orders-list');
        container.innerHTML = '<div class="text-center py-8"><div class="animate-spin rounded-full h-8 w-8 border-b-2 border-green-500 mx-auto"></div></div>';

        try {
            const data = await SellerAPI.getOrders({
                page: this.ordersPage,
                limit: Config.ORDERS_PER_PAGE,
                status,
            });
            this.renderOrdersList(data.orders || []);
        } catch (error) {
            console.error('Orders error:', error);
            container.innerHTML = '<div class="text-center text-red-500 py-8">Failed to load orders</div>';
        }
    },

    renderOrdersList(orders) {
        const container = document.getElementById('orders-list');
        if (!orders.length) {
            container.innerHTML = '<div class="text-center text-gray-400 py-8">No orders found</div>';
            return;
        }
        container.innerHTML = orders.map(order => `
            <div class="bg-white rounded-xl p-4 shadow cursor-pointer" onclick="SellerApp.showOrderDetail(${order.id})">
                <div class="flex justify-between items-start mb-2">
                    <div>
                        <p class="font-semibold">${this.escapeHtml(order.order_name)}</p>
                        <p class="text-sm text-gray-500">${this.escapeHtml(order.customer_name)}</p>
                    </div>
                    <span class="px-2 py-1 rounded-full text-xs ${this.getStatusClass(order.marketplace_state)}">${this.escapeHtml(order.marketplace_state_display)}</span>
                </div>
                <div class="flex justify-between items-center">
                    <div>
                        <p class="text-sm text-gray-600">${this.escapeHtml(order.product.name)}</p>
                        <p class="text-xs text-gray-400">x${order.quantity}</p>
                    </div>
                    <span class="text-green-600 font-semibold">฿${this.formatNumber(order.subtotal)}</span>
                </div>
            </div>
        `).join('');
    },

    async showOrderDetail(lineId) {
        try {
            const data = await SellerAPI.getOrderDetail(lineId);
            const state = data.marketplace_state;

            // Build action buttons based on state
            let actions = '';
            if (state === 'pending') {
                actions = `
                    <button onclick="SellerApp.handleOrderAction(${lineId}, 'approve')" class="flex-1 bg-green-500 text-white py-3 rounded-lg font-semibold">Approve</button>
                    <button onclick="SellerApp.handleOrderAction(${lineId}, 'cancel')" class="flex-1 bg-red-500 text-white py-3 rounded-lg font-semibold">Cancel</button>
                `;
            } else if (state === 'approved') {
                actions = `
                    <button onclick="SellerApp.handleOrderAction(${lineId}, 'ship')" class="flex-1 line-green text-white py-3 rounded-lg font-semibold">Mark Shipped</button>
                    <button onclick="SellerApp.handleOrderAction(${lineId}, 'cancel')" class="flex-1 bg-red-500 text-white py-3 rounded-lg font-semibold">Cancel</button>
                `;
            } else if (state === 'shipped') {
                actions = `
                    <button onclick="SellerApp.handleOrderAction(${lineId}, 'done')" class="flex-1 bg-blue-500 text-white py-3 rounded-lg font-semibold">Mark Done</button>
                `;
            }

            // Render all seller lines in the order
            const linesHtml = (data.seller_lines || []).map(l => `
                <div class="flex justify-between items-center py-2 border-b last:border-0">
                    <div class="flex items-center space-x-3">
                        <img src="${l.product.image_url || Config.DEFAULT_PRODUCT_IMAGE}" class="w-10 h-10 rounded object-cover">
                        <div>
                            <p class="text-sm font-medium">${this.escapeHtml(l.product.name)}</p>
                            <p class="text-xs text-gray-400">x${l.quantity} @ ฿${this.formatNumber(l.price_unit)}</p>
                        </div>
                    </div>
                    <p class="font-semibold">฿${this.formatNumber(l.subtotal)}</p>
                </div>
            `).join('');

            // Shipping address
            const addr = data.shipping_address;
            const addrHtml = addr ? `
                <div class="mt-4">
                    <h4 class="font-semibold text-sm mb-2">Shipping Address</h4>
                    <p class="text-sm text-gray-600">${this.escapeHtml(addr.name)}</p>
                    <p class="text-sm text-gray-600">${this.escapeHtml(addr.phone)}</p>
                    <p class="text-sm text-gray-600">${this.escapeHtml(addr.street)} ${this.escapeHtml(addr.street2 || '')}</p>
                    <p class="text-sm text-gray-600">${this.escapeHtml(addr.city)} ${this.escapeHtml(addr.state)} ${this.escapeHtml(addr.zip)}</p>
                </div>
            ` : '';

            const modal = document.getElementById('order-detail-modal');
            document.getElementById('order-detail-content').innerHTML = `
                <div class="flex justify-between items-center mb-4">
                    <h3 class="text-lg font-bold">${this.escapeHtml(data.order_name)}</h3>
                    <span class="px-3 py-1 rounded-full text-sm ${this.getStatusClass(state)}">${this.escapeHtml(data.marketplace_state_display)}</span>
                </div>

                <div class="mb-4">
                    <h4 class="font-semibold text-sm mb-2">Customer</h4>
                    <p class="text-sm text-gray-600">${this.escapeHtml(data.customer.name)}</p>
                    <p class="text-sm text-gray-600">${this.escapeHtml(data.customer.phone)} | ${this.escapeHtml(data.customer.email)}</p>
                </div>

                <div class="mb-4">
                    <h4 class="font-semibold text-sm mb-2">Items</h4>
                    ${linesHtml}
                </div>

                <div class="flex justify-between font-bold text-lg mb-4">
                    <span>Total</span>
                    <span class="text-green-600">฿${this.formatNumber(data.order_total)}</span>
                </div>

                ${addrHtml}

                ${actions ? `<div class="flex space-x-3 mt-6">${actions}</div>` : ''}
            `;
            modal.classList.remove('hidden');
        } catch (error) {
            console.error('Order detail error:', error);
            this.showToast('Failed to load order detail', 'error');
        }
    },

    async handleOrderAction(lineId, action) {
        try {
            const actionMap = {
                approve: () => SellerAPI.approveOrder(lineId),
                ship: () => SellerAPI.shipOrder(lineId),
                done: () => SellerAPI.markOrderDone(lineId),
                cancel: () => SellerAPI.cancelOrder(lineId),
            };

            if (!actionMap[action]) return;

            await actionMap[action]();
            this.showToast(`Order ${action}d successfully`, 'success');
            this.closeModal('order-detail-modal');
            this.loadOrders(this.currentOrderFilter);
            // Refresh dashboard stats too
            if (this.currentPage === 'orders') this.loadDashboard();
        } catch (error) {
            console.error(`Order ${action} error:`, error);
            this.showToast(error.message || `Failed to ${action} order`, 'error');
        }
    },

    // ==================== Products ====================

    async loadProducts() {
        const container = document.getElementById('products-list');
        container.innerHTML = '<div class="text-center py-8"><div class="animate-spin rounded-full h-8 w-8 border-b-2 border-green-500 mx-auto"></div></div>';

        try {
            const search = document.getElementById('productSearch')?.value || '';
            const data = await SellerAPI.getProducts({
                page: this.productsPage,
                limit: Config.PRODUCTS_PER_PAGE,
                search,
            });
            this.renderProductsList(data.items || []);
        } catch (error) {
            console.error('Products error:', error);
            container.innerHTML = '<div class="text-center text-red-500 py-8">Failed to load products</div>';
        }
    },

    renderProductsList(products) {
        const container = document.getElementById('products-list');
        if (!products.length) {
            container.innerHTML = '<div class="text-center text-gray-400 py-8">No products found</div>';
            return;
        }
        container.innerHTML = products.map(p => `
            <div class="bg-white rounded-xl p-4 shadow cursor-pointer" onclick="SellerApp.showEditProduct(${p.id})">
                <div class="flex items-center space-x-3">
                    <img src="${p.image_url || Config.DEFAULT_PRODUCT_IMAGE}" class="w-16 h-16 rounded-lg object-cover">
                    <div class="flex-1">
                        <p class="font-semibold">${this.escapeHtml(p.name)}</p>
                        <p class="text-green-600 font-bold">฿${this.formatNumber(p.price)}</p>
                        <div class="flex items-center space-x-2 mt-1">
                            <span class="px-2 py-0.5 rounded-full text-xs ${this.getProductStatusClass(p.status)}">${this.escapeHtml(p.status_display)}</span>
                            <span class="text-xs text-gray-400">Stock: ${p.qty_available}</span>
                        </div>
                    </div>
                    <i class="fas fa-chevron-right text-gray-300"></i>
                </div>
            </div>
        `).join('');
    },

    async showAddProduct() {
        await this.loadCategoriesIfNeeded();
        const modal = document.getElementById('product-form-modal');
        document.getElementById('product-form-title').textContent = 'Add New Product';
        document.getElementById('product-form').reset();
        document.getElementById('product-form').dataset.productId = '';
        document.getElementById('product-form').dataset.mode = 'create';
        document.getElementById('product-image-preview').src = Config.DEFAULT_PRODUCT_IMAGE;
        this.populateCategorySelect();
        // Reset gallery state
        this.existingImages = [];
        this.pendingImages = [];
        this.removedImageIds = [];
        this.renderGallery();
        modal.classList.remove('hidden');
    },

    async showEditProduct(productId) {
        try {
            const product = await SellerAPI.getProduct(productId);
            await this.loadCategoriesIfNeeded();

            const modal = document.getElementById('product-form-modal');
            document.getElementById('product-form-title').textContent = 'Edit Product';
            const form = document.getElementById('product-form');
            form.dataset.productId = productId;
            form.dataset.mode = 'edit';

            // Populate fields
            form.querySelector('[name="name"]').value = product.name || '';
            form.querySelector('[name="list_price"]').value = product.price || '';
            form.querySelector('[name="description_sale"]').value = product.description || '';
            form.querySelector('[name="mp_qty"]').value = product.mp_qty || '';
            document.getElementById('product-image-preview').src = product.image_url || Config.DEFAULT_PRODUCT_IMAGE;

            this.populateCategorySelect(product.category?.id);

            // Load gallery images
            this.existingImages = product.images || [];
            this.pendingImages = [];
            this.removedImageIds = [];
            this.renderGallery();

            // Show/hide submit button based on status
            const submitBtn = document.getElementById('btn-submit-product');
            const canEdit = ['draft', 'rejected'].includes(product.status);
            document.querySelectorAll('#product-form input, #product-form textarea, #product-form select').forEach(el => {
                el.disabled = !canEdit;
            });
            // Hide/show gallery add button based on edit permission
            const galleryAddBtn = document.getElementById('gallery-add-btn');
            if (galleryAddBtn) galleryAddBtn.classList.toggle('hidden', !canEdit);

            if (submitBtn) {
                submitBtn.classList.toggle('hidden', product.status !== 'draft' && product.status !== 'rejected');
            }

            modal.classList.remove('hidden');
        } catch (error) {
            console.error('Edit product error:', error);
            this.showToast('Failed to load product', 'error');
        }
    },

    async loadCategoriesIfNeeded() {
        if (this.categories.length) return;
        try {
            const data = await SellerAPI.getCategories();
            this.categories = data.categories || [];
        } catch (error) {
            console.error('Categories error:', error);
        }
    },

    populateCategorySelect(selectedId = null) {
        const select = document.getElementById('product-category');
        if (!select) return;
        select.innerHTML = '<option value="">เลือกหมวดหมู่</option>';
        this.categories.forEach(cat => {
            const opt = document.createElement('option');
            opt.value = cat.id;
            opt.textContent = cat.full_name || cat.name;
            if (selectedId && cat.id === selectedId) opt.selected = true;
            select.appendChild(opt);
        });
        // Add "create new" option
        const newOpt = document.createElement('option');
        newOpt.value = '__new__';
        newOpt.textContent = '+ สร้างหมวดหมู่ใหม่';
        select.appendChild(newOpt);
    },

    onCategoryChange(prefix) {
        const select = document.getElementById(prefix === 'product' ? 'product-category' : 'quickpost-category');
        const input = document.getElementById(prefix === 'product' ? 'product-new-category' : 'quickpost-new-category');
        if (!select || !input) return;
        if (select.value === '__new__') {
            input.classList.remove('hidden');
            input.focus();
        } else {
            input.classList.add('hidden');
            input.value = '';
        }
    },

    async handleProductFormSubmit(event) {
        event.preventDefault();
        const form = event.target;
        const mode = form.dataset.mode;
        const productId = form.dataset.productId;

        const categSelect = document.getElementById('product-category');
        const categValue = categSelect ? categSelect.value : '';
        const newCategInput = document.getElementById('product-new-category');

        const data = {
            name: form.querySelector('[name="name"]').value.trim(),
            list_price: parseFloat(form.querySelector('[name="list_price"]').value) || 0,
            description_sale: form.querySelector('[name="description_sale"]').value,
            mp_qty: parseFloat(form.querySelector('[name="mp_qty"]').value) || 0,
        };

        // Handle category: existing or new
        if (categValue === '__new__') {
            const newName = newCategInput ? newCategInput.value.trim() : '';
            if (!newName) {
                this.showToast('กรุณากรอกชื่อหมวดหมู่ใหม่', 'error');
                if (newCategInput) newCategInput.focus();
                return;
            }
            data.categ_name = newName;
        } else if (categValue) {
            data.categ_id = parseInt(categValue);
        }

        // Main image handling
        const fileInput = form.querySelector('[name="image"]');
        if (fileInput && fileInput.files.length > 0) {
            data.image_1920 = await this.fileToBase64(fileInput.files[0]);
        }

        if (!data.name) {
            this.showToast('กรุณากรอกชื่อสินค้า', 'error');
            return;
        }
        if (!data.categ_id && !data.categ_name) {
            this.showToast('กรุณาเลือกหมวดหมู่สินค้า', 'error');
            return;
        }

        try {
            let savedProductId = productId;
            if (mode === 'create') {
                const result = await SellerAPI.createProduct(data);
                savedProductId = result.id;
                this.showToast('Product created successfully', 'success');
            } else {
                await SellerAPI.updateProduct(productId, data);
                this.showToast('Product updated successfully', 'success');
            }

            // Handle extra images: delete removed, upload new
            if (savedProductId) {
                await this.syncGalleryImages(savedProductId);
            }

            this.closeModal('product-form-modal');
            this.loadProducts();
        } catch (error) {
            console.error('Product save error:', error);
            this.showToast(error.message || 'Failed to save product', 'error');
        }
    },

    async syncGalleryImages(productId) {
        // Delete removed images
        for (const imgId of this.removedImageIds) {
            try {
                await SellerAPI.deleteProductImage(productId, imgId);
            } catch (e) {
                console.error('Delete image error:', e);
            }
        }

        // Upload pending images/videos
        if (this.pendingImages.length > 0) {
            const images = [];
            for (const pending of this.pendingImages) {
                const entry = {};
                if (pending.file) {
                    entry.image_base64 = await this.fileToBase64(pending.file);
                    entry.name = pending.file.name.replace(/\.[^/.]+$/, '');
                }
                if (pending.video_url) {
                    entry.video_url = pending.video_url;
                    if (!entry.name) entry.name = 'Video';
                }
                if (entry.image_base64 || entry.video_url) {
                    images.push(entry);
                }
            }
            try {
                await SellerAPI.uploadProductImages(productId, images);
            } catch (e) {
                console.error('Upload images error:', e);
                this.showToast('Some images failed to upload', 'error');
            }
        }
    },

    async handleSubmitForApproval(productId) {
        if (!productId) return;
        try {
            await SellerAPI.submitProduct(productId);
            this.showToast('Product submitted for approval', 'success');
            this.closeModal('product-form-modal');
            this.loadProducts();
        } catch (error) {
            console.error('Submit error:', error);
            this.showToast(error.message || 'Failed to submit product', 'error');
        }
    },

    // ==================== Product Gallery ====================

    handleGalleryAdd(files) {
        if (!files || !files.length) return;
        const totalCount = this.existingImages.length - this.removedImageIds.length + this.pendingImages.length;
        const remaining = 10 - totalCount;
        if (remaining <= 0) {
            this.showToast('Maximum 10 extra images allowed', 'error');
            return;
        }
        const toAdd = Array.from(files).slice(0, remaining);
        for (const file of toAdd) {
            this.pendingImages.push({
                file,
                preview: URL.createObjectURL(file),
            });
        }
        this.renderGallery();
    },

    handleGalleryRemoveExisting(imgId) {
        this.removedImageIds.push(imgId);
        this.renderGallery();
    },

    handleGalleryRemovePending(index) {
        const removed = this.pendingImages.splice(index, 1);
        if (removed[0]?.preview) URL.revokeObjectURL(removed[0].preview);
        this.renderGallery();
    },

    toggleVideoUrlInput() {
        const container = document.getElementById('video-url-input-container');
        if (container) container.classList.toggle('hidden');
    },

    addVideoUrl() {
        const input = document.getElementById('gallery-video-url');
        const url = (input?.value || '').trim();
        if (!url) {
            this.showToast('Please enter a video URL', 'error');
            return;
        }
        const totalCount = this.existingImages.length - this.removedImageIds.length + this.pendingImages.length;
        if (totalCount >= 10) {
            this.showToast('Maximum 10 extra images/videos allowed', 'error');
            return;
        }
        this.pendingImages.push({
            file: null,
            preview: null,
            video_url: url,
        });
        input.value = '';
        document.getElementById('video-url-input-container')?.classList.add('hidden');
        this.renderGallery();
    },

    renderGallery() {
        const grid = document.getElementById('gallery-grid');
        if (!grid) return;

        let html = '';

        // Existing images (not removed)
        this.existingImages.forEach(img => {
            if (this.removedImageIds.includes(img.id)) return;
            const hasVideo = img.video_url ? true : false;
            html += `
                <div class="relative group">
                    <img src="${this.escapeHtml(img.thumbnail)}" class="w-full aspect-square rounded-lg object-cover border">
                    ${hasVideo ? '<span class="absolute top-1 left-1 bg-purple-600 text-white text-[9px] px-1 rounded"><i class="fas fa-video"></i></span>' : ''}
                    <button type="button" onclick="SellerApp.handleGalleryRemoveExisting(${img.id})"
                            class="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white rounded-full text-xs flex items-center justify-center shadow">
                        <i class="fas fa-times text-[10px]"></i>
                    </button>
                </div>
            `;
        });

        // Pending images (new, not yet uploaded)
        this.pendingImages.forEach((pending, idx) => {
            const isVideo = !!pending.video_url;
            html += `
                <div class="relative group">
                    ${isVideo
                        ? `<div class="w-full aspect-square rounded-lg border border-dashed border-purple-400 bg-purple-50 flex flex-col items-center justify-center">
                               <i class="fas fa-video text-purple-500 text-lg mb-1"></i>
                               <span class="text-[9px] text-purple-600 px-1 text-center truncate w-full">${this.escapeHtml(pending.video_url).substring(0, 30)}</span>
                           </div>`
                        : `<img src="${pending.preview}" class="w-full aspect-square rounded-lg object-cover border border-dashed border-green-400">`
                    }
                    <span class="absolute bottom-0 left-0 right-0 bg-green-500 text-white text-[10px] text-center">NEW</span>
                    <button type="button" onclick="SellerApp.handleGalleryRemovePending(${idx})"
                            class="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white rounded-full text-xs flex items-center justify-center shadow">
                        <i class="fas fa-times text-[10px]"></i>
                    </button>
                </div>
            `;
        });

        grid.innerHTML = html || '<p class="text-xs text-gray-400 col-span-4">No extra images yet</p>';
    },

    // ==================== Wallet ====================

    async loadWallet() {
        try {
            const data = await SellerAPI.getWallet();
            const w = data.wallet;
            const limits = data.withdrawal_limits;

            document.getElementById('wallet-balance').textContent = `${w.currency}${this.formatNumber(w.balance)}`;
            document.getElementById('wallet-earned').textContent = `${w.currency}${this.formatNumber(w.total_earned)}`;
            document.getElementById('wallet-withdrawn').textContent = `${w.currency}${this.formatNumber(w.total_withdrawn)}`;

            const withdrawBtn = document.getElementById('btn-withdraw');
            if (withdrawBtn) {
                withdrawBtn.disabled = !limits.can_withdraw;
                withdrawBtn.classList.toggle('opacity-50', !limits.can_withdraw);
            }

            // Store for withdrawal form
            this._walletData = data;

            // Load transactions
            this.loadWalletTransactions();
        } catch (error) {
            console.error('Wallet error:', error);
            this.showToast('Failed to load wallet', 'error');
        }
    },

    async loadWalletTransactions(type = 'all') {
        this.currentTxFilter = type;
        const container = document.getElementById('wallet-transactions');
        container.innerHTML = '<div class="text-center py-4"><div class="animate-spin rounded-full h-6 w-6 border-b-2 border-green-500 mx-auto"></div></div>';

        try {
            const data = await SellerAPI.getWalletTransactions({
                page: this.walletTxPage,
                limit: 20,
                type,
            });

            const txs = data.transactions || [];
            if (!txs.length) {
                container.innerHTML = '<div class="text-center text-gray-400 py-6">No transactions yet</div>';
                return;
            }

            container.innerHTML = txs.map(tx => {
                const isCredit = tx.amount > 0;
                const icon = isCredit ? 'fa-arrow-down' : 'fa-arrow-up';
                const color = isCredit ? 'text-green-600' : 'text-red-600';
                const bg = isCredit ? 'bg-green-50' : 'bg-red-50';
                return `
                    <div class="flex items-center space-x-3 py-3 border-b last:border-0">
                        <div class="w-10 h-10 rounded-full ${bg} flex items-center justify-center">
                            <i class="fas ${icon} ${color}"></i>
                        </div>
                        <div class="flex-1">
                            <p class="text-sm font-medium">${this.escapeHtml(tx.type_display)}</p>
                            <p class="text-xs text-gray-400">${this.escapeHtml(tx.reference)}</p>
                        </div>
                        <div class="text-right">
                            <p class="font-semibold ${color}">${isCredit ? '+' : ''}${tx.currency}${this.formatNumber(Math.abs(tx.amount))}</p>
                            <p class="text-xs text-gray-400">${this.formatDate(tx.date)}</p>
                        </div>
                    </div>
                `;
            }).join('');
        } catch (error) {
            console.error('Transactions error:', error);
            container.innerHTML = '<div class="text-center text-red-500 py-4">Failed to load</div>';
        }
    },

    showWithdrawModal() {
        const modal = document.getElementById('withdraw-modal');
        const w = this._walletData;
        if (!w || !w.withdrawal_limits.can_withdraw) {
            if (w && w.withdrawal_limits.has_pending_request) {
                this.showToast('You have a pending withdrawal request', 'info');
            } else {
                this.showToast('Withdrawal not available', 'info');
            }
            return;
        }
        document.getElementById('withdraw-available').textContent =
            `${w.wallet.currency}${this.formatNumber(w.wallet.balance)}`;
        document.getElementById('withdraw-min').textContent =
            `Min: ${w.wallet.currency}${this.formatNumber(w.withdrawal_limits.min_amount)}`;
        document.getElementById('withdraw-amount').value = '';
        document.getElementById('withdraw-bank-name').value = '';
        document.getElementById('withdraw-account-name').value = '';
        document.getElementById('withdraw-account-number').value = '';
        document.getElementById('withdraw-branch').value = '';
        modal.classList.remove('hidden');
    },

    async handleWithdrawSubmit(event) {
        event.preventDefault();
        const amount = parseFloat(document.getElementById('withdraw-amount').value);
        if (!amount || amount <= 0) {
            this.showToast('Please enter a valid amount', 'error');
            return;
        }

        try {
            await SellerAPI.requestWithdrawal({
                amount,
                payment_method_id: 2, // Bank Transfer (default)
                bank_name: document.getElementById('withdraw-bank-name').value.trim(),
                bank_account_name: document.getElementById('withdraw-account-name').value.trim(),
                bank_account_number: document.getElementById('withdraw-account-number').value.trim(),
                bank_branch: document.getElementById('withdraw-branch').value.trim(),
            });
            this.showToast('Withdrawal request submitted!', 'success');
            this.closeModal('withdraw-modal');
            this.loadWallet();
        } catch (error) {
            console.error('Withdraw error:', error);
            this.showToast(error.message || 'Failed to submit', 'error');
        }
    },

    async showWithdrawalHistory() {
        const modal = document.getElementById('withdrawal-history-modal');
        const container = document.getElementById('withdrawal-history-list');
        container.innerHTML = '<div class="text-center py-4"><div class="animate-spin rounded-full h-6 w-6 border-b-2 border-green-500 mx-auto"></div></div>';
        modal.classList.remove('hidden');

        try {
            const data = await SellerAPI.getWithdrawals({ limit: 20 });
            const wds = data.withdrawals || [];
            if (!wds.length) {
                container.innerHTML = '<div class="text-center text-gray-400 py-6">No withdrawal requests</div>';
                return;
            }
            container.innerHTML = wds.map(wd => {
                const stateClass = this.getWithdrawalStateClass(wd.state);
                return `
                    <div class="bg-white rounded-xl p-4 mb-3 shadow">
                        <div class="flex justify-between items-start mb-2">
                            <div>
                                <p class="font-semibold">${this.escapeHtml(wd.name)}</p>
                                <p class="text-sm text-gray-500">${this.formatDate(wd.requested_date)}</p>
                            </div>
                            <span class="px-2 py-1 rounded-full text-xs ${stateClass}">${this.escapeHtml(wd.state_display)}</span>
                        </div>
                        <div class="flex justify-between items-center">
                            <span class="text-lg font-bold">${wd.currency}${this.formatNumber(wd.amount)}</span>
                            ${wd.state === 'pending' ? `<button onclick="SellerApp.cancelWithdrawal(${wd.id})" class="text-sm text-red-500 underline">Cancel</button>` : ''}
                        </div>
                    </div>
                `;
            }).join('');
        } catch (error) {
            console.error('Withdrawals error:', error);
            container.innerHTML = '<div class="text-center text-red-500 py-4">Failed to load</div>';
        }
    },

    async cancelWithdrawal(id) {
        try {
            await SellerAPI.cancelWithdrawal(id);
            this.showToast('Withdrawal cancelled', 'success');
            this.showWithdrawalHistory();
            this.loadWallet();
        } catch (error) {
            this.showToast(error.message || 'Failed to cancel', 'error');
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
            'cancelled': 'bg-gray-100 text-gray-500',
        };
        return classes[state] || 'bg-gray-100 text-gray-800';
    },

    // ==================== Reports ====================

    async loadReports(period = 'today') {
        this.currentReportPeriod = period;
        try {
            const data = await SellerAPI.getReports(period);

            document.getElementById('report-total-sales').textContent = `${data.currency || '฿'}${this.formatNumber(data.total_sales)}`;
            document.getElementById('report-order-count').textContent = this.formatNumber(data.order_count);
            document.getElementById('report-items-sold').textContent = this.formatNumber(data.items_sold);
            document.getElementById('report-avg-order').textContent = `${data.currency || '฿'}${this.formatNumber(data.avg_order)}`;

            // Top products
            const container = document.getElementById('top-products');
            if (!data.top_products || !data.top_products.length) {
                container.innerHTML = '<div class="text-center text-gray-400 py-4">No data for this period</div>';
                return;
            }
            container.innerHTML = data.top_products.map((p, i) => `
                <div class="flex items-center space-x-3 py-2 border-b last:border-0">
                    <span class="text-lg font-bold text-gray-300 w-6">${i + 1}</span>
                    <img src="${p.image_url || Config.DEFAULT_PRODUCT_IMAGE}" class="w-10 h-10 rounded object-cover">
                    <div class="flex-1">
                        <p class="text-sm font-medium">${this.escapeHtml(p.name)}</p>
                        <p class="text-xs text-gray-400">${p.qty_sold} sold</p>
                    </div>
                    <p class="font-semibold text-green-600">฿${this.formatNumber(p.revenue)}</p>
                </div>
            `).join('');
        } catch (error) {
            console.error('Reports error:', error);
            this.showToast('Failed to load reports', 'error');
        }
    },

    // ==================== Profile ====================

    async loadProfile() {
        try {
            const data = await SellerAPI.getProfile();

            document.getElementById('profile-avatar').src = data.profile_image_url || this.user?.pictureUrl || Config.DEFAULT_AVATAR;
            document.getElementById('profile-name').textContent = data.name;
            document.getElementById('profile-shop').textContent = data.shop?.name || 'No shop';
            document.getElementById('profile-status').textContent = data.state;
            document.getElementById('profile-products').textContent = data.stats.total_products;
            document.getElementById('profile-orders').textContent = data.stats.total_orders;

            const rating = data.average_rating;
            document.getElementById('profile-rating').textContent = rating > 0 ? `${'★'.repeat(Math.round(rating))} ${rating.toFixed(1)}` : 'No rating';
        } catch (error) {
            console.error('Profile error:', error);
            this.showToast('Failed to load profile', 'error');
        }
    },

    async editProfile() {
        try {
            const data = await SellerAPI.getProfile();
            const modal = document.getElementById('profile-edit-modal');
            const form = document.getElementById('profile-edit-form');

            form.querySelector('[name="name"]').value = data.name || '';
            form.querySelector('[name="email"]').value = data.email || '';
            form.querySelector('[name="phone"]').value = data.phone || '';

            modal.classList.remove('hidden');
        } catch (error) {
            this.showToast('Failed to load profile', 'error');
        }
    },

    async handleProfileFormSubmit(event) {
        event.preventDefault();
        const form = event.target;
        const data = {
            name: form.querySelector('[name="name"]').value.trim(),
            email: form.querySelector('[name="email"]').value.trim(),
            phone: form.querySelector('[name="phone"]').value.trim(),
        };

        try {
            await SellerAPI.updateProfile(data);
            this.showToast('Profile updated', 'success');
            this.closeModal('profile-edit-modal');
            this.loadProfile();
        } catch (error) {
            this.showToast(error.message || 'Failed to update profile', 'error');
        }
    },

    async manageShop() {
        try {
            const data = await SellerAPI.getShop();
            const modal = document.getElementById('shop-edit-modal');
            const form = document.getElementById('shop-edit-form');

            form.querySelector('[name="description"]').value = data.description || '';
            form.querySelector('[name="shop_tag_line"]').value = data.shop_tag_line || '';
            form.querySelector('[name="email"]').value = data.email || '';
            form.querySelector('[name="phone"]').value = data.phone || '';

            document.getElementById('shop-name-display').textContent = data.name || '';

            modal.classList.remove('hidden');
        } catch (error) {
            this.showToast(error.message || 'Failed to load shop', 'error');
        }
    },

    async handleShopFormSubmit(event) {
        event.preventDefault();
        const form = event.target;
        const data = {
            description: form.querySelector('[name="description"]').value,
            shop_tag_line: form.querySelector('[name="shop_tag_line"]').value,
            email: form.querySelector('[name="email"]').value.trim(),
            phone: form.querySelector('[name="phone"]').value.trim(),
        };

        try {
            await SellerAPI.updateShop(data);
            this.showToast('Shop updated', 'success');
            this.closeModal('shop-edit-modal');
        } catch (error) {
            this.showToast(error.message || 'Failed to update shop', 'error');
        }
    },

    contactSupport() {
        this.showToast('Please contact LINE OA for support', 'info');
    },

    showNotifications() {
        this.showToast('No new notifications', 'info');
    },

    // ==================== Quick Post ====================

    startQuickPost() {
        this.previousPage = this.currentPage;
        this.quickPostPhotoFile = null;
        this.quickPostExtraFiles = [];
        this.lastCreatedProductId = null;
        this.quickPostExpanded = false;

        // Reset form
        const nameEl = document.getElementById('quickpost-name');
        const priceEl = document.getElementById('quickpost-price');
        const qtyEl = document.getElementById('quickpost-qty');
        const descEl = document.getElementById('quickpost-description');
        if (nameEl) nameEl.value = '';
        if (priceEl) priceEl.value = '';
        if (qtyEl) qtyEl.value = '';
        if (descEl) descEl.value = '';

        // Reset photo area
        document.getElementById('quickpost-preview').classList.add('hidden');
        document.getElementById('quickpost-preview').src = '';
        document.getElementById('quickpost-no-photo').classList.remove('hidden');
        this.renderQuickPostPhotoGrid();

        // Collapse optional
        const opt = document.getElementById('quickpost-optional');
        if (opt) opt.classList.add('collapsed');
        const icon = document.getElementById('quickpost-expand-icon');
        if (icon) icon.className = 'fas fa-chevron-down mr-1';

        // Hide success overlay
        document.getElementById('quickpost-success').classList.add('hidden');

        // Reset submit button
        const btn = document.getElementById('quickpost-submit-btn');
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-bolt mr-2"></i> โพสต์สินค้า';

        // Load categories async
        this.loadCategoriesIfNeeded().then(() => this.populateQuickPostCategories());

        // Show page then trigger camera
        this.showPage('quickpost');
        const fileInput = document.getElementById('quickpost-camera');
        if (fileInput) {
            fileInput.value = '';
            setTimeout(() => fileInput.click(), 150);
        }
    },

    handleQuickPostPhoto(input) {
        if (!input.files || !input.files[0]) {
            if (!this.quickPostPhotoFile) {
                this.cancelQuickPost();
            }
            return;
        }
        this.quickPostPhotoFile = input.files[0];
        const preview = document.getElementById('quickpost-preview');
        preview.src = URL.createObjectURL(this.quickPostPhotoFile);
        preview.classList.remove('hidden');
        document.getElementById('quickpost-no-photo').classList.add('hidden');
        this.renderQuickPostPhotoGrid();

        // Auto-focus name field
        setTimeout(() => document.getElementById('quickpost-name').focus(), 300);
    },

    handleQuickPostExtraPhotos(input) {
        if (!input.files || !input.files.length) return;
        const maxExtra = 9; // 1 main + 9 extra = 10 total
        const remaining = maxExtra - this.quickPostExtraFiles.length;
        if (remaining <= 0) {
            this.showToast('รูปเพิ่มเติมได้สูงสุด 9 รูป', 'error');
            return;
        }
        const filesToAdd = Array.from(input.files).slice(0, remaining);
        this.quickPostExtraFiles.push(...filesToAdd);
        input.value = '';
        this.renderQuickPostPhotoGrid();
    },

    removeQuickPostExtra(index) {
        this.quickPostExtraFiles.splice(index, 1);
        this.renderQuickPostPhotoGrid();
    },

    renderQuickPostPhotoGrid() {
        const grid = document.getElementById('quickpost-photo-grid');
        // Keep main slot, clear the rest
        const mainSlot = document.getElementById('quickpost-main-slot');
        grid.innerHTML = '';
        grid.appendChild(mainSlot);

        // Render extra photos
        this.quickPostExtraFiles.forEach((file, i) => {
            const div = document.createElement('div');
            div.className = 'relative aspect-square rounded-lg overflow-hidden border border-gray-200';
            div.innerHTML = `
                <img src="${URL.createObjectURL(file)}" class="w-full h-full object-cover">
                <button onclick="SellerApp.removeQuickPostExtra(${i})"
                        class="absolute top-0 right-0 bg-red-500 text-white w-5 h-5 flex items-center justify-center rounded-bl text-xs">&times;</button>
            `;
            grid.appendChild(div);
        });

        // Add "+" button if main photo exists and under limit
        if (this.quickPostPhotoFile && this.quickPostExtraFiles.length < 9) {
            const addBtn = document.createElement('div');
            addBtn.className = 'aspect-square rounded-lg border-2 border-dashed border-gray-300 flex items-center justify-center cursor-pointer bg-gray-50 hover:bg-gray-100';
            addBtn.innerHTML = '<div class="text-center text-gray-400"><i class="fas fa-plus text-xl"></i><p class="text-xs mt-1">เพิ่มรูป</p></div>';
            addBtn.onclick = () => document.getElementById('quickpost-extra-camera').click();
            grid.appendChild(addBtn);
        }
    },

    toggleQuickPostExpand() {
        this.quickPostExpanded = !this.quickPostExpanded;
        const section = document.getElementById('quickpost-optional');
        const icon = document.getElementById('quickpost-expand-icon');
        if (this.quickPostExpanded) {
            section.classList.remove('collapsed');
            icon.className = 'fas fa-chevron-up mr-1';
        } else {
            section.classList.add('collapsed');
            icon.className = 'fas fa-chevron-down mr-1';
        }
    },

    populateQuickPostCategories() {
        const sel = document.getElementById('quickpost-category');
        if (!sel) return;
        sel.innerHTML = '<option value="">เลือกหมวดหมู่</option>';
        (this.categories || []).forEach(cat => {
            const opt = document.createElement('option');
            opt.value = cat.id;
            opt.textContent = cat.full_name || cat.name;
            sel.appendChild(opt);
        });
        // Add "create new" option
        const newOpt = document.createElement('option');
        newOpt.value = '__new__';
        newOpt.textContent = '+ สร้างหมวดหมู่ใหม่';
        sel.appendChild(newOpt);
    },

    async submitQuickPost() {
        const name = document.getElementById('quickpost-name').value.trim();
        const price = parseFloat(document.getElementById('quickpost-price').value);

        if (!name) {
            this.showToast('กรุณากรอกชื่อสินค้า', 'error');
            document.getElementById('quickpost-name').focus();
            return;
        }
        if (!price || price <= 0) {
            this.showToast('กรุณากรอกราคา', 'error');
            document.getElementById('quickpost-price').focus();
            return;
        }
        const categVal = document.getElementById('quickpost-category')?.value;
        const newCategInput = document.getElementById('quickpost-new-category');
        if (!categVal) {
            this.showToast('กรุณาเลือกหมวดหมู่สินค้า', 'error');
            document.getElementById('quickpost-category')?.focus();
            return;
        }
        if (categVal === '__new__') {
            const newName = newCategInput ? newCategInput.value.trim() : '';
            if (!newName) {
                this.showToast('กรุณากรอกชื่อหมวดหมู่ใหม่', 'error');
                if (newCategInput) newCategInput.focus();
                return;
            }
        }

        const btn = document.getElementById('quickpost-submit-btn');
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> กำลังโพสต์...';

        try {
            const data = { name, list_price: price };

            if (this.quickPostPhotoFile) {
                data.image_1920 = await this.fileToBase64(this.quickPostPhotoFile);
            }

            // Handle category: existing or new
            if (categVal === '__new__') {
                data.categ_name = newCategInput.value.trim();
            } else if (categVal) {
                data.categ_id = parseInt(categVal);
            }
            const qty = document.getElementById('quickpost-qty')?.value;
            if (qty) data.mp_qty = parseFloat(qty);
            const desc = document.getElementById('quickpost-description')?.value?.trim();
            if (desc) data.description_sale = desc;

            const result = await SellerAPI.createProduct(data);
            this.lastCreatedProductId = result.id;

            // Upload extra images if any
            if (this.quickPostExtraFiles.length > 0) {
                btn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> กำลังอัปโหลดรูปเพิ่มเติม...';
                try {
                    const images = [];
                    for (const file of this.quickPostExtraFiles) {
                        const base64 = await this.fileToBase64(file);
                        images.push({ image_base64: base64 });
                    }
                    await SellerAPI.uploadProductImages(result.id, images);
                } catch (imgErr) {
                    console.error('Extra images upload error:', imgErr);
                    this.showToast('บางรูปอัปโหลดไม่สำเร็จ', 'error');
                }
            }

            document.getElementById('quickpost-success').classList.remove('hidden');
        } catch (error) {
            console.error('Quick post error:', error);
            this.showToast(error.message || 'ไม่สามารถสร้างสินค้าได้', 'error');
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-bolt mr-2"></i> โพสต์สินค้า';
        }
    },

    async quickPostSubmitForApproval() {
        if (!this.lastCreatedProductId) return;
        try {
            await SellerAPI.submitProduct(this.lastCreatedProductId);
            this.showToast('Product submitted for approval!', 'success');
            this.finishQuickPost();
        } catch (error) {
            console.error('Submit error:', error);
            this.showToast(error.message || 'Failed to submit', 'error');
        }
    },

    cancelQuickPost() {
        this.showPage(this.previousPage || 'dashboard');
    },

    finishQuickPost() {
        document.getElementById('quickpost-success').classList.add('hidden');
        this.showPage('products');
    },

    // ==================== UI Helpers ====================

    closeModal(modalId) {
        document.getElementById(modalId)?.classList.add('hidden');
    },

    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        const colors = {
            success: 'bg-green-500',
            error: 'bg-red-500',
            info: 'bg-blue-500',
        };
        toast.className = `fixed top-4 left-1/2 transform -translate-x-1/2 ${colors[type] || colors.info} text-white px-6 py-3 rounded-lg shadow-lg z-50 transition-opacity duration-300`;
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

    getStatusClass(state) {
        const classes = {
            'pending': 'bg-yellow-100 text-yellow-800',
            'approved': 'bg-blue-100 text-blue-800',
            'shipped': 'bg-purple-100 text-purple-800',
            'done': 'bg-green-100 text-green-800',
            'cancel': 'bg-red-100 text-red-800',
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

    async fileToBase64(file, { square = true, maxSize = 1024 } = {}) {
        return new Promise((resolve, reject) => {
            const img = new Image();
            img.onload = () => {
                const canvas = document.createElement('canvas');
                let sx = 0, sy = 0, sw = img.width, sh = img.height;

                if (square) {
                    // Center-crop to square
                    const size = Math.min(sw, sh);
                    sx = (sw - size) / 2;
                    sy = (sh - size) / 2;
                    sw = size;
                    sh = size;
                }

                // Determine output size
                const outW = square ? Math.min(sw, maxSize) : Math.min(sw, maxSize);
                const outH = square ? outW : Math.round(sh * (outW / sw));

                canvas.width = outW;
                canvas.height = outH;
                const ctx = canvas.getContext('2d');
                ctx.drawImage(img, sx, sy, sw, sh, 0, 0, outW, outH);

                // Export as JPEG for smaller file size
                const dataUrl = canvas.toDataURL('image/jpeg', 0.85);
                const base64 = dataUrl.split(',')[1];
                resolve(base64);
            };
            img.onerror = reject;
            img.src = URL.createObjectURL(file);
        });
    },
};

// Global function bindings for onclick handlers in HTML
function showPage(page) { SellerApp.showPage(page); }
function showAddProduct() { SellerApp.showAddProduct(); }
function editProfile() { SellerApp.editProfile(); }
function manageShop() { SellerApp.manageShop(); }
function contactSupport() { SellerApp.contactSupport(); }
function showNotifications() { SellerApp.showNotifications(); }

document.addEventListener('DOMContentLoaded', () => SellerApp.init());
