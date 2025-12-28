// TG-KDS Configuration
const CONFIG = {
    // Mode: 'local' (POS 직접 연결) or 'cloud' (중앙 서버)
    MODE: 'local',

    // Local Mode (POS가 서버 역할)
    LOCAL_POS_IP: '192.168.0.100',  // POS PC의 IP 주소
    LOCAL_PORT: 8080,

    // Cloud Mode (체인점용)
    CLOUD_API: 'https://api.tgcommerce.io/v1',

    // Development (개발 서버)
    DEV_API: 'http://localhost:8001',

    // App Info
    APP_NAME: 'TG-KDS',
    VERSION: '1.0.0',

    // KDS Settings
    REFRESH_INTERVAL: 3000,  // 3 seconds
    DEFAULT_STORE_ID: 1,
    USE_WEBSOCKET: true,     // WebSocket 사용 (실시간)

    // API Base URL (자동 결정)
    get API_BASE() {
        if (this.MODE === 'local') {
            return `http://${this.LOCAL_POS_IP}:${this.LOCAL_PORT}`;
        } else if (this.MODE === 'cloud') {
            return this.CLOUD_API;
        } else {
            return this.DEV_API;
        }
    },

    // WebSocket URL
    get WS_URL() {
        if (this.MODE === 'local') {
            return `ws://${this.LOCAL_POS_IP}:${this.LOCAL_PORT}/ws`;
        } else if (this.MODE === 'cloud') {
            return this.CLOUD_API.replace('https://', 'wss://').replace('http://', 'ws://') + '/kds/ws';
        }
        return null;
    }
};

if (typeof module !== 'undefined') {
    module.exports = CONFIG;
}
