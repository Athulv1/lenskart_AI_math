
const API_CONFIG = (function () {
    const BASE_API_PATH = '/api/dashboard';
    return {
        BASE_URL: BASE_API_PATH,

        getEndpoint: function (path) {
            const cleanPath = path.startsWith('/') ? path.substring(1) : path;
            return `${this.BASE_URL}/${cleanPath}`;
        }
    };
})();

window.API_CONFIG = API_CONFIG;