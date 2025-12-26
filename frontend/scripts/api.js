console.log('✅ api.js загружен');

window.TrustFlowAPI = {
    baseURL: '/api',

    async getCurrentUser() {
        const token = localStorage.getItem('token');

        try {
            const response = await fetch(`${this.baseURL}/users/me`, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const user = await response.json();
            return user;
        } catch (error) {
            console.error('❌ Ошибка getCurrentUser:', error);
            throw error;
        }
    },

    async getCreditScore() {
        const score = Math.floor(Math.random() * (850 - 300 + 1)) + 300;

        let category;
        if (score >= 720) category = 'excellent';
        else if (score >= 680) category = 'good';
        else if (score >= 620) category = 'fair';
        else if (score >= 580) category = 'poor';
        else category = 'bad';

        const historyLength = Math.floor(Math.random() * (20 - 1 + 1)) + 1;
        const debtIncomeRatio = Math.floor(Math.random() * (60 - 10 + 1)) + 10;
        const onTimePayments = Math.floor(Math.random() * (100 - 70 + 1)) + 70;
        const activeCredits = Math.floor(Math.random() * (8 - 0 + 1));

        return {
            score: score,
            score_category: category,
            report_data: JSON.stringify({
                factors: {
                    payment_history: onTimePayments,
                    credit_utilization: debtIncomeRatio,
                    credit_age: historyLength,
                    on_time_payments: onTimePayments,
                    active_credits: activeCredits
                }
            })
        };
    },

    async getOrCreateCreditScore() {
        return await this.getCreditScore();
    }
};

console.log('🎯 TrustFlowAPI создан');
