// frontend/scripts/api.js
class TrustFlowAPI {
    constructor() {
        this.baseURL = 'http://localhost:8000';
        this.token = localStorage.getItem('token');
    }

    // Обновление токена
    setToken(token) {
        this.token = token;
        localStorage.setItem('token', token);
    }

    // Очистка токена (выход)
    clearToken() {
        this.token = null;
        localStorage.removeItem('token');
        localStorage.removeItem('user');
    }

    // Установка заголовков
    getHeaders(additionalHeaders = {}) {
        const headers = {
            'Content-Type': 'application/json',
            ...additionalHeaders
        };

        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        return headers;
    }

    // Обработка ответа
    async handleResponse(response) {
        if (response.status === 401) {
            // Не авторизован - очищаем данные и перенаправляем
            this.clearToken();
            window.location.href = 'auth.html';
            throw new Error('Требуется авторизация');
        }

        if (response.status === 404) {
            return null; // Возвращаем null для 404, а не ошибку
        }

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `Ошибка ${response.status}`);
        }

        // Для 204 No Content
        if (response.status === 204) {
            return true;
        }

        return await response.json();
    }

    // Обработка ошибок
    handleError(error) {
        console.error('API Error:', error);

        // Показываем пользователю понятное сообщение
        const userMessages = {
            'NetworkError': 'Проблемы с подключением к серверу',
            'Failed to fetch': 'Сервер недоступен',
            'Требуется авторизация': 'Сессия истекла. Войдите заново'
        };

        const message = userMessages[error.message] || error.message || 'Произошла ошибка';
        throw new Error(message);
    }

    // ============ АВТОРИЗАЦИЯ ============

    async login(email, password) {
        try {
            const response = await fetch(`${this.baseURL}/api/auth/login`, {
                method: 'POST',
                headers: this.getHeaders(),
                body: JSON.stringify({ email, password })
            });

            const data = await this.handleResponse(response);

            if (data && data.access_token) {
                this.setToken(data.access_token);
                localStorage.setItem('user', JSON.stringify(data.user || { email }));
            }

            return data;
        } catch (error) {
            this.handleError(error);
        }
    }

    async register(email, password, userData = {}) {
        try {
            const response = await fetch(`${this.baseURL}/api/auth/register`, {
                method: 'POST',
                headers: this.getHeaders(),
                body: JSON.stringify({
                    email,
                    password,
                    ...userData
                })
            });

            const data = await this.handleResponse(response);

            // После регистрации автоматически входим
            if (data && data.id) {
                return await this.login(email, password);
            }

            return data;
        } catch (error) {
            this.handleError(error);
        }
    }

    // ============ ПОЛЬЗОВАТЕЛИ ============

    async getCurrentUser() {
        try {
            const response = await fetch(`${this.baseURL}/api/users/me`, {
                headers: this.getHeaders()
            });

            const data = await this.handleResponse(response);

            if (data) {
                localStorage.setItem('user', JSON.stringify(data));
            }

            return data;
        } catch (error) {
            this.handleError(error);
        }
    }

    async updateUserProfile(profileData) {
        try {
            const response = await fetch(`${this.baseURL}/api/users/me/profile`, {
                method: 'PUT',
                headers: this.getHeaders(),
                body: JSON.stringify(profileData)
            });

            return await this.handleResponse(response);
        } catch (error) {
            this.handleError(error);
        }
    }

    async getUserWithRating() {
        try {
            const response = await fetch(`${this.baseURL}/api/users/me/with-rating`, {
                headers: this.getHeaders()
            });

            return await this.handleResponse(response);
        } catch (error) {
            this.handleError(error);
        }
    }

    // ============ КРЕДИТНЫЙ СКОРИНГ ============

    async getCreditScore() {
        try {
            const response = await fetch(`${this.baseURL}/api/credit/score`, {
                headers: this.getHeaders()
            });

            return await this.handleResponse(response);
        } catch (error) {
            this.handleError(error);
        }
    }

    async requestCreditScore(method = 'demo') {
        try {
            const response = await fetch(`${this.baseURL}/api/credit/request`, {
                method: 'POST',
                headers: this.getHeaders(),
                body: JSON.stringify({
                    method,
                    consent_data_processing: true
                })
            });

            return await this.handleResponse(response);
        } catch (error) {
            this.handleError(error);
        }
    }

    async getCreditRating() {
        try {
            const response = await fetch(`${this.baseURL}/api/credit/rating`, {
                headers: this.getHeaders()
            });

            return await this.handleResponse(response);
        } catch (error) {
            this.handleError(error);
        }
    }

    async getCreditHistory() {
        try {
            const response = await fetch(`${this.baseURL}/api/credit/history`, {
                headers: this.getHeaders()
            });

            return await this.handleResponse(response);
        } catch (error) {
            this.handleError(error);
        }
    }

    async function getOrCreateCreditScore() {
    try {
        // 1. Пытаемся получить существующий отчет
        let score = await this.getCreditScore();

        // 2. Если отчета нет (404 → null), создаем новый
        if (!score) {
            console.log('No credit score found, creating request...');

            // Создаем запрос на расчет
            const requestResult = await this.requestCreditScore('demo');
            console.log('Score calculation requested:', requestResult);

            // Ждем 3 секунды для "расчета"
            await new Promise(resolve => setTimeout(resolve, 3000));

            // Пробуем получить снова
            score = await this.getCreditScore();

            // Если все еще нет, пробуем получить рейтинг
            if (!score) {
                console.log('Still no score, trying rating endpoint...');
                return await this.getCreditRating();
            }
        }

        return score;
    } catch (error) {
        console.error('Error in getOrCreateCreditScore:', error);
        throw error;
    }
}
TrustFlowAPI.prototype.getOrCreateCreditScore = getOrCreateCreditScore;

    async verifyReport(reportId) {
        try {
            const response = await fetch(`${this.baseURL}/api/credit/verify/${reportId}`, {
                method: 'POST',
                headers: this.getHeaders()
            });

            return await this.handleResponse(response);
        } catch (error) {
            this.handleError(error);
        }
    }

    // ============ УТИЛИТЫ ============

    async checkHealth() {
        try {
            const response = await fetch(`${this.baseURL}/`, {
                headers: this.getHeaders()
            });
            return response.ok;
        } catch {
            return false;
        }
    }

    isAuthenticated() {
        return !!this.token;
    }

    getUserData() {
        try {
            const userData = localStorage.getItem('user');
            return userData ? JSON.parse(userData) : null;
        } catch {
            return null;
        }
    }

    logout() {
        this.clearToken();
        window.location.href = 'auth.html';
    }
}

// Создаем глобальный экземпляр API
window.TrustFlowAPI = new TrustFlowAPI();
