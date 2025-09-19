const API_BASE_URL = 'http://localhost:8000/api/auth';

// Helper function to show/hide forms and profile section
function updateUIState(isLoggedIn) {
    document.getElementById('auth-forms').style.display = isLoggedIn ? 'none' : 'block';
    document.getElementById('profile-section').style.display = isLoggedIn ? 'block' : 'none';
}

// Helper function to make API requests
async function apiRequest(endpoint, method = 'GET', data = null) {
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json',
        },
    };

    if (data) {
        options.body = JSON.stringify(data);
    }

    // Add authorization header if token exists
    const token = localStorage.getItem('token');
    if (token) {
        options.headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
    const result = await response.json();

    if (!response.ok) {
        throw new Error(result.detail || 'An error occurred');
    }

    return result;
}

// Register function
async function register() {
    const username = document.getElementById('register-username').value;
    const password = document.getElementById('register-password').value;
    const messageElement = document.getElementById('register-message');

    try {
        await apiRequest('/register', 'POST', { username, password });
        messageElement.className = 'success';
        messageElement.textContent = 'Registration successful! Please log in.';
        
        // Clear form
        document.getElementById('register-username').value = '';
        document.getElementById('register-password').value = '';
    } catch (error) {
        messageElement.className = 'error';
        messageElement.textContent = error.message;
    }
}

// Login function
async function login() {
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;
    const messageElement = document.getElementById('login-message');

    try {
        // Format data as form data for OAuth2 compatibility
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);

        const response = await fetch(`${API_BASE_URL}/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: formData
        });

        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Login failed');
        }

        // Store token and update UI
        localStorage.setItem('token', data.access_token);
        messageElement.className = 'success';
        messageElement.textContent = 'Login successful!';

        // Clear form
        document.getElementById('login-username').value = '';
        document.getElementById('login-password').value = '';

        // Load profile
        await loadProfile();
    } catch (error) {
        messageElement.className = 'error';
        messageElement.textContent = error.message;
    }
}

// Logout function
async function logout() {
    const messageElement = document.getElementById('logout-message');

    try {
        await apiRequest('/logout', 'POST');
        localStorage.removeItem('token');
        messageElement.className = 'success';
        messageElement.textContent = 'Logged out successfully!';
        updateUIState(false);
    } catch (error) {
        messageElement.className = 'error';
        messageElement.textContent = error.message;
    }
}

// Load profile function
async function loadProfile() {
    try {
        const profile = await apiRequest('/profile');
        document.getElementById('profile-username').textContent = profile.username;
        updateUIState(true);
    } catch (error) {
        // If there's an error loading the profile, clear the token and show login form
        localStorage.removeItem('token');
        updateUIState(false);
    }
}

// Check if user is logged in on page load
window.addEventListener('load', () => {
    if (localStorage.getItem('token')) {
        loadProfile();
    } else {
        updateUIState(false);
    }
});
