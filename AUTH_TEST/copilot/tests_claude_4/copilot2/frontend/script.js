// API Configuration
const API_BASE_URL = window.location.origin;
const API_AUTH_URL = `${API_BASE_URL}/api/auth`;

// Token management
class TokenManager {
    static getToken() {
        return localStorage.getItem('access_token');
    }
    
    static setToken(token) {
        localStorage.setItem('access_token', token);
    }
    
    static removeToken() {
        localStorage.removeItem('access_token');
    }
    
    static hasToken() {
        return !!this.getToken();
    }
}

// API helper functions
async function apiRequest(url, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        },
    };
    
    // Add authorization header if token exists
    const token = TokenManager.getToken();
    if (token) {
        defaultOptions.headers['Authorization'] = `Bearer ${token}`;
    }
    
    const config = {
        ...defaultOptions,
        ...options,
        headers: {
            ...defaultOptions.headers,
            ...options.headers,
        },
    };
    
    try {
        const response = await fetch(url, config);
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || `HTTP error! status: ${response.status}`);
        }
        
        return data;
    } catch (error) {
        console.error('API request failed:', error);
        throw error;
    }
}

// UI helper functions
function showError(elementId, message) {
    const errorElement = document.getElementById(elementId);
    errorElement.textContent = message;
    errorElement.style.display = 'block';
    
    // Hide error after 5 seconds
    setTimeout(() => {
        errorElement.style.display = 'none';
    }, 5000);
}

function showSuccess(elementId, message) {
    const successElement = document.getElementById(elementId);
    successElement.textContent = message;
    successElement.style.display = 'block';
    
    // Hide success message after 3 seconds
    setTimeout(() => {
        successElement.style.display = 'none';
    }, 3000);
}

function hideMessage(elementId) {
    const element = document.getElementById(elementId);
    element.style.display = 'none';
}

function setLoading(buttonId, isLoading) {
    const button = document.getElementById(buttonId);
    const btnText = button.querySelector('.btn-text');
    
    if (isLoading) {
        button.disabled = true;
        btnText.innerHTML = '<span class="loading"></span> Loading...';
    } else {
        button.disabled = false;
        btnText.textContent = button.id.includes('login') ? 'Sign In' : 
                              button.id.includes('register') ? 'Sign Up' : 'Logout';
    }
}

function showPage(pageName) {
    // Hide all pages
    const pages = document.querySelectorAll('.page');
    pages.forEach(page => page.classList.remove('active'));
    
    // Show selected page
    const targetPage = document.getElementById(`${pageName}-page`);
    if (targetPage) {
        targetPage.classList.add('active');
    }
    
    // Update header
    const headerTitle = document.getElementById('header-title');
    const headerSubtitle = document.getElementById('header-subtitle');
    
    switch (pageName) {
        case 'login':
            headerTitle.textContent = 'Welcome Back';
            headerSubtitle.textContent = 'Please sign in to continue';
            break;
        case 'register':
            headerTitle.textContent = 'Create Account';
            headerSubtitle.textContent = 'Sign up to get started';
            break;
        case 'profile':
            headerTitle.textContent = 'Profile';
            headerSubtitle.textContent = 'Manage your account';
            break;
    }
    
    // Clear any error messages
    const errorElements = document.querySelectorAll('.error, .success');
    errorElements.forEach(el => el.style.display = 'none');
    
    // Clear form data
    const forms = document.querySelectorAll('form');
    forms.forEach(form => form.reset());
}

// Authentication functions
async function register(username, password) {
    const response = await apiRequest(`${API_AUTH_URL}/register`, {
        method: 'POST',
        body: JSON.stringify({ username, password }),
    });
    return response;
}

async function login(username, password) {
    const response = await apiRequest(`${API_AUTH_URL}/login`, {
        method: 'POST',
        body: JSON.stringify({ username, password }),
    });
    return response;
}

async function logout() {
    try {
        await apiRequest(`${API_AUTH_URL}/logout`, {
            method: 'POST',
        });
    } catch (error) {
        console.error('Logout error:', error);
    } finally {
        // Always remove token and redirect to login
        TokenManager.removeToken();
        showPage('login');
    }
}

async function getProfile() {
    const response = await apiRequest(`${API_AUTH_URL}/profile`);
    return response;
}

// Form handlers
async function handleLogin(event) {
    event.preventDefault();
    
    const username = document.getElementById('login-username').value.trim();
    const password = document.getElementById('login-password').value;
    
    if (!username || !password) {
        showError('login-error', 'Please fill in all fields');
        return;
    }
    
    setLoading('login-btn', true);
    hideMessage('login-error');
    
    try {
        const response = await login(username, password);
        TokenManager.setToken(response.access_token);
        await loadProfile();
        showPage('profile');
    } catch (error) {
        showError('login-error', error.message);
    } finally {
        setLoading('login-btn', false);
    }
}

async function handleRegister(event) {
    event.preventDefault();
    
    const username = document.getElementById('register-username').value.trim();
    const password = document.getElementById('register-password').value;
    const confirmPassword = document.getElementById('register-confirm-password').value;
    
    if (!username || !password || !confirmPassword) {
        showError('register-error', 'Please fill in all fields');
        return;
    }
    
    if (password !== confirmPassword) {
        showError('register-error', 'Passwords do not match');
        return;
    }
    
    if (username.length < 3) {
        showError('register-error', 'Username must be at least 3 characters long');
        return;
    }
    
    if (password.length < 6) {
        showError('register-error', 'Password must be at least 6 characters long');
        return;
    }
    
    setLoading('register-btn', true);
    hideMessage('register-error');
    hideMessage('register-success');
    
    try {
        await register(username, password);
        showSuccess('register-success', 'Account created successfully! You can now sign in.');
        
        // Clear form and switch to login after 2 seconds
        setTimeout(() => {
            showPage('login');
            document.getElementById('login-username').value = username;
        }, 2000);
        
    } catch (error) {
        showError('register-error', error.message);
    } finally {
        setLoading('register-btn', false);
    }
}

async function loadProfile() {
    try {
        const profile = await getProfile();
        
        document.getElementById('profile-id').textContent = profile.id;
        document.getElementById('profile-username').textContent = profile.username;
        
        // Format date
        const createdDate = new Date(profile.created_at);
        document.getElementById('profile-created').textContent = createdDate.toLocaleDateString();
        
    } catch (error) {
        showError('profile-error', 'Failed to load profile information');
        console.error('Profile loading error:', error);
    }
}

// Initialize app
function initializeApp() {
    // Check if user is already logged in
    if (TokenManager.hasToken()) {
        loadProfile().then(() => {
            showPage('profile');
        }).catch(() => {
            // Token might be invalid, remove it and show login
            TokenManager.removeToken();
            showPage('login');
        });
    } else {
        showPage('login');
    }
    
    // Add form event listeners
    document.getElementById('login-form').addEventListener('submit', handleLogin);
    document.getElementById('register-form').addEventListener('submit', handleRegister);
    
    // Add keyboard shortcuts
    document.addEventListener('keydown', function(event) {
        // ESC key to go back to login
        if (event.key === 'Escape') {
            const currentPage = document.querySelector('.page.active').id;
            if (currentPage === 'register-page') {
                showPage('login');
            }
        }
    });
}

// Start the app when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeApp);