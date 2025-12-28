// TG-Admin Configuration
const CONFIG = {
    // Production
    // API_BASE: 'https://api.tgcommerce.io/v1',

    // Development
    API_BASE: 'http://localhost:8001',

    // App Info
    APP_NAME: 'TG-Admin',
    VERSION: '1.0.0'
};

// Export for ES modules (if needed)
if (typeof module !== 'undefined') {
    module.exports = CONFIG;
}
