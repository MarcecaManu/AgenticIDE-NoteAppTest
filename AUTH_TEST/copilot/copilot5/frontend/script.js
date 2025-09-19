const API_URL = 'http://localhost:8000/api/auth';
let token = localStorage.getItem('token');

function showProfile() {
    document.querySelector('.auth-forms').style.display = 'none';
    document.querySelector('.profile').style.display = 'block';
}

function showAuthForms() {
    document.querySelector('.auth-forms').style.display = 'block';
    document.querySelector('.profile').style.display = 'none';
}

async function register() {
    const username = document.getElementById('register-username').value;
    const password = document.getElementById('register-password').value;

    try {
        const response = await fetch(`${API_URL}/register`, {
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

        alert('Registration successful! Please log in.');
        document.getElementById('register-username').value = '';
        document.getElementById('register-password').value = '';
    } catch (error) {
        alert(error.message);
    }
}

async function login() {
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;

    try {
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);

        const response = await fetch(`${API_URL}/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: formData,
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Login failed');
        }

        const data = await response.json();
        token = data.access_token;
        localStorage.setItem('token', token);

        document.getElementById('login-username').value = '';
        document.getElementById('login-password').value = '';
        
        await loadProfile();
    } catch (error) {
        alert(error.message);
    }
}

async function logout() {
    try {
        const response = await fetch(`${API_URL}/logout`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
            },
        });

        if (!response.ok) {
            throw new Error('Logout failed');
        }

        token = null;
        localStorage.removeItem('token');
        showAuthForms();
    } catch (error) {
        alert(error.message);
    }
}

async function loadProfile() {
    try {
        const response = await fetch(`${API_URL}/profile`, {
            headers: {
                'Authorization': `Bearer ${token}`,
            },
        });

        if (!response.ok) {
            if (response.status === 401) {
                token = null;
                localStorage.removeItem('token');
                showAuthForms();
                return;
            }
            throw new Error('Failed to load profile');
        }

        const user = await response.json();
        document.getElementById('profile-username').textContent = user.username;
        showProfile();
    } catch (error) {
        alert(error.message);
    }
}

// Check if user is already logged in
if (token) {
    loadProfile();
} else {
    showAuthForms();
}
