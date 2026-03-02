/**
 * LINE LIFF App - Main Application
 */
const App = {
    // State
    user: null,
    cart: null,
    currentPage: 'home',
    productsPage: 1,
    ordersPage: 1,
    selectedAddress: null,
    categories: [],
    provinces: [],
    addresses: [],
    editingAddressId: null,

    // ==================== Initialization ====================

    async init() {
        console.log('Initializing LIFF app...');

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
                // Mock mode - skip LIFF
                await this.initMockMode();
            } else {
                // Production mode - use LIFF
                await this.initLiff();
            }

            // Setup event listeners
            this.setupEventListeners();

            // Load initial data
            await this.loadInitialData();

            // Show app
            this.hideLoading();
            this.showApp();

            // Handle deep-link from Rich Menu (read from sessionStorage to survive LIFF reload)
            const _deepLink = sessionStorage.getItem('liff_deep_link');
            if (_deepLink) {
                sessionStorage.removeItem('liff_deep_link');
                if (['products', 'cart', 'orders', 'profile', 'home'].includes(_deepLink)) {
                    console.log('Deep-link navigating to:', _deepLink);
                    this.showPage(_deepLink);
                }
            }

            console.log('LIFF app initialized successfully');
        } catch (error) {
            if (error.message === 'LOGIN_REQUIRED') {
                console.log('Login required - showing login screen');
                return;
            }
            console.error('Failed to initialize app:', error);
            this.showError(`Error: ${error.code || error.message || error}\n\nLIFF_ID: ${Config.LIFF_ID}\nURL: ${window.location.href}`);
        }
    },

    async initLiff() {
        await liff.init({ liffId: Config.LIFF_ID });

        if (!liff.isLoggedIn()) {
            document.getElementById('loading').classList.add('hidden');
            document.getElementById('login-required').classList.remove('hidden');
            throw new Error('LOGIN_REQUIRED');
        }

        const profile = await liff.getProfile();
        const accessToken = liff.getAccessToken();

        this.user = {
            userId: profile.userId,
            displayName: profile.displayName,
            pictureUrl: profile.pictureUrl,
        };

        API.setAuth(accessToken, profile.userId);

        // Fetch channel config from LIFF ID (Multi-channel support)
        await this.loadChannelConfig();
    },

    async loadChannelConfig() {
        try {
            const context = liff.getContext();
            if (context && context.liffId) {
                const response = await fetch(`${Config.API_BASE_URL}/api/line-buyer/liff/config?liff_id=${context.liffId}`);
                const data = await response.json();

                if (data.success && data.data) {
                    // Update config with channel info
                    Config.CHANNEL_CODE = data.data.channel.code;
                    Config.CHANNEL_NAME = data.data.channel.name;
                    Config.CHANNEL_LIFFS = data.data.liffs || {};

                    // Store for navigation to other LIFFs
                    this.channelLiffs = data.data.liffs;

                    console.log('Channel config loaded:', Config.CHANNEL_CODE);
                }
            }
        } catch (error) {
            console.warn('Could not load channel config:', error);
            // Continue with default config
        }
    },

    navigateToLiff(liffType) {
        // Navigate to another LIFF in the same channel
        if (this.channelLiffs && this.channelLiffs[liffType]) {
            const liffUrl = this.channelLiffs[liffType].liff_url;
            if (liffUrl) {
                window.location.href = liffUrl;
            }
        }
    },

    async initMockMode() {
        console.log('Running in MOCK mode');

        this.user = Config.MOCK_USER;
        API.setAuth(null, this.user.userId);
    },

    // ==================== Event Listeners ====================

    setupEventListeners() {
        // Login button
        document.getElementById('btn-login')?.addEventListener('click', () => {
            liff.login();
        });

        // Navigation tabs
        document.querySelectorAll('.nav-tab, .bottom-nav-item').forEach(tab => {
            tab.addEventListener('click', (e) => {
                const page = e.currentTarget.dataset.page;
                this.showPage(page);
            });
        });

        // Cart button in header
        document.getElementById('btn-cart')?.addEventListener('click', () => {
            this.showPage('cart');
        });

        // Search
        document.getElementById('btn-search')?.addEventListener('click', () => {
            this.searchProducts();
        });

        document.getElementById('search-input')?.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.searchProducts();
            }
        });

        // Filters
        document.getElementById('category-filter')?.addEventListener('change', () => {
            this.loadProducts();
        });

        document.getElementById('sort-filter')?.addEventListener('change', () => {
            this.loadProducts();
        });

        // Pagination
        document.getElementById('btn-prev-page')?.addEventListener('click', () => {
            if (this.productsPage > 1) {
                this.productsPage--;
                this.loadProducts();
            }
        });

        document.getElementById('btn-next-page')?.addEventListener('click', () => {
            this.productsPage++;
            this.loadProducts();
        });

        // Checkout
        document.getElementById('btn-checkout')?.addEventListener('click', () => {
            this.showPage('checkout');
        });

        document.getElementById('checkout-form')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.placeOrder();
        });

        // New address
        document.getElementById('btn-new-address')?.addEventListener('click', () => {
            this.showAddressModal();
        });

        document.getElementById('btn-add-address')?.addEventListener('click', () => {
            this.showAddressModal();
        });

        document.getElementById('address-form')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveAddress();
        });

        document.getElementById('btn-delete-address')?.addEventListener('click', () => {
            this.deleteAddress();
        });

        // Modal close buttons
        document.querySelectorAll('.modal-close').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.target.closest('.modal').classList.add('hidden');
            });
        });

        // Close modal on backdrop click
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    modal.classList.add('hidden');
                }
            });
        });
    },

    // ==================== Data Loading ====================

    async loadInitialData() {
        try {
            // Load categories
            const catData = await API.getCategories();
            this.categories = catData.categories || [];
            this.renderCategories();

            // Load featured products
            const productsData = await API.getFeaturedProducts(8);
            this.renderFeaturedProducts(productsData.items || productsData.products || []);

            // Load cart
            await this.loadCart();
        } catch (error) {
            console.error('Error loading initial data:', error);
        }
    },

    async loadCart() {
        try {
            this.cart = await API.getCart();
            this.updateCartBadge();
        } catch (error) {
            console.error('Error loading cart:', error);
            this.cart = { lines: [], total: 0 };
        }
    },

    // ==================== Page Navigation ====================

    showPage(pageName) {
        // Hide all pages
        document.querySelectorAll('.page').forEach(page => {
            page.classList.add('hidden');
            page.classList.remove('active');
        });

        // Show selected page
        const page = document.getElementById(`page-${pageName}`);
        if (page) {
            page.classList.remove('hidden');
            page.classList.add('active');
        }

        // Update navigation
        document.querySelectorAll('.nav-tab, .bottom-nav-item').forEach(tab => {
            tab.classList.toggle('active', tab.dataset.page === pageName);
        });

        this.currentPage = pageName;

        // Load page-specific data
        switch (pageName) {
            case 'products':
                this.loadProducts();
                break;
            case 'cart':
                this.renderCart();
                break;
            case 'checkout':
                this.loadCheckout();
                break;
            case 'orders':
                this.loadOrders();
                break;
            case 'profile':
                this.loadProfile();
                break;
        }
    },

    // ==================== Products ====================

    async loadProducts() {
        const container = document.getElementById('products-list');
        container.innerHTML = '<div class="text-center text-muted">Loading...</div>';

        try {
            const params = {
                page: this.productsPage,
                limit: Config.PRODUCTS_PER_PAGE,
            };

            const categoryFilter = document.getElementById('category-filter');
            if (categoryFilter?.value) {
                params.category = categoryFilter.value;
            }

            const sortFilter = document.getElementById('sort-filter');
            if (sortFilter?.value) {
                params.sort = sortFilter.value;
            }

            const searchInput = document.getElementById('search-input');
            if (searchInput?.value.trim()) {
                params.search = searchInput.value.trim();
            }

            const data = await API.getProducts(params);
            this.renderProducts(data.items || data.products || [], container);
            this.updatePagination(data.pagination);

        } catch (error) {
            console.error('Error loading products:', error);
            container.innerHTML = '<div class="text-center text-danger">Failed to load products</div>';
        }
    },

    searchProducts() {
        this.productsPage = 1;
        this.loadProducts();
    },

    renderProducts(products, container) {
        if (!products.length) {
            container.innerHTML = '<div class="text-center text-muted">No products found</div>';
            return;
        }

        container.innerHTML = products.map(product => {
            const isLowStock = product.stock_status === 'low_stock';
            const stockBadgeHtml = isLowStock
                ? `<div class="stock-badge low-stock">เหลือ ${Math.floor(product.qty_available)} ชิ้น</div>`
                : '';

            return `
            <div class="product-card">
                <div class="product-card-tap" onclick="App.showProductDetail(${product.id})">
                    <img class="product-image" src="${product.image_url || Config.DEFAULT_PRODUCT_IMAGE}"
                         alt="${this.escapeHtml(product.name)}"
                         onerror="this.src='${Config.DEFAULT_PRODUCT_IMAGE}'">
                    <div class="product-info">
                        <div class="product-name">${this.escapeHtml(product.name)}</div>
                        <div class="product-price">${product.currency}${this.formatNumber(product.price)}</div>
                        ${product.seller ? `<div class="product-seller">ผู้ขาย: ${this.escapeHtml(product.seller.name)}</div>` : ''}
                        ${stockBadgeHtml}
                    </div>
                </div>
                <div class="product-card-actions">
                    <button class="btn-card-detail" onclick="App.showProductDetail(${product.id})">
                        <svg viewBox="0 0 24 24" width="14" height="14"><path fill="currentColor" d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/></svg>
                        รายละเอียด
                    </button>
                    <button class="btn-card-cart" onclick="event.stopPropagation(); App.quickAddToCart(${product.id})">
                        <svg viewBox="0 0 24 24" width="14" height="14"><path fill="currentColor" d="M11 9h2V6h3V4h-3V1h-2v3H8v2h3v3zm-4 9c-1.1 0-1.99.9-1.99 2S5.9 22 7 22s2-.9 2-2-.9-2-2-2zm10 0c-1.1 0-1.99.9-1.99 2s.89 2 1.99 2 2-.9 2-2-.9-2-2-2zm-9.83-3.25l.03-.12.9-1.63h7.45c.75 0 1.41-.41 1.75-1.03l3.58-6.49c.08-.14.12-.31.12-.48 0-.55-.45-1-1-1H5.21l-.94-2H1v2h2l3.6 7.59-1.35 2.45c-.16.28-.25.61-.25.96 0 1.1.9 2 2 2h12v-2H7.42c-.14 0-.25-.11-.25-.25z"/></svg>
                        หยิบใส่ตะกร้า
                    </button>
                </div>
            </div>`;
        }).join('');
    },

    renderFeaturedProducts(products) {
        const container = document.getElementById('featured-products');
        if (container) {
            this.renderProducts(products.slice(0, 4), container);
        }
    },

    updatePagination(pagination) {
        const paginationEl = document.getElementById('products-pagination');
        if (!pagination || pagination.pages <= 1) {
            paginationEl?.classList.add('hidden');
            return;
        }

        paginationEl?.classList.remove('hidden');
        document.getElementById('page-info').textContent =
            `Page ${pagination.page} of ${pagination.pages}`;
        document.getElementById('btn-prev-page').disabled = pagination.page <= 1;
        document.getElementById('btn-next-page').disabled = pagination.page >= pagination.pages;
    },

    async showProductDetail(productId) {
        const modal = document.getElementById('product-modal');
        const container = document.getElementById('product-detail');

        container.innerHTML = '<div class="text-center">Loading...</div>';
        modal.classList.remove('hidden');

        try {
            const product = await API.getProduct(productId);

            // Build gallery images (main + extra)
            const allImages = [product.image_url || Config.DEFAULT_PRODUCT_IMAGE];
            if (product.images && product.images.length) {
                product.images.forEach(img => allImages.push(img.url));
            }
            const galleryHtml = allImages.length > 1
                ? `<div class="pd-gallery">
                       <img class="pd-main-image" id="pd-main-img" src="${allImages[0]}"
                            alt="${this.escapeHtml(product.name)}"
                            onerror="this.src='${Config.DEFAULT_PRODUCT_IMAGE}'">
                       <div class="pd-thumbs">
                           ${allImages.map((url, i) => `
                               <img class="pd-thumb ${i === 0 ? 'active' : ''}" src="${url}"
                                    onclick="App.switchDetailImage(this, '${url}')"
                                    onerror="this.style.display='none'">
                           `).join('')}
                       </div>
                   </div>`
                : `<img class="pd-main-image" src="${allImages[0]}"
                        alt="${this.escapeHtml(product.name)}"
                        onerror="this.src='${Config.DEFAULT_PRODUCT_IMAGE}'">`;

            container.innerHTML = `
                ${galleryHtml}
                <div class="pd-body">
                    <h2 class="pd-name">${this.escapeHtml(product.name)}</h2>
                    <div class="pd-price">${product.currency}${this.formatNumber(product.price)}</div>
                    ${product.seller ? `<div class="pd-seller">
                        <svg viewBox="0 0 24 24" width="14" height="14"><path fill="currentColor" d="M20 4H4v2h16V4zm1 10v-2l-1-5H4l-1 5v2h1v6h10v-6h4v6h2v-6h1zm-9 4H6v-4h6v4z"/></svg>
                        ผู้ขาย: ${this.escapeHtml(product.seller.name)}
                    </div>` : ''}
                    ${product.category ? `<div class="pd-category">
                        <svg viewBox="0 0 24 24" width="14" height="14"><path fill="currentColor" d="M10 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2h-8l-2-2z"/></svg>
                        ${this.escapeHtml(product.category.name)}
                    </div>` : ''}
                    ${product.description ? `
                        <div class="pd-section-title">รายละเอียดสินค้า</div>
                        <p class="pd-desc">${this.escapeHtml(product.description)}</p>
                    ` : ''}
                    ${product.short_description ? `
                        <div class="pd-section-title">คำอธิบายสั้น</div>
                        <p class="pd-desc">${this.escapeHtml(product.short_description)}</p>
                    ` : ''}
                    ${product.stock_status === 'low_stock' ? `<div class="pd-stock-info low-stock">เหลือเพียง ${Math.floor(product.qty_available)} ชิ้น</div>` : ''}
                    ${product.stock_status === 'out_of_stock' ? `<div class="pd-stock-info out-of-stock">สินค้าหมด</div>` : ''}
                    <div class="pd-add-cart">
                        <div class="quantity-selector">
                            <button type="button" onclick="App.decrementQty()">-</button>
                            <input type="number" id="product-qty" value="1" min="1"
                                   max="${product.is_service ? 99 : Math.max(Math.floor(product.qty_available), 1)}">
                            <button type="button" onclick="App.incrementQty()">+</button>
                        </div>
                        <button class="btn btn-primary btn-block" onclick="App.addToCart(${product.id})"
                                ${product.stock_status === 'out_of_stock' ? 'disabled style="background:#ccc;cursor:not-allowed"' : ''}>
                            <svg viewBox="0 0 24 24" width="18" height="18"><path fill="currentColor" d="M11 9h2V6h3V4h-3V1h-2v3H8v2h3v3zm-4 9c-1.1 0-1.99.9-1.99 2S5.9 22 7 22s2-.9 2-2-.9-2-2-2zm10 0c-1.1 0-1.99.9-1.99 2s.89 2 1.99 2 2-.9 2-2-.9-2-2-2zm-9.83-3.25l.03-.12.9-1.63h7.45c.75 0 1.41-.41 1.75-1.03l3.58-6.49c.08-.14.12-.31.12-.48 0-.55-.45-1-1-1H5.21l-.94-2H1v2h2l3.6 7.59-1.35 2.45c-.16.28-.25.61-.25.96 0 1.1.9 2 2 2h12v-2H7.42c-.14 0-.25-.11-.25-.25z"/></svg>
                            ${product.stock_status === 'out_of_stock' ? 'สินค้าหมด' : 'หยิบใส่ตะกร้า'}
                        </button>
                    </div>
                </div>
            `;
        } catch (error) {
            console.error('Error loading product:', error);
            container.innerHTML = '<div class="text-center text-danger">ไม่สามารถโหลดข้อมูลสินค้าได้</div>';
        }
    },

    switchDetailImage(thumbEl, url) {
        document.getElementById('pd-main-img').src = url;
        document.querySelectorAll('.pd-thumb').forEach(t => t.classList.remove('active'));
        thumbEl.classList.add('active');
    },

    incrementQty() {
        const input = document.getElementById('product-qty');
        const max = parseInt(input?.max) || 99;
        if (input && parseInt(input.value) < max) {
            input.value = parseInt(input.value) + 1;
        }
    },

    decrementQty() {
        const input = document.getElementById('product-qty');
        if (input && input.value > 1) {
            input.value = parseInt(input.value) - 1;
        }
    },

    // ==================== Categories ====================

    renderCategories() {
        const container = document.getElementById('categories');
        const filter = document.getElementById('category-filter');

        if (container) {
            container.innerHTML = this.categories.slice(0, 8).map(cat => `
                <div class="category-item" onclick="App.filterByCategory(${cat.id})">
                    <div class="category-icon">
                        ${this.getCategoryIcon(cat.name)}
                    </div>
                    <div class="category-name">${this.escapeHtml(cat.name)}</div>
                </div>
            `).join('');
        }

        if (filter) {
            filter.innerHTML = '<option value="">All Categories</option>' +
                this.categories.map(cat =>
                    `<option value="${cat.id}">${this.escapeHtml(cat.name)}</option>`
                ).join('');
        }
    },

    getCategoryIcon(name) {
        const icons = {
            'food': '🍎', 'drink': '🥤', 'vegetable': '🥬', 'fruit': '🍊',
            'meat': '🥩', 'seafood': '🦐', 'dairy': '🧀', 'bakery': '🍞',
        };
        const lowerName = name.toLowerCase();
        for (const [key, icon] of Object.entries(icons)) {
            if (lowerName.includes(key)) return icon;
        }
        return '📦';
    },

    filterByCategory(categoryId) {
        document.getElementById('category-filter').value = categoryId;
        this.showPage('products');
    },

    // ==================== Cart ====================

    async quickAddToCart(productId) {
        try {
            this.cart = await API.addToCart(productId, 1);
            this.updateCartBadge();
            this.showToast('เพิ่มลงตะกร้าแล้ว', 'success');
        } catch (error) {
            console.error('Error adding to cart:', error);
            this.showToast(error.message, 'error');
        }
    },

    async addToCart(productId) {
        const qtyInput = document.getElementById('product-qty');
        const quantity = qtyInput ? parseInt(qtyInput.value) : 1;

        try {
            this.cart = await API.addToCart(productId, quantity);
            this.updateCartBadge();
            this.showToast('เพิ่มลงตะกร้าแล้ว', 'success');
            document.getElementById('product-modal').classList.add('hidden');
        } catch (error) {
            console.error('Error adding to cart:', error);
            this.showToast(error.message, 'error');
        }
    },

    renderCart() {
        const emptyEl = document.getElementById('cart-empty');
        const itemsEl = document.getElementById('cart-items');
        const summaryEl = document.getElementById('cart-summary');

        if (!this.cart || !this.cart.lines || this.cart.lines.length === 0) {
            emptyEl?.classList.remove('hidden');
            itemsEl.innerHTML = '';
            summaryEl?.classList.add('hidden');
            return;
        }

        emptyEl?.classList.add('hidden');
        summaryEl?.classList.remove('hidden');

        itemsEl.innerHTML = this.cart.lines.map(line => {
            const stockWarning = !line.is_service && line.stock_status === 'low_stock'
                ? `<div class="cart-stock-warning">เหลือ ${Math.floor(line.qty_available)} ชิ้น</div>`
                : (!line.is_service && line.stock_status === 'out_of_stock'
                    ? `<div class="cart-stock-warning" style="color:#c62828">สินค้าหมด</div>`
                    : '');
            const maxQty = line.is_service ? 99 : Math.floor(line.qty_available);
            const plusDisabled = line.quantity >= maxQty ? ' disabled' : '';
            return `
            <div class="cart-item">
                <img class="cart-item-image" src="${line.product.image_url || Config.DEFAULT_PRODUCT_IMAGE}"
                     alt="${this.escapeHtml(line.product.name)}"
                     onerror="this.src='${Config.DEFAULT_PRODUCT_IMAGE}'">
                <div class="cart-item-info">
                    <div class="cart-item-name">${this.escapeHtml(line.product.name)}</div>
                    <div class="cart-item-price">${this.cart.currency}${this.formatNumber(line.price_unit)}</div>
                    ${stockWarning}
                    <div class="cart-item-actions">
                        <div class="cart-item-qty">
                            <button onclick="App.updateCartQty(${line.id}, ${line.quantity - 1})">-</button>
                            <span>${line.quantity}</span>
                            <button onclick="App.updateCartQty(${line.id}, ${line.quantity + 1})"${plusDisabled}>+</button>
                        </div>
                        <button class="cart-item-remove" onclick="App.removeCartItem(${line.id})">ลบ</button>
                    </div>
                </div>
            </div>`;
        }).join('');

        document.getElementById('cart-subtotal').textContent =
            `${this.cart.currency}${this.formatNumber(this.cart.subtotal)}`;
        document.getElementById('cart-tax').textContent =
            `${this.cart.currency}${this.formatNumber(this.cart.tax)}`;
        document.getElementById('cart-total').textContent =
            `${this.cart.currency}${this.formatNumber(this.cart.total)}`;
    },

    async updateCartQty(lineId, quantity) {
        try {
            if (quantity <= 0) {
                await this.removeCartItem(lineId);
                return;
            }
            this.cart = await API.updateCartLine(lineId, quantity);
            this.updateCartBadge();
            this.renderCart();
        } catch (error) {
            console.error('Error updating cart:', error);
            this.showToast(error.message, 'error');
        }
    },

    async removeCartItem(lineId) {
        try {
            this.cart = await API.removeFromCart(lineId);
            this.updateCartBadge();
            this.renderCart();
            this.showToast('Item removed', 'success');
        } catch (error) {
            console.error('Error removing item:', error);
            this.showToast(error.message, 'error');
        }
    },

    updateCartBadge() {
        const count = this.cart?.item_count || 0;
        const badges = [
            document.getElementById('cart-badge'),
            document.getElementById('cart-badge-nav'),
        ];

        badges.forEach(badge => {
            if (badge) {
                badge.textContent = count;
                badge.classList.toggle('hidden', count === 0);
            }
        });
    },

    // ==================== Checkout ====================

    async loadCheckout() {
        await this.loadCart();
        await this.loadAddresses();
        this.renderCheckoutSummary();
    },

    async loadAddresses() {
        try {
            const data = await API.getShippingAddresses();
            this.renderAddresses(data.addresses || []);
        } catch (error) {
            console.error('Error loading addresses:', error);
        }
    },

    renderAddresses(addresses) {
        const container = document.getElementById('address-list');

        if (!addresses.length) {
            container.innerHTML = '<p class="text-muted">No saved addresses</p>';
            return;
        }

        container.innerHTML = addresses.map((addr, index) => `
            <div class="address-item ${index === 0 ? 'selected' : ''}"
                 onclick="App.selectAddress(${addr.id}, this)">
                <div class="address-item-name">${this.escapeHtml(addr.name)}</div>
                <div class="address-item-detail">
                    ${this.escapeHtml(addr.street)}
                    ${addr.city ? ', ' + this.escapeHtml(addr.city) : ''}
                    ${addr.zip ? ' ' + this.escapeHtml(addr.zip) : ''}<br>
                    Tel: ${this.escapeHtml(addr.phone)}
                </div>
            </div>
        `).join('');

        // Select first address by default
        if (addresses.length > 0) {
            this.selectedAddress = addresses[0].id;
        }
    },

    selectAddress(addressId, element) {
        document.querySelectorAll('.address-item').forEach(el => {
            el.classList.remove('selected');
        });
        element.classList.add('selected');
        this.selectedAddress = addressId;
    },

    renderCheckoutSummary() {
        const container = document.getElementById('checkout-summary');
        if (!container || !this.cart) return;

        container.innerHTML = `
            <div class="summary-row">
                <span>Items (${this.cart.item_count || 0})</span>
                <span>${this.cart.currency}${this.formatNumber(this.cart.subtotal)}</span>
            </div>
            <div class="summary-row">
                <span>Tax</span>
                <span>${this.cart.currency}${this.formatNumber(this.cart.tax)}</span>
            </div>
            <div class="summary-row total">
                <span>Total</span>
                <span>${this.cart.currency}${this.formatNumber(this.cart.total)}</span>
            </div>
        `;
    },

    async loadProvinces() {
        if (this.provinces.length > 0) return;

        // Use local Thai address data if available, fallback to API
        if (typeof THAI_ADDRESS_DATA !== 'undefined' && THAI_ADDRESS_DATA.length > 0) {
            this.provinces = THAI_ADDRESS_DATA.map(p => ({ id: p.id, name: p.name }));
        } else {
            try {
                const data = await API.getProvinces();
                this.provinces = data.provinces || [];
            } catch (error) {
                console.error('Error loading provinces:', error);
            }
        }
        this.renderProvinceDropdown();
    },

    renderProvinceDropdown() {
        const select = document.getElementById('addr-province');
        if (!select) return;

        select.innerHTML = '<option value="">เลือกจังหวัด</option>' +
            this.provinces.map(p =>
                `<option value="${p.id}">${this.escapeHtml(p.name)}</option>`
            ).join('');
    },

    // ── Cascading Address Dropdowns ──

    onProvinceChange(provinceId) {
        const districtSelect = document.getElementById('addr-district');
        const subDistrictSelect = document.getElementById('addr-subdistrict');
        const zipInput = document.getElementById('addr-zip');

        // Reset dependent fields
        if (subDistrictSelect) {
            subDistrictSelect.innerHTML = '<option value="">-- เลือกอำเภอก่อน --</option>';
        }
        if (zipInput) zipInput.value = '';

        if (!provinceId || typeof THAI_ADDRESS_DATA === 'undefined') {
            if (districtSelect) {
                districtSelect.innerHTML = '<option value="">-- เลือกจังหวัดก่อน --</option>';
            }
            return;
        }

        const province = THAI_ADDRESS_DATA.find(p => p.id === parseInt(provinceId));
        if (!province || !districtSelect) return;

        districtSelect.innerHTML = '<option value="">เลือกอำเภอ/เขต</option>' +
            province.districts.map(d =>
                `<option value="${this.escapeHtml(d.name)}">${this.escapeHtml(d.name)}</option>`
            ).join('');
    },

    onDistrictChange(districtName) {
        const provinceId = document.getElementById('addr-province')?.value;
        const subDistrictSelect = document.getElementById('addr-subdistrict');
        const zipInput = document.getElementById('addr-zip');

        if (zipInput) zipInput.value = '';

        if (!districtName || !provinceId || typeof THAI_ADDRESS_DATA === 'undefined') {
            if (subDistrictSelect) {
                subDistrictSelect.innerHTML = '<option value="">-- เลือกอำเภอก่อน --</option>';
            }
            return;
        }

        const province = THAI_ADDRESS_DATA.find(p => p.id === parseInt(provinceId));
        const district = province?.districts.find(d => d.name === districtName);
        if (!district || !subDistrictSelect) return;

        subDistrictSelect.innerHTML = '<option value="">เลือกตำบล/แขวง</option>' +
            district.sub_districts.map(s =>
                `<option value="${this.escapeHtml(s.name)}" data-zip="${s.zip}">${this.escapeHtml(s.name)}</option>`
            ).join('');
    },

    onSubDistrictChange(subDistrictName) {
        const zipInput = document.getElementById('addr-zip');
        const subDistrictSelect = document.getElementById('addr-subdistrict');
        if (!zipInput || !subDistrictSelect) return;

        const selected = subDistrictSelect.selectedOptions[0];
        if (selected && selected.dataset.zip) {
            zipInput.value = selected.dataset.zip;
        }
    },

    showAddressModal(addressId = null) {
        this.editingAddressId = addressId;
        const form = document.getElementById('address-form');
        const modal = document.getElementById('address-modal');
        const title = document.getElementById('address-modal-title');
        const deleteBtn = document.getElementById('btn-delete-address');

        form.reset();

        // Reset cascading dropdowns
        const districtSelect = document.getElementById('addr-district');
        const subDistrictSelect = document.getElementById('addr-subdistrict');
        if (districtSelect) districtSelect.innerHTML = '<option value="">-- เลือกจังหวัดก่อน --</option>';
        if (subDistrictSelect) subDistrictSelect.innerHTML = '<option value="">-- เลือกอำเภอก่อน --</option>';

        this.loadProvinces();

        if (addressId) {
            // Edit mode
            title.textContent = 'แก้ไขที่อยู่';
            deleteBtn?.classList.remove('hidden');

            const addr = this.addresses.find(a => a.id === addressId);
            if (addr) {
                document.getElementById('addr-id').value = addr.id;
                document.getElementById('addr-name').value = addr.name || '';
                document.getElementById('addr-phone').value = addr.phone || '';
                document.getElementById('addr-street').value = addr.street || '';
                document.getElementById('addr-zip').value = addr.zip || '';
                document.getElementById('addr-default').checked = addr.is_default || false;

                // Cascading pre-fill: province → district → sub-district
                setTimeout(() => {
                    const provinceSelect = document.getElementById('addr-province');
                    if (provinceSelect && addr.province_id) {
                        provinceSelect.value = addr.province_id;
                        this.onProvinceChange(addr.province_id);

                        // Set district after districts are populated
                        setTimeout(() => {
                            if (districtSelect && addr.city) {
                                districtSelect.value = addr.city;
                                this.onDistrictChange(addr.city);

                                // Set sub-district after sub-districts are populated
                                setTimeout(() => {
                                    if (subDistrictSelect && addr.street2) {
                                        subDistrictSelect.value = addr.street2;
                                    }
                                    // Restore zip (may have been overwritten by cascade)
                                    if (addr.zip) {
                                        document.getElementById('addr-zip').value = addr.zip;
                                    }
                                }, 50);
                            }
                        }, 50);
                    }
                }, 100);
            }
        } else {
            // Create mode
            title.textContent = 'เพิ่มที่อยู่ใหม่';
            deleteBtn?.classList.add('hidden');
            document.getElementById('addr-id').value = '';
        }

        modal.classList.remove('hidden');
    },

    async saveAddress() {
        const address = {
            name: document.getElementById('addr-name').value,
            phone: document.getElementById('addr-phone').value,
            street: document.getElementById('addr-street').value,
            street2: document.getElementById('addr-subdistrict')?.value || '',
            city: document.getElementById('addr-district')?.value || '',
            state_id: parseInt(document.getElementById('addr-province').value) || null,
            zip: document.getElementById('addr-zip').value,
            is_default: document.getElementById('addr-default').checked,
        };

        try {
            if (this.editingAddressId) {
                await API.updateAddress(this.editingAddressId, address);
                this.showToast('บันทึกที่อยู่แล้ว', 'success');
            } else {
                await API.createAddress(address);
                this.showToast('เพิ่มที่อยู่แล้ว', 'success');
            }

            document.getElementById('address-modal').classList.add('hidden');
            this.editingAddressId = null;

            // Reload addresses
            if (this.currentPage === 'profile') {
                await this.loadProfileAddresses();
            } else if (this.currentPage === 'checkout') {
                await this.loadAddresses();
            }
        } catch (error) {
            console.error('Error saving address:', error);
            this.showToast(error.message, 'error');
        }
    },

    async deleteAddress() {
        if (!this.editingAddressId) return;

        if (!confirm('ต้องการลบที่อยู่นี้หรือไม่?')) return;

        try {
            await API.deleteAddress(this.editingAddressId);
            document.getElementById('address-modal').classList.add('hidden');
            this.editingAddressId = null;
            this.showToast('ลบที่อยู่แล้ว', 'success');

            if (this.currentPage === 'profile') {
                await this.loadProfileAddresses();
            } else if (this.currentPage === 'checkout') {
                await this.loadAddresses();
            }
        } catch (error) {
            console.error('Error deleting address:', error);
            this.showToast(error.message, 'error');
        }
    },

    async setDefaultAddress(addressId) {
        try {
            await API.setDefaultAddress(addressId);
            this.showToast('ตั้งเป็นที่อยู่เริ่มต้นแล้ว', 'success');
            await this.loadProfileAddresses();
        } catch (error) {
            console.error('Error setting default:', error);
            this.showToast(error.message, 'error');
        }
    },

    async placeOrder() {
        const note = document.getElementById('order-note')?.value || '';

        try {
            const result = await API.confirmOrder(this.selectedAddress, note);

            // Clear cart
            this.cart = { lines: [], total: 0, item_count: 0 };
            this.updateCartBadge();

            // Show success and go to orders
            this.showToast('Order placed successfully!', 'success');
            this.showPage('orders');

        } catch (error) {
            console.error('Error placing order:', error);
            this.showToast(error.message, 'error');
        }
    },

    // ==================== Profile ====================

    async loadProfile() {
        // Load profile from API
        try {
            const profile = await API.getProfile();
            this.profileData = profile;

            const avatarEl = document.getElementById('profile-avatar');
            if (avatarEl) {
                avatarEl.src = (profile.picture_url || this.user?.pictureUrl || '');
            }
            document.getElementById('profile-name').textContent = profile.name || this.user?.displayName || 'User';
            document.getElementById('profile-phone').textContent = profile.phone || '-';
        } catch (e) {
            // Fallback to LINE user info
            if (this.user) {
                const avatarEl = document.getElementById('profile-avatar');
                if (avatarEl && this.user.pictureUrl) avatarEl.src = this.user.pictureUrl;
                document.getElementById('profile-name').textContent = this.user.displayName || 'User';
            }
        }

        // Load addresses
        await this.loadProfileAddresses();

        // Load seller status
        await this.loadSellerStatus();
    },

    showEditProfile() {
        const section = document.getElementById('edit-profile-section');
        if (!section) return;

        // Pre-fill from profile data
        const p = this.profileData || {};
        document.getElementById('edit-profile-name').value = p.name || '';
        document.getElementById('edit-profile-phone').value = p.phone || '';
        document.getElementById('edit-profile-email').value = p.email || '';

        section.classList.remove('hidden');
        document.getElementById('btn-edit-profile')?.classList.add('hidden');
    },

    hideEditProfile() {
        document.getElementById('edit-profile-section')?.classList.add('hidden');
        document.getElementById('btn-edit-profile')?.classList.remove('hidden');
    },

    async saveProfile() {
        const name = document.getElementById('edit-profile-name').value.trim();
        const phone = document.getElementById('edit-profile-phone').value.trim();
        const email = document.getElementById('edit-profile-email').value.trim();

        if (!name) return this.showToast('กรุณากรอกชื่อ', 'error');
        if (!phone) return this.showToast('กรุณากรอกเบอร์โทร', 'error');

        try {
            await API.updateProfile({ name, phone, email });
            this.showToast('บันทึกข้อมูลแล้ว', 'success');
            this.hideEditProfile();
            await this.loadProfile();
        } catch (e) {
            this.showToast(e.message, 'error');
        }
    },

    // ==================== Seller Application ====================

    async loadSellerStatus() {
        const section = document.getElementById('seller-section');
        if (!section) return;

        try {
            const data = await API.getSellerStatus();
            section.classList.remove('hidden');

            // Hide all status divs
            document.getElementById('seller-not-applied').classList.add('hidden');
            document.getElementById('seller-pending').classList.add('hidden');
            document.getElementById('seller-approved').classList.add('hidden');
            document.getElementById('seller-denied').classList.add('hidden');

            if (!data.is_seller || data.can_apply) {
                document.getElementById('seller-not-applied').classList.remove('hidden');
                // Setup apply button
                const btn = document.getElementById('btn-apply-seller');
                btn.onclick = () => this.applyAsSeller();
            } else if (data.seller_status === 'pending') {
                document.getElementById('seller-pending').classList.remove('hidden');
            } else if (data.seller_status === 'approved') {
                document.getElementById('seller-approved').classList.remove('hidden');
                const shopInfo = document.getElementById('seller-shop-info');
                if (data.shop) {
                    shopInfo.textContent = `ร้าน: ${data.shop.name}`;
                }
                // Setup open seller LIFF button
                const btn = document.getElementById('btn-open-seller-liff');
                btn.onclick = () => {
                    if (this.channelLiffs && this.channelLiffs.seller) {
                        window.location.href = this.channelLiffs.seller.liff_url;
                    } else {
                        this.showToast('ไม่พบ Seller LIFF', 'error');
                    }
                };
            } else if (data.seller_status === 'denied') {
                document.getElementById('seller-denied').classList.remove('hidden');
            }
        } catch (error) {
            console.error('Error loading seller status:', error);
            // Don't show section if error
        }
    },

    async applyAsSeller() {
        const btn = document.getElementById('btn-apply-seller');
        const shopName = document.getElementById('seller-shop-name')?.value?.trim() || '';

        // Confirm
        if (!confirm('ต้องการสมัครเป็นผู้ขายใช่หรือไม่?')) return;

        btn.disabled = true;
        btn.innerHTML = '<span class="spinner-sm"></span> กำลังสมัคร...';

        try {
            const result = await API.applyAsSeller(shopName);
            this.showToast(result.message || 'สมัครสำเร็จ!', 'success');
            // Reload seller status
            await this.loadSellerStatus();
        } catch (error) {
            this.showToast(error.message || 'สมัครไม่สำเร็จ กรุณาลองใหม่', 'error');
            btn.disabled = false;
            btn.innerHTML = 'สมัครเป็นผู้ขาย';
        }
    },

    async loadProfileAddresses() {
        const container = document.getElementById('profile-addresses');
        if (!container) return;

        try {
            const data = await API.getAddresses();
            this.addresses = data.addresses || [];

            if (!this.addresses.length) {
                container.innerHTML = '<p class="text-muted">ยังไม่มีที่อยู่</p>';
                return;
            }

            container.innerHTML = this.addresses.map(addr => `
                <div class="address-card">
                    <div class="address-card-header">
                        <span class="address-card-name">${this.escapeHtml(addr.name)}</span>
                        ${addr.is_default ? '<span class="badge badge-primary">เริ่มต้น</span>' : ''}
                    </div>
                    <div class="address-card-phone">${this.escapeHtml(addr.phone)}</div>
                    <div class="address-card-detail">${this.escapeHtml(addr.full_address || addr.street)}</div>
                    <div class="address-card-actions">
                        <button class="btn btn-sm btn-outline" onclick="App.showAddressModal(${addr.id})">แก้ไข</button>
                        ${!addr.is_default ? `
                            <button class="btn btn-sm btn-outline" onclick="App.setDefaultAddress(${addr.id})">ตั้งเป็นเริ่มต้น</button>
                        ` : ''}
                    </div>
                </div>
            `).join('');
        } catch (error) {
            console.error('Error loading addresses:', error);
            container.innerHTML = '<p class="text-danger">โหลดที่อยู่ไม่สำเร็จ</p>';
        }
    },

    // ==================== Orders ====================

    async loadOrders() {
        const container = document.getElementById('orders-list');
        const emptyEl = document.getElementById('orders-empty');

        container.innerHTML = '<div class="text-center text-muted">Loading...</div>';
        emptyEl?.classList.add('hidden');

        try {
            const data = await API.getOrders({
                page: this.ordersPage,
                limit: Config.ORDERS_PER_PAGE,
            });

            const orders = data.orders || [];

            if (!orders.length) {
                container.innerHTML = '';
                emptyEl?.classList.remove('hidden');
                return;
            }

            container.innerHTML = orders.map(order => `
                <div class="order-card" onclick="App.showOrderDetail(${order.id})">
                    <div class="order-header">
                        <span class="order-number">${this.escapeHtml(order.name)}</span>
                        <span class="order-status ${order.state}">${this.escapeHtml(order.state_display)}</span>
                    </div>
                    <div class="order-date">${this.formatDate(order.date)}</div>
                    <div class="order-total">${order.currency}${this.formatNumber(order.total)}</div>
                    <div class="order-items-preview">${order.item_count} item(s)</div>
                </div>
            `).join('');

        } catch (error) {
            console.error('Error loading orders:', error);
            container.innerHTML = '<div class="text-center text-danger">Failed to load orders</div>';
        }
    },

    async showOrderDetail(orderId) {
        const modal = document.getElementById('order-modal');
        const container = document.getElementById('order-detail');

        container.innerHTML = '<div class="text-center">Loading...</div>';
        modal.classList.remove('hidden');

        try {
            const order = await API.getOrder(orderId);

            container.innerHTML = `
                <div class="order-detail-header">
                    <div class="order-detail-number">${this.escapeHtml(order.name)}</div>
                    <div class="order-status ${order.state}">${this.escapeHtml(order.state_display)}</div>
                    <div class="order-date mt-1">${this.formatDate(order.date)}</div>
                </div>

                <div class="order-detail-section">
                    <h4>Items</h4>
                    ${(order.lines || []).map(line => `
                        <div class="order-line">
                            <img class="order-line-image" src="${line.product.image_url || Config.DEFAULT_PRODUCT_IMAGE}"
                                 onerror="this.src='${Config.DEFAULT_PRODUCT_IMAGE}'">
                            <div class="order-line-info">
                                <div class="order-line-name">${this.escapeHtml(line.product.name)}</div>
                                <div class="order-line-qty">x${line.quantity} @ ${order.currency}${this.formatNumber(line.price_unit)}</div>
                            </div>
                            <div class="order-line-price">${order.currency}${this.formatNumber(line.subtotal)}</div>
                        </div>
                    `).join('')}
                </div>

                ${order.shipping_address ? `
                <div class="order-detail-section">
                    <h4>Shipping Address</h4>
                    <p>
                        ${this.escapeHtml(order.shipping_address.name)}<br>
                        ${this.escapeHtml(order.shipping_address.street)}
                        ${order.shipping_address.city ? ', ' + this.escapeHtml(order.shipping_address.city) : ''}<br>
                        Tel: ${this.escapeHtml(order.shipping_address.phone)}
                    </p>
                </div>
                ` : ''}

                <div class="order-detail-section">
                    <h4>Summary</h4>
                    <div class="summary-row">
                        <span>Subtotal</span>
                        <span>${order.currency}${this.formatNumber(order.subtotal)}</span>
                    </div>
                    <div class="summary-row">
                        <span>Tax</span>
                        <span>${order.currency}${this.formatNumber(order.tax)}</span>
                    </div>
                    <div class="summary-row total">
                        <span>Total</span>
                        <span>${order.currency}${this.formatNumber(order.total)}</span>
                    </div>
                </div>

                <div class="mt-2">
                    <button class="btn btn-outline btn-block" onclick="App.reorder(${order.id})">
                        Reorder
                    </button>
                </div>
            `;
        } catch (error) {
            console.error('Error loading order:', error);
            container.innerHTML = '<div class="text-center text-danger">Failed to load order</div>';
        }
    },

    async reorder(orderId) {
        try {
            await API.reorder(orderId);
            document.getElementById('order-modal').classList.add('hidden');
            await this.loadCart();
            this.showToast('Items added to cart', 'success');
            this.showPage('cart');
        } catch (error) {
            console.error('Error reordering:', error);
            this.showToast(error.message, 'error');
        }
    },

    // ==================== UI Helpers ====================

    hideLoading() {
        document.getElementById('loading').classList.add('hidden');
    },

    showApp() {
        document.getElementById('app').classList.remove('hidden');

        // Update user info
        if (this.user) {
            document.getElementById('user-name').textContent = this.user.displayName;
            const avatar = document.getElementById('user-avatar');
            if (avatar && this.user.pictureUrl) {
                avatar.src = this.user.pictureUrl;
            }
        }
    },

    showError(message) {
        this.hideLoading();
        alert(message);
    },

    showToast(message, type = 'info') {
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        container.appendChild(toast);

        setTimeout(() => {
            toast.remove();
        }, 3000);
    },

    // ==================== Utilities ====================

    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },

    formatNumber(num) {
        return Number(num || 0).toLocaleString('en-US', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
        });
    },

    formatDate(dateStr) {
        if (!dateStr) return '';
        const date = new Date(dateStr);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
        });
    },
};

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    App.init();
});
