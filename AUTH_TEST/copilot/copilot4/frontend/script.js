const API_BASE_URL = 'http://127.0.0.1:8000/api/auth';

// Helper function to show messages
function showMessage(elementId, message, isError = false) {
    const element = document.getElementById(elementId);
    element.textContent = message;
    element.className = isError ? 'error' : 'success';
}

// Helper function to make API calls
async function apiCall(endpoint, method = 'GET', data = null) {
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
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

// Register Form Handler
document.getElementById('register-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('reg-username').value;
    const password = document.getElementById('reg-password').value;

    try {
        await apiCall('/register', 'POST', { username, password });
        showMessage('register-message', 'Registration successful! Please login.');
        e.target.reset();
    } catch (error) {
        showMessage('register-message', error.message, true);
    }
});

// Login Form Handler
document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;

    try {
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);

        const response = await fetch(`${API_BASE_URL}/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: formData
        });

        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.detail || 'Login failed');
        }

        localStorage.setItem('token', data.access_token);
        showMessage('login-message', 'Login successful!');
        e.target.reset();
        updateUI(true);
        loadProfile();
    } catch (error) {
        showMessage('login-message', error.message, true);
    }
});

// Logout Button Handler
document.getElementById('logout-btn').addEventListener('click', async () => {
    try {
        await apiCall('/logout', 'POST');
        localStorage.removeItem('token');
        updateUI(false);
    } catch (error) {
        console.error('Logout error:', error);
    }
});

// Load Profile Data
async function loadProfile() {
    try {
        const profile = await apiCall('/profile');
        document.getElementById('profile-info').innerHTML = `
            <p>Username: ${profile.username}</p>
            <p>ID: ${profile.id}</p>
        `;
    } catch (error) {
        showMessage('profile-info', 'Error loading profile: ' + error.message, true);
    }
}

// Update UI based on auth state
function updateUI(isLoggedIn) {
    document.getElementById('auth-container').style.display = isLoggedIn ? 'none' : 'block';
    document.getElementById('profile-container').style.display = isLoggedIn ? 'block' : 'none';
    if (isLoggedIn) {
        loadProfile();
    }
}

// Check auth state on page load
const token = localStorage.getItem('token');
updateUI(!!token);
