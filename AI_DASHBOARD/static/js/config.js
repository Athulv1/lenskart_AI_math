/**
 * AI_DASHBOARD API Configuration
 * Auto-detects environment and sets correct Flask API URL
 * 
 * Local: http://localhost:5000
 * Production: https://lenskart.thinkneural.ai
 */

const API_CONFIG = (function () {
    // Detect if running on localhost
    const isLocal = window.location.hostname === 'localhost' ||
        window.location.hostname === '127.0.0.1' ||
        window.location.hostname === '';

    // Set Flask API base URL based on environment
    const BASE_URL = isLocal
        ? 'http://localhost:5000'
        : 'https://lenskart.thinkneural.ai/ai-editor';

    // Log environment info
    console.log(`🌐 AI_DASHBOARD Environment: ${isLocal ? 'LOCAL' : 'PRODUCTION'}`);
    console.log(`📡 Flask API Base URL: ${BASE_URL}`);

    return {
        BASE_URL: BASE_URL,
        IS_LOCAL: isLocal,
        IS_PRODUCTION: !isLocal,

        /**
         * Build full API endpoint URL
         * @param {string} path - API endpoint path (e.g., '/upload', 'generate_with_ai')
         * @returns {string} Full URL with base URL
         */
        getEndpoint: function (path) {
            // Remove leading slash if present to avoid double slashes
            const cleanPath = path.startsWith('/') ? path.substring(1) : path;
            return `${this.BASE_URL}/${cleanPath}`;
        },

        /**
         * Get configured fetch options with proper headers
         */
        getFetchOptions: function (method = 'GET', body = null) {
            const options = {
                method: method,
                headers: {
                    'Content-Type': 'application/json'
                }
            };

            if (body) {
                options.body = typeof body === 'string' ? body : JSON.stringify(body);
            }

            return options;
        }
    };
})();

// Make available globally
window.API_CONFIG = API_CONFIG;
