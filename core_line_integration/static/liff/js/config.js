/**
 * LIFF App Configuration
 */
const Config = {
    // LIFF ID - Get from LINE Developer Console
    // Replace with your actual LIFF ID
    LIFF_ID: '2009197406-xBQQuZ5s',

    // API Base URL - Odoo server
    API_BASE_URL: window.location.origin,

    // Channel code for this LIFF app
    CHANNEL_CODE: 'marketplace',

    // Mock mode - set to true for local dev without LINE
    MOCK_MODE: false,

    // Mock user for development
    MOCK_USER: {
        userId: 'U1234567890abcdef1234567890abcdef',
        displayName: 'Test User',
        pictureUrl: 'https://profile.line-scdn.net/0h_example',
    },

    // Default images
    DEFAULT_PRODUCT_IMAGE: '/core_line_integration/static/liff/img/placeholder.svg',
    DEFAULT_AVATAR: '/core_line_integration/static/liff/img/avatar.svg',

    // Pagination
    PRODUCTS_PER_PAGE: 12,
    ORDERS_PER_PAGE: 10,
};

// Override with URL parameters (for testing)
(function() {
    const params = new URLSearchParams(window.location.search);

    if (params.has('liff_id')) {
        Config.LIFF_ID = params.get('liff_id');
    }
    if (params.has('channel')) {
        Config.CHANNEL_CODE = params.get('channel');
    }
    if (params.has('mock')) {
        Config.MOCK_MODE = params.get('mock') === 'true';
    }
    if (params.has('api')) {
        Config.API_BASE_URL = params.get('api');
    }
})();
