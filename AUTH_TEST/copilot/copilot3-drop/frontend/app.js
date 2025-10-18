// API endpoints
const API_BASE_URL = 'http://localhost:8000/api/auth';
const API_ENDPOINTS = {
    register: `${API_BASE_URL}/register`,
    login: `${API_BASE_URL}/login`,
    logout: `${API_BASE_URL}/logout`,
    profile: `${API_BASE_URL}/profile`,
};

// UI elements
const authSection = document.getElementById('auth-section');
const profileSection = document.getElementById('profile-section');
const profileInfo = document.getElementById('profile-info');
const registerError = document.getElementById('register-error');
const loginError = document.getElementById('login-error');

// Check authentication status on page load
document.addEventListener('DOMContentLoaded', () => {
    if (isAuthenticated()) {
        fetchProfile();
    } else {
        showAuthForms();
    }
});

// Helper functions
function isAuthenticated() {
    return !!localStorage.getItem('token');
}

function showAuthForms() {
    authSection.style.display = 'block';
    profileSection.style.display = 'none';
}

function showProfile() {
    authSection.style.display = 'none';
    profileSection.style.display = 'block';
}

async function register() {
    const username = document.getElementById('register-username').value;
    const password = document.getElementById('register-password').value;

    try {
        const response = await fetch(API_ENDPOINTS.register, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password }),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Registration failed');
        }

        await response.json();
        registerError.textContent = '';
        // Auto-login after successful registration
        await login(username, password);
    } catch (error) {
        registerError.textContent = error.message;
    }
}

async function login(username = null, password = null) {
    // If credentials are not provided, get them from the form
    username = username || document.getElementById('login-username').value;
    password = password || document.getElementById('login-password').value;

    try {
        const formData = new FormData();
        formData.append('username', username);
        formData.append('password', password);

        const response = await fetch(API_ENDPOINTS.login, {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Login failed');
        }

        const data = await response.json();
        localStorage.setItem('token', data.access_token);
        loginError.textContent = '';
        await fetchProfile();
    } catch (error) {
        loginError.textContent = error.message;
    }
}

async function logout() {
    try {
        await fetch(API_ENDPOINTS.logout, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`,
            },
        });
    } finally {
        localStorage.removeItem('token');
        showAuthForms();
        profileInfo.textContent = '';
    }
}

async function fetchProfile() {
    try {
        const response = await fetch(API_ENDPOINTS.profile, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`,
            },
        });

        if (!response.ok) {
            throw new Error('Failed to fetch profile');
        }

        const profile = await response.json();
        profileInfo.textContent = `Welcome, ${profile.username}!`;
        showProfile();
    } catch (error) {
        localStorage.removeItem('token');
        showAuthForms();
    }
}
