const API_URL = 'https://live-weather-2.onrender.com/api';

const loginForm = document.getElementById('loginForm');
const registerForm = document.getElementById('authRegisterForm');

function switchTab(tab) {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    
    if (tab === 'login') {
        document.querySelectorAll('.tab')[0].classList.add('active');
        document.getElementById('loginForm').classList.add('active');
    } else {
        document.querySelectorAll('.tab')[1].classList.add('active');
        document.getElementById('registerForm').classList.add('active');
    }
}

function showLogin() {
    loginForm.classList.remove('hidden');
    registerForm.classList.add('hidden');
    document.querySelectorAll('.tab')[0].classList.add('active');
    document.querySelectorAll('.tab')[1].classList.remove('active');
    clearMessages();
}

function showRegister() {
    registerForm.classList.remove('hidden');
    loginForm.classList.add('hidden');
    document.querySelectorAll('.tab')[1].classList.add('active');
    document.querySelectorAll('.tab')[0].classList.remove('active');
    clearMessages();
}

function clearMessages() {
    document.getElementById('loginMessage').textContent = '';
    document.getElementById('registerMessage').textContent = '';
}

loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    const messageEl = document.getElementById('loginMessage');
    
    try {
        const response = await fetch(`${API_URL}/login`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({email, password})
        });
        
        const data = await response.json();
        
        if (response.ok) {
            localStorage.setItem('user', JSON.stringify(data.user));
            window.location.href = 'home.html';
        } else {
            messageEl.textContent = data.error;
            messageEl.className = 'message error';
        }
    } catch (error) {
        messageEl.textContent = 'Error al conectar con el servidor';
        messageEl.className = 'message error';
    }
});

registerForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const full_name = document.getElementById('registerName').value;
    const email = document.getElementById('registerEmail').value;
    const password = document.getElementById('registerPassword').value;
    const messageEl = document.getElementById('registerMessage');
    
    try {
        const response = await fetch(`${API_URL}/register`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({email, password, full_name})
        });
        
        const data = await response.json();
        
        if (response.ok) {
            messageEl.textContent = '¡Cuenta creada! Ahora puedes iniciar sesión';
            messageEl.className = 'message success';
            registerForm.reset();
        } else {
            messageEl.textContent = data.error;
            messageEl.className = 'message error';
        }
    } catch (error) {
        messageEl.textContent = 'Error al conectar con el servidor';
        messageEl.className = 'message error';
    }
});