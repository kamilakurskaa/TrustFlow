// frontend/js/api.js
const API_BASE_URL = 'http://localhost:8000/api';

class TrustFlowAPI {
    constructor() {
        this.token = localStorage.getItem('token');
    }

    async request(endpoint, options = {}) {
        const url = `${API_BASE_URL}${endpoint}`;

        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        const response = await fetch(url, {
            ...options,
            headers
        });

        if (!response.ok) {
            if (response.status === 401) {
                // Токен истек или недействителен
                localStorage.removeItem('token');
                window.location.href = 'login.html';
            }
            throw new Error(`HTTP ${response.status}: ${await response.text()}`);
        }

        return await response.json();
    }

    // Аутентификация
    async login(email, password) {
        return this.request('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ email, password })
        });
    }

    async register(userData) {
        return this.request('/auth/register', {
            method: 'POST',
            body: JSON.stringify(userData)
        });
    }

    // Пользователи
    async getCurrentUser() {
        return this.request('/users/me');
    }

    async updateUser(userData) {
        return this.request('/users/me', {
            method: 'PUT',
            body: JSON.stringify(userData)
        });
    }

    // Кредитные операции
    async getTransactions() {
        return this.request('/credits/transactions');
    }

    async createTransaction(transactionData) {
        return this.request('/credits/transactions', {
            method: 'POST',
            body: JSON.stringify(transactionData)
        });
    }

    async getCreditScore() {
        return this.request('/credits/score');
    }

    // Блокчейн
    async getBlockchainHistory() {
        return this.request('/credits/blockchain');
    }
}

// Создаем глобальный экземпляр API
const api = new TrustFlowAPI();