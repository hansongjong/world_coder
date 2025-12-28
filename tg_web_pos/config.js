// TG-WebPOS Configuration
const CONFIG = {
    // Production
    // API_BASE: 'https://api.tgcommerce.io/v1',

    // Development
    API_BASE: 'http://localhost:8001',

    // App Info
    APP_NAME: 'TG-WebPOS',
    VERSION: '1.0.0',

    // POS Settings
    DEFAULT_STORE_ID: 1
};

if (typeof module !== 'undefined') {
    module.exports = CONFIG;
}
