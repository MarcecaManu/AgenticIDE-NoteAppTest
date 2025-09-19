const API_URL = 'http://localhost:8000/api/auth';

// Helper function to show messages
function showMessage(elementId, message, isError = false) {
    const element = document.getElementById(elementId);
    element.textContent = message;
    element.className = isError ? 'error' : 'success';
}

// Helper function for making API requests
async function apiRequest(endpoint, method, body = null) {
    const headers = {
        'Content-Type': 'application/json'
    };
    
    // Add authorization header if token exists
    const token = localStorage.getItem('token');
    if (token && endpoint !== '/login') {
        headers['Authorization'] = `Bearer ${token}`;
    }

    // For login endpoint, we need to send form data
    if (endpoint === '/login') {
        const formData = new URLSearchParams();
        formData.append('username', body.username);
        formData.append('password', body.password);
        
        return fetch(`${API_URL}${endpoint}`, {
            method,
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: formData
        });
    }

    const options = {
        method,
        headers,
        body: body ? JSON.stringify(body) : null
    };

    return fetch(`${API_URL}${endpoint}`, options);
}

// Register function
async function register() {
    const username = document.getElementById('register-username').value;
    const password = document.getElementById('register-password').value;

    try {
        const response = await apiRequest('/register', 'POST', { username, password });
        const data = await response.json();

        if (response.ok) {
            showMessage('register-message', 'Registration successful! Please log in.');
            document.getElementById('register-username').value = '';
            document.getElementById('register-password').value = '';
        } else {
            showMessage('register-message', data.detail || 'Registration failed', true);
        }
    } catch (error) {
        showMessage('register-message', 'An error occurred during registration', true);
    }
}

// Login function
async function login() {
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;

    try {
        const response = await apiRequest('/login', 'POST', { username, password });
        const data = await response.json();

        if (response.ok) {
            localStorage.setItem('token', data.access_token);
            showMessage('login-message', 'Login successful!');
            document.getElementById('login-username').value = '';
            document.getElementById('login-password').value = '';
            await loadProfile();
        } else {
            showMessage('login-message', data.detail || 'Login failed', true);
        }
    } catch (error) {
        showMessage('login-message', 'An error occurred during login', true);
    }
}

// Logout function
async function logout() {
    try {
        const response = await apiRequest('/logout', 'POST');
        const data = await response.json();

        if (response.ok) {
            localStorage.removeItem('token');
            document.getElementById('auth-forms').style.display = 'block';
            document.getElementById('profile').style.display = 'none';
        }
    } catch (error) {
        console.error('Logout failed:', error);
    }
}

// Load profile function
async function loadProfile() {
    try {
        const response = await apiRequest('/profile', 'GET');
        const data = await response.json();

        if (response.ok) {
            document.getElementById('profile-username').textContent = data.username;
            document.getElementById('auth-forms').style.display = 'none';
            document.getElementById('profile').style.display = 'block';
        } else {
            localStorage.removeItem('token');
        }
    } catch (error) {
        console.error('Failed to load profile:', error);
        localStorage.removeItem('token');
    }
}

// Check if user is logged in on page load
window.addEventListener('load', () => {
    if (localStorage.getItem('token')) {
        loadProfile();
    }
});
