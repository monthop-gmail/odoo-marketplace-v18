/**
 * Admin LIFF App Configuration
 */
const Config = {
    LIFF_ID: '2009197406-qVLxxuOx',
    API_BASE_URL: window.location.origin,
    CHANNEL_CODE: 'marketplace',
    MOCK_MODE: false,

    MOCK_USER: {
        userId: 'U_ADMIN_MOCK_001',
        displayName: 'Test Admin',
        pictureUrl: '',
    },

    DEFAULT_AVATAR: '/core_line_integration/static/liff/img/avatar.svg',
    MEMBERS_PER_PAGE: 20,
    ORDERS_PER_PAGE: 20,
    NOTIFICATIONS_PER_PAGE: 20,
};

// Allow URL parameter overrides for testing
(function () {
    const params = new URLSearchParams(window.location.search);
    if (params.has('liff_id')) Config.LIFF_ID = params.get('liff_id');
    if (params.has('channel')) Config.CHANNEL_CODE = params.get('channel');
    if (params.has('mock')) Config.MOCK_MODE = params.get('mock') === 'true';
    if (params.has('api')) Config.API_BASE_URL = params.get('api');
    if (params.has('user_id')) Config.MOCK_USER.userId = params.get('user_id');
})();
