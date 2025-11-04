/**
 * Unified API Configuration for Lenskart Backend
 * Auto-detects environment and sets correct API URLs
 * 
 * Usage:
 *   - Django templates: <script src="/static/js/config.js"></script>
 *   - Flask templates: <script src="{{ url_for('static', filename='js/config.js') }}"></script>
 * 
 * Environment Detection:
 *   - Local: http://localhost:5000 (Flask), http://localhost:8001 (Django)
 *   - Production: https://lenskart.thinkneural.ai
 */

const API_CONFIG = (function() {
    // Detect if running on localhost
    const isLocal = window.location.hostname === 'localhost' || 
                    window.location.hostname === '127.0.0.1' ||
                    window.location.hostname === '';
    
    // Set base URLs based on environment
    const FLASK_BASE_URL = isLocal 
        ? 'http://localhost:5000' 
        : 'https://lenskart.thinkneural.ai';
    
    const DJANGO_BASE_URL = isLocal 
        ? 'http://localhost:8001' 
        : 'https://lenskart.thinkneural.ai';
    
    // Log environment info
    console.log(`🌐 Environment: ${isLocal ? 'LOCAL' : 'PRODUCTION'}`);
    console.log(`📡 Flask API: ${FLASK_BASE_URL}`);
    console.log(`📡 Django API: ${DJANGO_BASE_URL}`);
    
    return {
        // Primary base URL (Flask AI_DASHBOARD) - for backward compatibility
        BASE_URL: FLASK_BASE_URL,
        
        // Specific service URLs
        FLASK_URL: FLASK_BASE_URL,
        DJANGO_URL: DJANGO_BASE_URL,
        
        // Environment flags
        IS_LOCAL: isLocal,
        IS_PRODUCTION: !isLocal,
        
        /**
         * Build full API endpoint URL for Flask
         * @param {string} path - API endpoint path (e.g., '/upload', 'generate_with_ai')
         * @returns {string} Full URL with base URL
         */
        getEndpoint: function(path) {
            const cleanPath = path.startsWith('/') ? path.substring(1) : path;
            return `${this.FLASK_URL}/${cleanPath}`;
        },
        
        /**
         * Build full API endpoint URL for Django
         * @param {string} path - API endpoint path
         * @returns {string} Full URL with Django base URL
         */
        getDjangoEndpoint: function(path) {
            const cleanPath = path.startsWith('/') ? path.substring(1) : path;
            return `${this.DJANGO_URL}/${cleanPath}`;
        },
        
        /**
         * Get configured fetch options with proper headers
         * @param {string} method - HTTP method (GET, POST, etc.)
         * @param {object|string|null} body - Request body
         * @returns {object} Fetch options object
         */
        getFetchOptions: function(method = 'GET', body = null) {
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
