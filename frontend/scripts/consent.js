document.addEventListener('DOMContentLoaded', function() {
    // Проверяем авторизацию
    checkAuth();
    
    // Обработка кнопки "Дать согласие"
    const giveConsentBtn = document.getElementById('giveConsent');
    if (giveConsentBtn) {
        giveConsentBtn.addEventListener('click', handleConsent);
    }
    
    // Загрузка данных пользователя
    loadUserData();
});

function checkAuth() {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = 'auth.html';
        return;
    }
}

function loadUserData() {
    const userData = localStorage.getItem('user');
    if (userData) {
        try {
            const user = JSON.parse(userData);
            // Можно обновить интерфейс с данными пользователя
            console.log('User loaded:', user.email);
        } catch (e) {
            console.error('Error parsing user data:', e);
        }
    }
}

async function handleConsent(e) {
    e.preventDefault();
    
    const agreeConsent = document.getElementById('agreeConsent');
    const button = e.target;
    
    if (!agreeConsent || !agreeConsent.checked) {
        alert('Пожалуйста, дайте согласие на обработку данных');
        return;
    }
    
    try {
        // Показываем индикатор загрузки
        const originalText = button.innerHTML;
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Обработка...';
        button.disabled = true;
        
        const token = localStorage.getItem('token');
        if (!token) {
            throw new Error('Требуется авторизация');
        }
        
        // Обновляем статус согласия у пользователя
        const response = await fetch('http://localhost:8000/api/users/me/profile', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                // Здесь можно передать данные для профиля
                consent_given: true,
                consent_date: new Date().toISOString()
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Ошибка сохранения согласия');
        }
        
        // Сохраняем статус согласия в localStorage
        localStorage.setItem('consent_given', 'true');
        localStorage.setItem('consent_date', new Date().toISOString());
        
        // Показываем успешное сообщение
        showSuccess('Согласие успешно принято!');
        
        // Перенаправляем на страницу загрузки документа
        setTimeout(() => {
            window.location.href = 'upload.html';
        }, 1500);
        
    } catch (error) {
        console.error('Consent error:', error);
        alert(`Ошибка: ${error.message}`);
    } finally {
        // Восстанавливаем кнопку
        if (button) {
            button.innerHTML = '<i class="fas fa-check"></i> Дать согласие и продолжить';
            button.disabled = false;
        }
    }
}

function showSuccess(message) {
    // Создаем сообщение об успехе
    const successDiv = document.createElement('div');
    successDiv.className = 'success-message';
    successDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #4CAF50;
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
    
    successDiv.innerHTML = `
        <i class="fas fa-check-circle"></i>
        <span>${message}</span>
    `;
    
    // Добавляем стили для анимации
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
    `;
    document.head.appendChild(style);
    
    document.body.appendChild(successDiv);
    
    // Удаляем через 3 секунды
    setTimeout(() => {
        successDiv.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => successDiv.remove(), 300);
    }, 3000);
}

// Добавляем кнопку выхода
document.addEventListener('DOMContentLoaded', function() {
    const navActions = document.querySelector('.nav-actions');
    if (navActions) {
        const logoutBtn = document.createElement('button');
        logoutBtn.className = 'btn btn-outline';
        logoutBtn.innerHTML = '<i class="fas fa-sign-out-alt"></i> Выйти';
        logoutBtn.addEventListener('click', function() {
            localStorage.clear();
            window.location.href = 'auth.html';
        });
        navActions.appendChild(logoutBtn);
    }
});