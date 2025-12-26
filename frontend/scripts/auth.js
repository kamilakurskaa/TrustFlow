// frontend/scripts/auth.js
document.addEventListener('DOMContentLoaded', function() {
    // Проверяем, авторизован ли пользователь
    checkAuthStatus();
    
    // Переключение между вкладками
    const loginTab = document.getElementById('loginTab');
    const registerTab = document.getElementById('registerTab');
    
    if (loginTab && registerTab) {
        loginTab.addEventListener('click', () => switchTab('login'));
        registerTab.addEventListener('click', () => switchTab('register'));
    }
    
    // Обработка формы входа
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    
    // Обработка формы регистрации
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegister);
    }
    
    // Восстановление пароля
    const forgotPassword = document.getElementById('forgotPassword');
    if (forgotPassword) {
        forgotPassword.addEventListener('click', handleForgotPassword);
    }
});

console.log('Auth script loaded');

function checkAuthStatus() {
    console.log('checkAuthStatus called');
    const token = localStorage.getItem('token');
    console.log('Token:', token);

    // ВРЕМЕННО отключаем редирект
    // if (token && window.location.pathname.includes('auth.html')) {
    //     window.location.href = 'index.html';
    // }
}

function switchTab(tabName) {
    const loginTab = document.getElementById('loginTab');
    const registerTab = document.getElementById('registerTab');
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    
    if (!loginTab || !registerTab) return;
    
    // Обновляем активные табы
    loginTab.classList.toggle('active', tabName === 'login');
    registerTab.classList.toggle('active', tabName === 'register');
    
    // Показываем/скрываем формы
    if (loginForm) loginForm.classList.toggle('active', tabName === 'login');
    if (registerForm) registerForm.classList.toggle('active', tabName === 'register');
}

async function handleLogin(e) {
    console.log('Handle login called');
    console.log('Event type:', e.type);

    e.preventDefault();
    console.log('Default prevented');
    //e.stopPropagation();
    console.log('Propagation stopped');

    console.log('Login started');
    const email = document.getElementById('loginEmail')?.value;
    const password = document.getElementById('loginPassword')?.value;
    const submitBtn = document.querySelector('#loginForm button[type="button"]');
    
    if (!email || !password) {
        showError('Пожалуйста, заполните все поля');
        return;
    }
    
    // Валидация email
    if (!validateEmail(email)) {
        showError('Введите корректный email адрес');
        return;
    }
    
    try {
        // Показываем индикатор загрузки
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Вход...';
        submitBtn.disabled = true;
        
        // Выполняем запрос
        const response = await fetch('http://localhost:8000/api/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: email,
                password: password
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Ошибка входа');
        }
        
        // Сохраняем токен и данные пользователя
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('user', JSON.stringify(data.user));
        
        // Показываем успешное сообщение
        showSuccess('Вход выполнен успешно!');
        
        // Перенаправляем через 1 секунду
        setTimeout(() => {
            window.location.href = 'consent.html';
        }, 1000);
        
    } catch (error) {
        console.error('Login error:', error);
        showError(error.message || 'Ошибка при входе в систему');
    } finally {
        // Восстанавливаем кнопку
        if (submitBtn) {
            submitBtn.innerHTML = '<i class="fas fa-sign-in-alt"></i> Войти';
            submitBtn.disabled = false;
        }
    }
}

async function handleLoginSubmit() {
    const email = document.getElementById('loginEmail')?.value;
    const password = document.getElementById('loginPassword')?.value;

    if (!email || !password) {
        showError('Заполните все поля');
        return;
    }

    // Вызываем существующую логику
    const fakeEvent = { preventDefault: () => {}, target: document.getElementById('loginForm') };
    await handleLogin(fakeEvent);
}

// Сделаем функцию глобальной
window.handleLoginSubmit = handleLoginSubmit;

async function handleRegister(e) {
    e.preventDefault();
    
    const email = document.getElementById('registerEmail')?.value;
    const password = document.getElementById('registerPassword')?.value;
    const confirmPassword = document.getElementById('confirmPassword')?.value;
    const agreeTerms = document.getElementById('agreeTerms')?.checked;
    const submitBtn = e.target.querySelector('button[type="submit"]');
    
    // Валидация
    if (!email || !password || !confirmPassword) {
        showError('Пожалуйста, заполните все поля');
        return;
    }
    
    if (!validateEmail(email)) {
        showError('Введите корректный email адрес');
        return;
    }
    
    if (password.length < 8) {
        showError('Пароль должен быть не менее 8 символов');
        return;
    }
    
    if (password !== confirmPassword) {
        showError('Пароли не совпадают');
        return;
    }
    
    if (!agreeTerms) {
        showError('Необходимо согласиться с условиями использования');
        return;
    }
    
    try {
        // Показываем индикатор загрузки
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Регистрация...';
        submitBtn.disabled = true;
        
        // Выполняем запрос
        const response = await fetch('http://localhost:8000/api/auth/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: email,
                password: password,
                consent_data_processing: true,
                has_credit_history: null
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Ошибка регистрации');
        }
        
        // Автоматически входим после регистрации
        const loginResponse = await fetch('http://localhost:8000/api/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: email,
                password: password
            })
        });
        
        const loginData = await loginResponse.json();
        
        if (!loginResponse.ok) {
            throw new Error(loginData.detail || 'Ошибка автоматического входа');
        }
        
        // Сохраняем токен и данные пользователя
        localStorage.setItem('token', loginData.access_token);
        localStorage.setItem('user', JSON.stringify(loginData.user));
        
        showSuccess('Регистрация прошла успешно!');
        
        // Перенаправляем через 1 секунду
        setTimeout(() => {
            window.location.href = 'consent.html';
        }, 1000);
        
    } catch (error) {
        console.error('Register error:', error);
        showError(error.message || 'Ошибка при регистрации');
    } finally {
        // Восстанавливаем кнопку
        if (submitBtn) {
            submitBtn.innerHTML = '<i class="fas fa-user-plus"></i> Зарегистрироваться';
            submitBtn.disabled = false;
        }
    }
}

function handleForgotPassword(e) {
    e.preventDefault();
    alert('Функция восстановления пароля временно недоступна. Пожалуйста, свяжитесь с поддержкой.');
}

function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function showError(message) {
    // Создаем или находим контейнер для сообщений
    let errorContainer = document.querySelector('.error-container');
    if (!errorContainer) {
        errorContainer = document.createElement('div');
        errorContainer.className = 'error-container';
        document.querySelector('.auth-card')?.prepend(errorContainer);
    }
    
    // Создаем сообщение об ошибке
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.innerHTML = `
        <i class="fas fa-exclamation-circle"></i>
        <span>${message}</span>
    `;
    
    // Добавляем сообщение
    errorContainer.appendChild(errorDiv);
    
    // Удаляем через 5 секунд
    setTimeout(() => {
        errorDiv.remove();
        if (errorContainer.children.length === 0) {
            errorContainer.remove();
        }
    }, 5000);
}

function showSuccess(message) {
    // Создаем или находим контейнер для сообщений
    let successContainer = document.querySelector('.success-container');
    if (!successContainer) {
        successContainer = document.createElement('div');
        successContainer.className = 'success-container';
        document.querySelector('.auth-card')?.prepend(successContainer);
    }
    
    // Создаем сообщение об успехе
    const successDiv = document.createElement('div');
    successDiv.className = 'success-message';
    successDiv.innerHTML = `
        <i class="fas fa-check-circle"></i>
        <span>${message}</span>
    `;
    
    // Добавляем сообщение
    successContainer.appendChild(successDiv);
    
    // Удаляем через 3 секунды
    setTimeout(() => {
        successDiv.remove();
        if (successContainer.children.length === 0) {
            successContainer.remove();
        }
    }, 3000);
}

// Функция для показа/скрытия пароля
function togglePassword(inputId) {
    const input = document.getElementById(inputId);
    const button = input?.parentNode.querySelector('.show-password');
    
    if (!input || !button) return;
    
    if (input.type === 'password') {
        input.type = 'text';
        button.innerHTML = '<i class="fas fa-eye-slash"></i>';
    } else {
        input.type = 'password';
        button.innerHTML = '<i class="fas fa-eye"></i>';
    }
}

// Добавляем глобальную функцию для кнопок показа пароля
window.togglePassword = togglePassword;