// Configuration
const API_BASE_URL = 'http://localhost:8000/api/auth';

// DOM Elements
const sections = {
    register: document.getElementById('register-section'),
    login: document.getElementById('login-section'),
    profile: document.getElementById('profile-section')
};

const forms = {
    register: document.getElementById('register-form'),
    login: document.getElementById('login-form')
};

const messages = {
    register: document.getElementById('register-message'),
    login: document.getElementById('login-message'),
    profile: document.getElementById('profile-message')
};

// Navigation links
document.getElementById('show-login').addEventListener('click', () => showSection('login'));
document.getElementById('show-register').addEventListener('click', () => showSection('register'));
document.getElementById('logout-btn').addEventListener('click', logout);
document.getElementById('refresh-profile-btn').addEventListener('click', loadProfile);

// Utility Functions
function showSection(sectionName) {
    Object.values(sections).forEach(section => section.classList.remove('active'));
    sections[sectionName].classList.add('active');
    clearMessages();
}

function showMessage(section, message, type = 'success') {
    const messageEl = messages[section];
    messageEl.innerHTML = `<div class="message ${type}">${message}</div>`;
    setTimeout(() => {
        messageEl.innerHTML = '';
    }, 5000);
}

function clearMessages() {
    Object.values(messages).forEach(msg => msg.innerHTML = '');
}

function getToken() {
    return localStorage.getItem('access_token');
}

function setToken(token) {
    localStorage.setItem('access_token', token);
}

function removeToken() {
    localStorage.removeItem('access_token');
}

// API Functions
async function apiCall(endpoint, method = 'GET', body = null, requiresAuth = false) {
    const headers = {
        'Content-Type': 'application/json'
    };

    if (requiresAuth) {
        const token = getToken();
        if (!token) {
            throw new Error('No authentication token found');
        }
        headers['Authorization'] = `Bearer ${token}`;
    }

    const config = {
        method,
        headers
    };

    if (body) {
        config.body = JSON.stringify(body);
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.detail || 'An error occurred');
    }

    return data;
}

// Form Handlers
forms.register.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const username = document.getElementById('register-username').value;
    const password = document.getElementById('register-password').value;

    try {
        const data = await apiCall('/register', 'POST', { username, password });
        showMessage('register', data.message, 'success');
        forms.register.reset();
        
        // Auto-switch to login after successful registration
        setTimeout(() => {
            showSection('login');
            showMessage('login', 'Registration successful! Please login.', 'success');
        }, 1500);
    } catch (error) {
        showMessage('register', error.message, 'error');
    }
});

forms.login.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;

    try {
        const data = await apiCall('/login', 'POST', { username, password });
        setToken(data.access_token);
        showMessage('login', 'Login successful!', 'success');
        forms.login.reset();
        
        // Switch to profile section and load profile
        setTimeout(async () => {
            showSection('profile');
            await loadProfile();
        }, 500);
    } catch (error) {
        showMessage('login', error.message, 'error');
    }
});

async function loadProfile() {
    try {
        const data = await apiCall('/profile', 'GET', null, true);
        document.getElementById('profile-username').textContent = data.username;
        document.getElementById('profile-created').textContent = new Date(data.created_at).toLocaleString();
        showMessage('profile', 'Profile loaded successfully', 'success');
    } catch (error) {
        showMessage('profile', error.message, 'error');
        // If token is invalid, redirect to login
        if (error.message.includes('token') || error.message.includes('credentials')) {
            removeToken();
            setTimeout(() => {
                showSection('login');
                showMessage('login', 'Session expired. Please login again.', 'error');
            }, 1500);
        }
    }
}

async function logout() {
    try {
        await apiCall('/logout', 'POST', null, true);
        removeToken();
        showMessage('profile', 'Logged out successfully', 'success');
        
        setTimeout(() => {
            showSection('login');
            document.getElementById('profile-username').textContent = '-';
            document.getElementById('profile-created').textContent = '-';
        }, 1000);
    } catch (error) {
        // Even if API call fails, remove token locally
        removeToken();
        showSection('login');
        showMessage('login', 'Logged out (local session cleared)', 'success');
    }
}

// Check if user is already logged in on page load
window.addEventListener('DOMContentLoaded', () => {
    const token = getToken();
    if (token) {
        showSection('profile');
        loadProfile();
    }
});

