// API base URL - change this to match your backend URL
const API_BASE_URL = 'http://localhost:8000';

// Store authentication token
let authToken = localStorage.getItem('authToken');

// DOM elements
const registerSection = document.getElementById('register-section');
const loginSection = document.getElementById('login-section');
const profileSection = document.getElementById('profile-section');

const registerForm = document.getElementById('register-form');
const loginForm = document.getElementById('login-form');
const logoutBtn = document.getElementById('logout-btn');

const registerMessage = document.getElementById('register-message');
const loginMessage = document.getElementById('login-message');
const profileMessage = document.getElementById('profile-message');

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    if (authToken) {
        loadProfile();
    }
    
    registerForm.addEventListener('submit', handleRegister);
    loginForm.addEventListener('submit', handleLogin);
    logoutBtn.addEventListener('click', handleLogout);
});

// Show/hide sections
function showAuthForms() {
    registerSection.classList.remove('hidden');
    loginSection.classList.remove('hidden');
    profileSection.classList.add('hidden');
}

function showProfile() {
    registerSection.classList.add('hidden');
    loginSection.classList.add('hidden');
    profileSection.classList.remove('hidden');
}

// Display messages
function showMessage(element, message, isSuccess) {
    element.textContent = message;
    element.className = 'message show ' + (isSuccess ? 'success' : 'error');
    setTimeout(() => {
        element.className = 'message';
    }, 5000);
}

// Handle registration
async function handleRegister(e) {
    e.preventDefault();
    
    const username = document.getElementById('register-username').value;
    const password = document.getElementById('register-password').value;
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password }),
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage(registerMessage, 'Registration successful! You can now log in.', true);
            registerForm.reset();
        } else {
            showMessage(registerMessage, data.detail || 'Registration failed', false);
        }
    } catch (error) {
        showMessage(registerMessage, 'Network error. Please try again.', false);
        console.error('Registration error:', error);
    }
}

// Handle login
async function handleLogin(e) {
    e.preventDefault();
    
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password }),
        });
        
        const data = await response.json();
        
        if (response.ok) {
            authToken = data.access_token;
            localStorage.setItem('authToken', authToken);
            showMessage(loginMessage, 'Login successful!', true);
            loginForm.reset();
            setTimeout(() => {
                loadProfile();
            }, 1000);
        } else {
            showMessage(loginMessage, data.detail || 'Login failed', false);
        }
    } catch (error) {
        showMessage(loginMessage, 'Network error. Please try again.', false);
        console.error('Login error:', error);
    }
}

// Load user profile
async function loadProfile() {
    if (!authToken) {
        showAuthForms();
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/auth/profile`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${authToken}`,
            },
        });
        
        const data = await response.json();
        
        if (response.ok) {
            document.getElementById('profile-id').textContent = data.id;
            document.getElementById('profile-username').textContent = data.username;
            document.getElementById('profile-created').textContent = new Date(data.created_at).toLocaleString();
            showProfile();
        } else {
            // Token invalid or expired
            localStorage.removeItem('authToken');
            authToken = null;
            showAuthForms();
            showMessage(loginMessage, 'Session expired. Please log in again.', false);
        }
    } catch (error) {
        showMessage(profileMessage, 'Failed to load profile.', false);
        console.error('Profile error:', error);
    }
}

// Handle logout
async function handleLogout() {
    if (!authToken) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/auth/logout`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`,
            },
        });
        
        if (response.ok) {
            localStorage.removeItem('authToken');
            authToken = null;
            showAuthForms();
            showMessage(loginMessage, 'Logged out successfully!', true);
        } else {
            showMessage(profileMessage, 'Logout failed', false);
        }
    } catch (error) {
        // Even if network fails, clear local storage
        localStorage.removeItem('authToken');
        authToken = null;
        showAuthForms();
        showMessage(loginMessage, 'Logged out (network error occurred)', true);
        console.error('Logout error:', error);
    }
}

