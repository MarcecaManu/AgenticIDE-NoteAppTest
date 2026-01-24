// Configuration
const API_BASE_URL = 'http://localhost:8000';

// State management
let authToken = localStorage.getItem('authToken');

// DOM Elements
const loginView = document.getElementById('login-view');
const registerView = document.getElementById('register-view');
const profileView = document.getElementById('profile-view');
const messageDiv = document.getElementById('message');

const loginForm = document.getElementById('login-form');
const registerForm = document.getElementById('register-form');
const logoutBtn = document.getElementById('logout-btn');

const showRegisterLink = document.getElementById('show-register');
const showLoginLink = document.getElementById('show-login');

// Utility functions
function showMessage(text, type = 'success') {
    messageDiv.textContent = text;
    messageDiv.className = `message ${type}`;
    messageDiv.style.display = 'block';
    
    setTimeout(() => {
        messageDiv.style.display = 'none';
    }, 5000);
}

function hideAllViews() {
    loginView.classList.add('hidden');
    registerView.classList.add('hidden');
    profileView.classList.add('hidden');
}

function showLoginView() {
    hideAllViews();
    loginView.classList.remove('hidden');
    messageDiv.style.display = 'none';
}

function showRegisterView() {
    hideAllViews();
    registerView.classList.remove('hidden');
    messageDiv.style.display = 'none';
}

function showProfileView() {
    hideAllViews();
    profileView.classList.remove('hidden');
}

// API functions
async function register(username, password) {
    const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.detail || 'Registration failed');
    }

    return data;
}

async function login(username, password) {
    const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.detail || 'Login failed');
    }

    return data;
}

async function getProfile() {
    const response = await fetch(`${API_BASE_URL}/api/auth/profile`, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${authToken}`,
        },
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.detail || 'Failed to fetch profile');
    }

    return data;
}

async function logout() {
    const response = await fetch(`${API_BASE_URL}/api/auth/logout`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${authToken}`,
        },
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.detail || 'Logout failed');
    }

    return data;
}

// Event handlers
loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;

    try {
        const data = await login(username, password);
        authToken = data.access_token;
        localStorage.setItem('authToken', authToken);
        
        showMessage('Login successful!', 'success');
        loginForm.reset();
        
        // Load profile
        await loadProfile();
    } catch (error) {
        showMessage(error.message, 'error');
    }
});

registerForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const username = document.getElementById('register-username').value;
    const password = document.getElementById('register-password').value;

    try {
        await register(username, password);
        showMessage('Registration successful! Please login.', 'success');
        registerForm.reset();
        
        // Switch to login view after successful registration
        setTimeout(() => {
            showLoginView();
        }, 2000);
    } catch (error) {
        showMessage(error.message, 'error');
    }
});

logoutBtn.addEventListener('click', async () => {
    try {
        await logout();
        authToken = null;
        localStorage.removeItem('authToken');
        
        showMessage('Logged out successfully!', 'success');
        showLoginView();
    } catch (error) {
        // Even if logout fails on server, clear local token
        authToken = null;
        localStorage.removeItem('authToken');
        showMessage('Logged out', 'success');
        showLoginView();
    }
});

showRegisterLink.addEventListener('click', (e) => {
    e.preventDefault();
    showRegisterView();
});

showLoginLink.addEventListener('click', (e) => {
    e.preventDefault();
    showLoginView();
});

// Load profile function
async function loadProfile() {
    try {
        const profile = await getProfile();
        
        document.getElementById('profile-username').textContent = profile.username;
        
        // Format the date
        const date = new Date(profile.created_at);
        document.getElementById('profile-created').textContent = date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
        
        showProfileView();
    } catch (error) {
        // If profile fetch fails, token might be invalid
        authToken = null;
        localStorage.removeItem('authToken');
        showMessage('Session expired. Please login again.', 'error');
        showLoginView();
    }
}

// Initialize app
function init() {
    if (authToken) {
        // If token exists, try to load profile
        loadProfile();
    } else {
        // Show login view
        showLoginView();
    }
}

// Start the app
init();

