// Configuration
const API_BASE_URL = 'http://localhost:8000';
const TOKEN_STORAGE_KEY = 'auth_token';

// DOM Elements
const loginSection = document.getElementById('login-section');
const registerSection = document.getElementById('register-section');
const profileSection = document.getElementById('profile-section');

// Forms
const loginForm = document.getElementById('login-form');
const registerForm = document.getElementById('register-form');
const logoutBtn = document.getElementById('logout-btn');

// Message elements
const loginMessage = document.getElementById('login-message');
const registerMessage = document.getElementById('register-message');
const profileMessage = document.getElementById('profile-message');

// Loading elements
const loginLoading = document.getElementById('login-loading');
const registerLoading = document.getElementById('register-loading');
const profileLoading = document.getElementById('profile-loading');

// Profile elements
const profileInfo = document.getElementById('profile-info');
const profileUsername = document.getElementById('profile-username');
const profileCreated = document.getElementById('profile-created');

// Utility Functions
function showMessage(messageElement, text, type = 'info') {
    messageElement.textContent = text;
    messageElement.className = `message ${type}`;
    messageElement.style.display = 'block';
    
    // Auto-hide success messages after 3 seconds
    if (type === 'success') {
        setTimeout(() => {
            messageElement.style.display = 'none';
        }, 3000);
    }
}

function hideMessage(messageElement) {
    messageElement.style.display = 'none';
}

function showLoading(loadingElement) {
    loadingElement.style.display = 'block';
}

function hideLoading(loadingElement) {
    loadingElement.style.display = 'none';
}

function showSection(sectionName) {
    // Hide all sections
    document.querySelectorAll('.section').forEach(section => {
        section.classList.remove('active');
    });
    
    // Show the requested section
    const section = document.getElementById(`${sectionName}-section`);
    if (section) {
        section.classList.add('active');
    }
    
    // Clear messages when switching sections
    hideMessage(loginMessage);
    hideMessage(registerMessage);
    hideMessage(profileMessage);
}

// Token Management
function getToken() {
    return localStorage.getItem(TOKEN_STORAGE_KEY);
}

function setToken(token) {
    localStorage.setItem(TOKEN_STORAGE_KEY, token);
}

function removeToken() {
    localStorage.removeItem(TOKEN_STORAGE_KEY);
}

function isLoggedIn() {
    return !!getToken();
}

// API Functions
async function apiRequest(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const config = {
        headers: {
            'Content-Type': 'application/json',
            ...options.headers
        },
        ...options
    };
    
    // Add authorization header if token exists
    const token = getToken();
    if (token) {
        config.headers['Authorization'] = `Bearer ${token}`;
    }
    
    try {
        const response = await fetch(url, config);
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || `HTTP error! status: ${response.status}`);
        }
        
        return data;
    } catch (error) {
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
            throw new Error('Cannot connect to server. Please make sure the backend is running.');
        }
        throw error;
    }
}

// Authentication Functions
async function register(username, password) {
    const data = await apiRequest('/api/auth/register', {
        method: 'POST',
        body: JSON.stringify({ username, password })
    });
    return data;
}

async function login(username, password) {
    const data = await apiRequest('/api/auth/login', {
        method: 'POST',
        body: JSON.stringify({ username, password })
    });
    return data;
}

async function logout() {
    try {
        await apiRequest('/api/auth/logout', {
            method: 'POST'
        });
    } catch (error) {
        console.warn('Logout API call failed:', error.message);
        // Continue with local logout even if API call fails
    }
    
    removeToken();
    showSection('login');
}

async function getProfile() {
    const data = await apiRequest('/api/auth/profile');
    return data;
}

// Event Handlers
loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = new FormData(loginForm);
    const username = formData.get('username').trim();
    const password = formData.get('password');
    
    if (!username || !password) {
        showMessage(loginMessage, 'Please fill in all fields', 'error');
        return;
    }
    
    hideMessage(loginMessage);
    showLoading(loginLoading);
    
    try {
        const response = await login(username, password);
        setToken(response.access_token);
        
        hideLoading(loginLoading);
        showMessage(loginMessage, 'Login successful!', 'success');
        
        // Switch to profile section and load profile data
        setTimeout(() => {
            showSection('profile');
            loadProfile();
        }, 1000);
        
    } catch (error) {
        hideLoading(loginLoading);
        showMessage(loginMessage, error.message, 'error');
    }
});

registerForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = new FormData(registerForm);
    const username = formData.get('username').trim();
    const password = formData.get('password');
    
    if (!username || !password) {
        showMessage(registerMessage, 'Please fill in all fields', 'error');
        return;
    }
    
    if (password.length < 6) {
        showMessage(registerMessage, 'Password must be at least 6 characters long', 'error');
        return;
    }
    
    hideMessage(registerMessage);
    showLoading(registerLoading);
    
    try {
        await register(username, password);
        
        hideLoading(registerLoading);
        showMessage(registerMessage, 'Account created successfully! Please log in.', 'success');
        
        // Clear form and switch to login after delay
        registerForm.reset();
        setTimeout(() => {
            showSection('login');
        }, 2000);
        
    } catch (error) {
        hideLoading(registerLoading);
        showMessage(registerMessage, error.message, 'error');
    }
});

logoutBtn.addEventListener('click', async () => {
    await logout();
});

// Profile Loading
async function loadProfile() {
    hideMessage(profileMessage);
    showLoading(profileLoading);
    profileInfo.style.display = 'none';
    
    try {
        const profile = await getProfile();
        
        profileUsername.textContent = profile.username;
        
        // Format the created date
        const createdDate = new Date(profile.created_at);
        profileCreated.textContent = createdDate.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
        
        hideLoading(profileLoading);
        profileInfo.style.display = 'block';
        
    } catch (error) {
        hideLoading(profileLoading);
        
        if (error.message.includes('401') || error.message.includes('invalidated')) {
            // Token is invalid or expired
            removeToken();
            showMessage(profileMessage, 'Session expired. Please log in again.', 'error');
            setTimeout(() => {
                showSection('login');
            }, 2000);
        } else {
            showMessage(profileMessage, `Failed to load profile: ${error.message}`, 'error');
        }
    }
}

// Initialize App
function initializeApp() {
    if (isLoggedIn()) {
        showSection('profile');
        loadProfile();
    } else {
        showSection('login');
    }
}

// Global function for template usage
window.showSection = showSection;

// Start the app when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeApp);