// frontend/scripts/main.js
document.addEventListener('DOMContentLoaded', function() {
    // Основные функции для всех страниц
    initializeCommonFeatures();
    
    // Проверка авторизации на защищенных страницах
    checkPageAuth();
    
    // Инициализация специфичных для страницы функций
    initializePageSpecificFunctions();
});

function initializeCommonFeatures() {
    // Инициализация кнопки выхода
    initLogoutButton();
    
    // Обновление информации о пользователе в навигации
    updateUserInfo();
    
    // Обработка всех кнопок навигации
    initNavigationButtons();
    
    // Инициализация обработчиков ошибок
    initErrorHandling();
}

function checkPageAuth() {
    const protectedPages = ['consent.html', 'result.html', 'upload.html', 'profile.html'];
    const currentPage = window.location.pathname.split('/').pop();
    
    if (protectedPages.includes(currentPage)) {
        const token = localStorage.getItem('token');
        if (!token) {
            window.location.href = 'auth.html';
            return false;
        }
    }
    return true;
}

function initializePageSpecificFunctions() {
    const currentPage = window.location.pathname.split('/').pop();
    
    switch(currentPage) {
        case 'index.html':
            initHomePage();
            break;
        case 'result.html':
            initResultPage();
            break;
        case 'consent.html':
            // Уже обрабатывается в consent.js
            break;
        case 'auth.html':
            // Уже обрабатывается в auth.js
            break;
        default:
            // Для других страниц
            if (currentPage.includes('result')) {
                initResultPage();
            }
    }
}

function initHomePage() {
    // Анимация карточек на главной
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform += ' scale(1.05)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = this.style.transform.replace(' scale(1.05)', '');
        });
    });
    
    // Обработка кнопки "Начать анализ"
    const startBtn = document.querySelector('.btn-large');
    if (startBtn) {
        startBtn.addEventListener('click', function(e) {
            const token = localStorage.getItem('token');
            if (!token) {
                e.preventDefault();
                window.location.href = 'auth.html';
            }
        });
    }
}

async function initResultPage() {
    if (!checkPageAuth()) return;
    console.log('=== RESULT PAGE LOADED ===');
    console.log('Token:', localStorage.getItem('token'));
    console.log('User:', localStorage.getItem('user'));
    try {
        showLoading(true);

        console.log('🔍 Loading result page...');

        // 1. Получаем данные пользователя
        let user;
        try {
            user = await TrustFlowAPI.getCurrentUser();
            console.log('✅ User from API:', user);
        } catch (error) {
            console.error('❌ API error, using localStorage:', error);
            user = JSON.parse(localStorage.getItem('user'));
        }
        if (!user) throw new Error('Не удалось загрузить данные пользователя');

        console.log('✅ User data loaded:', user.email);

        // 2. ПОЛУЧАЕМ ИЛИ СОЗДАЕМ кредитный отчет
        let creditData = await TrustFlowAPI.getCreditScore();

        if (!creditData) {
            // Если все еще нет данных
            console.log('❌ No credit data available');
            showNoReportUI(user);
            return;
        }

        console.log('✅ Credit data loaded:', creditData);

        // 3. Обновляем интерфейс
        updateResultPageUI(user, creditData);

    } catch (error) {
        console.error('❌ Error loading result page:', error);
        showError(`Ошибка: ${error.message}`);
    } finally {
        showLoading(false);
    }
}

function createMockCreditData() {
    const score = Math.floor(Math.random() * (750 - 500) + 500);

    let category;
    if (score >= 720) category = "excellent";
    else if (score >= 680) category = "good";
    else if (score >= 620) category = "fair";
    else if (score >= 580) category = "poor";
    else category = "bad";

    return {
        "score": score,
        "score_category": category,
        "reputation_score": score / 850,
        "report_data": JSON.stringify({
            "factors": {
                "payment_history": 85,
                "credit_utilization": Math.floor(Math.random() * 60) + 10,
                "credit_age": Math.floor(Math.random() * 15) + 1
            }
        })
    };
}

function showMockResult() {
    // Показываем демо-результаты даже при ошибке
    const mockData = {
        "score": 750,
        "score_category": "good",
        "message": "Демонстрационные данные"
    };

    // Обновляем UI с демо-данными
    const mainScore = document.getElementById('mainScore');
    const scoreDescription = document.getElementById('scoreDescription');

    if (mainScore) mainScore.textContent = mockData.score;
    if (scoreDescription) {
        const descriptions = {
            'excellent': 'Отличный кредитный рейтинг',
            'good': 'Хороший кредитный рейтинг',
            'fair': 'Средний кредитный рейтинг',
            'poor': 'Низкий кредитный рейтинг',
            'bad': 'Очень низкий кредитный рейтинг'
        };
        scoreDescription.textContent = descriptions[mockData.score_category] || 'Рейтинг рассчитан';
    }
}

function updateResultPageUI(user, creditData) {
    // Обновляем заголовок
    const userName = document.getElementById('userName');
    if (userName && user.full_name) {
        userName.textContent = user.full_name;
    }
    
    // Обновляем кредитный рейтинг
    if (creditData) {
        const mainScore = document.getElementById('mainScore');
        const scoreDescription = document.getElementById('scoreDescription');
        const scoreBar = document.getElementById('scoreBar');
        
        if (mainScore) mainScore.textContent = creditData.score || '0';
        if (scoreDescription) {
            const category = creditData.score_category || 'unknown';
            const descriptions = {
                'excellent': 'Отличный кредитный рейтинг',
                'good': 'Хороший кредитный рейтинг',
                'fair': 'Средний кредитный рейтинг',
                'poor': 'Низкий кредитный рейтинг',
                'bad': 'Очень низкий кредитный рейтинг',
                'unknown': 'Рейтинг не определен'
            };
            scoreDescription.textContent = descriptions[category];
        }
        
        if (scoreBar && creditData.score) {
            const percentage = (creditData.score / 850) * 100;
            scoreBar.style.width = `${percentage}%`;
        }
        
        // Обновляем детали
        updateResultDetails(creditData);
    }
    
    // Обновляем дату
    const updateDate = document.getElementById('updateDate');
    if (updateDate) {
        updateDate.textContent = new Date().toLocaleDateString('ru-RU', {
            day: 'numeric',
            month: 'long',
            year: 'numeric'
        });
    }
}

function updateResultDetails(creditData) {
    // Заполняем детали (используем мок данные если нет реальных)
    const details = {
        historyLength: creditData.report_data?.factors?.credit_age || '5',
        debtIncomeRatio: creditData.report_data?.factors?.credit_utilization || '35',
        onTimePayments: '95',
        activeCredits: '2'
    };
    
    Object.keys(details).forEach(key => {
        const element = document.getElementById(key);
        if (element) {
            element.textContent = details[key] + (key === 'debtIncomeRatio' || key === 'onTimePayments' ? '%' : 
                                                key === 'historyLength' ? ' лет' : '');
        }
    });
}

async function loadCreditHistory() {
    try {
        const token = localStorage.getItem('token');
        const response = await fetch('http://localhost:8000/api/credit/history', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const history = await response.json();
            // Можно отобразить историю в таблице или графике
            console.log('Credit history loaded:', history);
        }
    } catch (error) {
        console.error('Error loading history:', error);
    }
}

function initLogoutButton() {
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Показываем подтверждение
            if (confirm('Вы уверены, что хотите выйти?')) {
                // Очищаем localStorage
                localStorage.removeItem('token');
                localStorage.removeItem('user');
                localStorage.removeItem('consent_given');
                
                // Перенаправляем на главную
                window.location.href = 'index.html';
            }
        });
    }
}

function updateUserInfo() {
    const userData = localStorage.getItem('user');
    const userInfoElements = document.querySelectorAll('.user-info');
    
    if (userData && userInfoElements.length > 0) {
        try {
            const user = JSON.parse(userData);
            userInfoElements.forEach(el => {
                if (user.full_name) {
                    el.textContent = user.full_name;
                } else if (user.email) {
                    el.textContent = user.email.split('@')[0];
                }
            });
        } catch (e) {
            console.error('Error parsing user data:', e);
        }
    }
}

function initNavigationButtons() {
    // Обработка всех кнопок навигации
    document.querySelectorAll('[data-navigate]').forEach(button => {
        button.addEventListener('click', function() {
            const page = this.getAttribute('data-navigate');
            if (page) {
                window.location.href = page;
            }
        });
    });
}

function initErrorHandling() {
    // Глобальный обработчик ошибок fetch
    const originalFetch = window.fetch;
    window.fetch = async function(...args) {
        try {
            const response = await originalFetch.apply(this, args);
            
            // Проверка на 401 Unauthorized
            if (response.status === 401) {
                localStorage.clear();
                window.location.href = 'auth.html';
                return response;
            }
            
            return response;
        } catch (error) {
            console.error('Fetch error:', error);
            throw error;
        }
    };
}

function showLoading(show) {
    const loadingOverlay = document.getElementById('loadingOverlay') || createLoadingOverlay();
    
    if (show) {
        loadingOverlay.style.display = 'flex';
    } else {
        loadingOverlay.style.display = 'none';
    }
}

function createLoadingOverlay() {
    const overlay = document.createElement('div');
    overlay.id = 'loadingOverlay';
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(255, 255, 255, 0.8);
        display: none;
        justify-content: center;
        align-items: center;
        z-index: 9999;
        flex-direction: column;
        gap: 20px;
    `;
    
    overlay.innerHTML = `
        <div class="spinner"></div>
        <p>Загрузка...</p>
    `;
    
    // Добавляем стили для спиннера
    const style = document.createElement('style');
    style.textContent = `
        .spinner {
            width: 50px;
            height: 50px;
            border: 5px solid #f3f3f3;
            border-top: 5px solid #4361ee;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    `;
    
    document.head.appendChild(style);
    document.body.appendChild(overlay);
    
    return overlay;
}

function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'global-error';
    errorDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #f44336;
        color: white;
        padding: 15px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        display: flex;
        align-items: center;
        gap: 10px;
        z-index: 1000;
        animation: slideIn 0.3s ease-out;
    `;
    
    errorDiv.innerHTML = `
        <i class="fas fa-exclamation-triangle"></i>
        <span>${message}</span>
    `;
    
    document.body.appendChild(errorDiv);
    
    // Удаляем через 5 секунд
    setTimeout(() => {
        errorDiv.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => errorDiv.remove(), 300);
    }, 5000);
}

// Глобальные вспомогательные функции
window.TrustFlow = {
    logout: function() {
        localStorage.clear();
        window.location.href = 'auth.html';
    },
    
    getUser: function() {
        const userData = localStorage.getItem('user');
        return userData ? JSON.parse(userData) : null;
    },
    
    isAuthenticated: function() {
        return !!localStorage.getItem('token');
    },
    
    navigateTo: function(page) {
        window.location.href = page;
    }
};