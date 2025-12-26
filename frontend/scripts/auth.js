document.addEventListener('DOMContentLoaded', function() {
    const loginTab = document.getElementById('loginTab');
    const registerTab = document.getElementById('registerTab');
    
    if (loginTab && registerTab) {
        loginTab.addEventListener('click', () => switchTab('login'));
        registerTab.addEventListener('click', () => switchTab('register'));
    }
    
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegister);
    }
});

function switchTab(tabName) {
    const loginTab = document.getElementById('loginTab');
    const registerTab = document.getElementById('registerTab');
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    
    if (!loginTab || !registerTab) return;
    
    loginTab.classList.toggle('active', tabName === 'login');
    registerTab.classList.toggle('active', tabName === 'register');
    
    if (loginForm) loginForm.classList.toggle('active', tabName === 'login');
    if (registerForm) registerForm.classList.toggle('active', tabName === 'register');
}

async function handleLogin(e) {
    e.preventDefault();
    
    const email = document.getElementById('loginEmail')?.value;
    const password = document.getElementById('loginPassword')?.value;
    const submitBtn = document.querySelector('#loginForm button[type="button"]');
    
    if (!email || !password) {
        alert('Заполните все поля');
        return;
    }
    
    try {
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Вход...';
        submitBtn.disabled = true;
        
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Ошибка входа');
        }
        
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('user', JSON.stringify(data.user));
        
        alert('Вход успешен!');
        window.location.href = 'consent.html';
        
    } catch (error) {
        alert('Ошибка: ' + error.message);
    } finally {
        submitBtn.innerHTML = '<i class="fas fa-sign-in-alt"></i> Войти';
        submitBtn.disabled = false;
    }
}

async function handleLoginSubmit() {
    const fakeEvent = { preventDefault: () => {} };
    await handleLogin(fakeEvent);
}

window.handleLoginSubmit = handleLoginSubmit;

async function handleRegister(e) {
    e.preventDefault();
    
    const email = document.getElementById('registerEmail')?.value;
    const password = document.getElementById('registerPassword')?.value;
    const confirmPassword = document.getElementById('confirmPassword')?.value;
    const agreeTerms = document.getElementById('agreeTerms')?.checked;
    const submitBtn = e.target.querySelector('button[type="submit"]');
    
    if (!email || !password || !confirmPassword) {
        alert('Заполните все поля');
        return;
    }
    
    if (password.length < 8) {
        alert('Пароль должен быть не менее 8 символов');
        return;
    }
    
    if (password !== confirmPassword) {
        alert('Пароли не совпадают');
        return;
    }
    
    if (!agreeTerms) {
        alert('Примите условия использования');
        return;
    }
    
    try {
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Регистрация...';
        submitBtn.disabled = true;
        
        const response = await fetch('/api/auth/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                email,
                password,
                consent_data_processing: true
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Ошибка регистрации');
        }
        
        const loginResponse = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        
        const loginData = await loginResponse.json();
        
        if (!loginResponse.ok) {
            throw new Error(loginData.detail || 'Ошибка входа');
        }
        
        localStorage.setItem('token', loginData.access_token);
        localStorage.setItem('user', JSON.stringify(loginData.user));
        
        alert('Регистрация успешна!');
        window.location.href = 'consent.html';
        
    } catch (error) {
        alert('Ошибка: ' + error.message);
    } finally {
        submitBtn.innerHTML = '<i class="fas fa-user-plus"></i> Зарегистрироваться';
        submitBtn.disabled = false;
    }
}

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

window.togglePassword = togglePassword;
