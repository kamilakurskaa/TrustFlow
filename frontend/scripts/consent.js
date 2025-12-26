document.addEventListener('DOMContentLoaded', function() {
    checkAuth();
    
    const giveConsentBtn = document.getElementById('giveConsent');
    if (giveConsentBtn) {
        giveConsentBtn.addEventListener('click', handleConsent);
    }
    
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
        const originalText = button.innerHTML;
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Обработка...';
        button.disabled = true;
        
        const token = localStorage.getItem('token');
        if (!token) {
            throw new Error('Требуется авторизация');
        }
        
        const response = await fetch('/api/users/me/profile', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                consent_given: true,
                consent_date: new Date().toISOString()
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Ошибка сохранения согласия');
        }
        
        localStorage.setItem('consent_given', 'true');
        localStorage.setItem('consent_date', new Date().toISOString());
        
        alert('Согласие успешно принято!');
        
        setTimeout(() => {
            window.location.href = 'result.html';
        }, 1000);
        
    } catch (error) {
        console.error('Consent error:', error);
        alert(`Ошибка: ${error.message}`);
    } finally {
        if (button) {
            button.innerHTML = '<i class="fas fa-check"></i> Дать согласие и продолжить';
            button.disabled = false;
        }
    }
}
