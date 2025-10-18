// API base URL - change this to match your backend server
const API_BASE = 'http://localhost:8000/api/auth';

// DOM elements
const registerSection = document.getElementById('register-section');
const loginSection = document.getElementById('login-section');
const profileSection = document.getElementById('profile-section');
const registerForm = document.getElementById('register-form');
const loginForm = document.getElementById('login-form');

// Token management
let authToken = localStorage.getItem('authToken');

// Initialize the app
document.addEventListener('DOMContentLoaded', function() {
    if (authToken) {
        loadProfile();
    } else {
        showLogin();
    }
});

// Show/hide sections
function showRegister() {
    registerSection.classList.remove('hidden');
    loginSection.classList.add('hidden');
    profileSection.classList.add('hidden');
    clearMessages();
}

function showLogin() {
    loginSection.classList.remove('hidden');
    registerSection.classList.add('hidden');
    profileSection.classList.add('hidden');
    clearMessages();
}

function showProfile() {
    profileSection.classList.remove('hidden');
    registerSection.classList.add('hidden');
    loginSection.classList.add('hidden');
    clearMessages();
}

// Clear all messages
function clearMessages() {
    const messages = document.querySelectorAll('.message');
    messages.forEach(msg => {
        msg.classList.add('hidden');
        msg.textContent = '';
    });
}

// Show message
function showMessage(elementId, message, isError = false) {
    const messageEl = document.getElementById(elementId);
    messageEl.textContent = message;
    messageEl.className = isError ? 'message error' : 'message success';
    messageEl.classList.remove('hidden');
}

// API call helper
async function apiCall(endpoint, method = 'GET', data = null, requiresAuth = false) {
    const url = `${API_BASE}${endpoint}`;
    const headers = {
        'Content-Type': 'application/json'
    };

    if (requiresAuth && authToken) {
        headers['Authorization'] = `Bearer ${authToken}`;
    }

    const config = {
        method,
        headers
    };

    if (data) {
        config.body = JSON.stringify(data);
    }

    try {
        const response = await fetch(url, config);
        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.detail || `HTTP error! status: ${response.status}`);
        }

        return result;
    } catch (error) {
        throw error;
    }
}

// Register form handler
registerForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const username = document.getElementById('register-username').value.trim();
    const password = document.getElementById('register-password').value;

    if (username.length < 3) {
        showMessage('register-message', 'Username must be at least 3 characters long', true);
        return;
    }

    if (password.length < 6) {
        showMessage('register-message', 'Password must be at least 6 characters long', true);
        return;
    }

    try {
        const result = await apiCall('/register', 'POST', {
            username: username,
            password: password
        });

        showMessage('register-message', 'Registration successful! You can now login.');
        registerForm.reset();
        setTimeout(() => showLogin(), 2000);

    } catch (error) {
        showMessage('register-message', error.message, true);
    }
});

// Login form handler
loginForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const username = document.getElementById('login-username').value.trim();
    const password = document.getElementById('login-password').value;

    try {
        const result = await apiCall('/login', 'POST', {
            username: username,
            password: password
        });

        authToken = result.access_token;
        localStorage.setItem('authToken', authToken);
        
        showMessage('login-message', 'Login successful!');
        loginForm.reset();
        setTimeout(() => loadProfile(), 1000);

    } catch (error) {
        showMessage('login-message', error.message, true);
    }
});

// Load user profile
async function loadProfile() {
    try {
        const profile = await apiCall('/profile', 'GET', null, true);
        
        const profileInfo = document.getElementById('profile-info');
        profileInfo.innerHTML = `
            <p><strong>User ID:</strong> ${profile.id}</p>
            <p><strong>Username:</strong> ${profile.username}</p>
            <p><strong>Member since:</strong> ${new Date(profile.created_at).toLocaleDateString()}</p>
        `;
        
        showProfile();

    } catch (error) {
        showMessage('profile-message', 'Failed to load profile: ' + error.message, true);
        // If token is invalid, logout
        if (error.message.includes('401') || error.message.includes('Invalid') || error.message.includes('invalidated')) {
            logout();
        }
    }
}

// Logout function
async function logout() {
    try {
        if (authToken) {
            await apiCall('/logout', 'POST', null, true);
        }
    } catch (error) {
        console.error('Logout error:', error);
    } finally {
        authToken = null;
        localStorage.removeItem('authToken');
        showLogin();
        showMessage('login-message', 'You have been logged out.');
    }
}