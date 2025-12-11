class TrustFlowAPI {
    constructor() {
        this.baseURL = 'http://localhost:8000'; // Измените на ваш URL бэкенда
        this.token = localStorage.getItem('token');
    }

    // Установка заголовков
    getHeaders() {
        const headers = {
            'Content-Type': 'application/json'
        };
        
        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }
        
        return headers;
    }

    // Обработка ошибок
    handleError(error) {
        console.error('API Error:', error);
        throw error;
    }

    // Авторизация
    async login(email, password) {
        try {
            const response = await fetch(`${this.baseURL}/api/auth/login`,