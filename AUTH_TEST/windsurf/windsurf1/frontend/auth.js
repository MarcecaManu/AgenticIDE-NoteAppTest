// API Base URL
const API_BASE_URL = 'http://localhost:8000';

// DOM Elements
const loginSection = document.getElementById('login-section');
const registerSection = document.getElementById('register-section');
const profileSection = document.getElementById('profile-section');
const userInfo = document.getElementById('user-info');
const messageContainer = document.getElementById('message-container');

// Forms
const loginForm = document.getElementById('login-form');
const registerForm = document.getElementById('register-form');

// Buttons and links
const showRegisterLink = document.getElementById('show-register');
const showLoginLink = document.getElementById('show-login');
const logoutBtn = document.getElementById('logout-btn');
const viewProfileBtn = document.getElementById('view-profile-btn');

// Profile elements
const usernameDisplay = document.getElementById('username-display');
const profileUsername = document.getElementById('profile-username');
const profileCreated = document.getElementById('profile-created');

// Token management
let authToken = localStorage.getItem('authToken');
let currentUser = localStorage.getItem('currentUser');

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
});

function initializeApp() {
    if (authToken && currentUser) {
        showProfileSection();
        loadUserProfile();
    } else {
        showLoginSection();
    }
}

function setupEventListeners() {
    // Form submissions
    loginForm.addEventListener('submit', handleLogin);
    registerForm.addEventListener('submit', handleRegister);
    
    // Navigation links
    showRegisterLink.addEventListener('click', (e) => {
        e.preventDefault();
        showRegisterSection();
    });
    
    showLoginLink.addEventListener('click', (e) => {
        e.preventDefault();
        showLoginSection();
    });
    
    // Buttons
    logoutBtn.addEventListener('click', handleLogout);
    viewProfileBtn.addEventListener('click', loadUserProfile);
}

// UI Navigation Functions
function showLoginSection() {
    loginSection.style.display = 'block';
    registerSection.style.display = 'none';
    profileSection.style.display = 'none';
    userInfo.style.display = 'none';
    clearForms();
}

function showRegisterSection() {
    loginSection.style.display = 'none';
    registerSection.style.display = 'block';
    profileSection.style.display = 'none';
    userInfo.style.display = 'none';
    clearForms();
}

function showProfileSection() {
    loginSection.style.display = 'none';
    registerSection.style.display = 'none';
    profileSection.style.display = 'block';
    userInfo.style.display = 'flex';
    usernameDisplay.textContent = `Welcome, ${currentUser}!`;
    clearForms();
}

function clearForms() {
    loginForm.reset();
    registerForm.reset();
}

// Authentication Functions
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
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            authToken = data.access_token;
            currentUser = username;
            
            localStorage.setItem('authToken', authToken);
            localStorage.setItem('currentUser', currentUser);
            
            showMessage('Login successful!', 'success');
            showProfileSection();
            loadUserProfile();
        } else {
            showMessage(data.detail || 'Login failed', 'error');
        }
    } catch (error) {
        showMessage('Network error. Please try again.', 'error');
        console.error('Login error:', error);
    }
}

async function handleRegister(e) {
    e.preventDefault();
    
    const username = document.getElementById('register-username').value;
    const password = document.getElementById('register-password').value;
    const confirmPassword = document.getElementById('confirm-password').value;
    
    // Validate password confirmation
    if (password !== confirmPassword) {
        showMessage('Passwords do not match', 'error');
        return;
    }
    
    // Basic password validation
    if (password.length < 6) {
        showMessage('Password must be at least 6 characters long', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage('Registration successful! Please log in.', 'success');
            showLoginSection();
            // Pre-fill login form
            document.getElementById('login-username').value = username;
        } else {
            showMessage(data.detail || 'Registration failed', 'error');
        }
    } catch (error) {
        showMessage('Network error. Please try again.', 'error');
        console.error('Registration error:', error);
    }
}

async function handleLogout() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/auth/logout`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json',
            }
        });
        
        if (response.ok) {
            showMessage('Logged out successfully', 'success');
        } else {
            showMessage('Logout completed', 'info');
        }
    } catch (error) {
        showMessage('Logout completed', 'info');
        console.error('Logout error:', error);
    } finally {
        // Clear local storage and redirect to login
        localStorage.removeItem('authToken');
        localStorage.removeItem('currentUser');
        authToken = null;
        currentUser = null;
        showLoginSection();
    }
}

async function loadUserProfile() {
    if (!authToken) {
        showMessage('Please log in first', 'error');
        showLoginSection();
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/auth/profile`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json',
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            profileUsername.textContent = data.username;
            profileCreated.textContent = new Date(data.created_at).toLocaleDateString();
            showMessage('Profile loaded successfully', 'success');
        } else {
            if (response.status === 401) {
                showMessage('Session expired. Please log in again.', 'error');
                localStorage.removeItem('authToken');
                localStorage.removeItem('currentUser');
                authToken = null;
                currentUser = null;
                showLoginSection();
            } else {
                showMessage(data.detail || 'Failed to load profile', 'error');
            }
        }
    } catch (error) {
        showMessage('Network error. Please try again.', 'error');
        console.error('Profile load error:', error);
    }
}

// Utility Functions
function showMessage(message, type = 'info') {
    const messageElement = document.createElement('div');
    messageElement.className = `message ${type}`;
    messageElement.textContent = message;
    
    messageContainer.appendChild(messageElement);
    
    // Auto-remove message after 5 seconds
    setTimeout(() => {
        if (messageElement.parentNode) {
            messageElement.parentNode.removeChild(messageElement);
        }
    }, 5000);
    
    // Make message clickable to dismiss
    messageElement.addEventListener('click', () => {
        if (messageElement.parentNode) {
            messageElement.parentNode.removeChild(messageElement);
        }
    });
}

// Handle token expiration globally
window.addEventListener('beforeunload', function() {
    // Optional: Clean up any pending requests
});

// Auto-refresh token before expiration (optional enhancement)
function scheduleTokenRefresh() {
    // This could be implemented to refresh tokens automatically
    // For now, we rely on the 30-minute expiration
}
