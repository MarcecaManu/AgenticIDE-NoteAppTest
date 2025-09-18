const API_BASE_URL = 'http://localhost:8000/api/auth';

class AuthApp {
    constructor() {
        this.token = localStorage.getItem('authToken');
        this.init();
    }

    init() {
        this.bindEvents();
        this.checkAuthStatus();
    }

    bindEvents() {
        // Form submissions
        document.getElementById('login-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleLogin();
        });

        document.getElementById('register-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleRegister();
        });

        // Navigation links
        document.getElementById('show-register').addEventListener('click', (e) => {
            e.preventDefault();
            this.showRegisterForm();
        });

        document.getElementById('show-login').addEventListener('click', (e) => {
            e.preventDefault();
            this.showLoginForm();
        });

        // Logout button
        document.getElementById('logout-btn').addEventListener('click', () => {
            this.handleLogout();
        });
    }

    async handleLogin() {
        const username = document.getElementById('login-username').value.trim();
        const password = document.getElementById('login-password').value;

        if (!username || !password) {
            this.showMessage('Please fill in all fields', 'error');
            return;
        }

        try {
            const response = await fetch(`${API_BASE_URL}/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password }),
            });

            const data = await response.json();

            if (response.ok) {
                this.token = data.access_token;
                localStorage.setItem('authToken', this.token);
                this.showMessage('Login successful!', 'success');
                await this.loadProfile();
            } else {
                this.showMessage(data.detail || 'Login failed', 'error');
            }
        } catch (error) {
            this.showMessage('Network error. Please try again.', 'error');
            console.error('Login error:', error);
        }
    }

    async handleRegister() {
        const username = document.getElementById('register-username').value.trim();
        const password = document.getElementById('register-password').value;

        if (!username || !password) {
            this.showMessage('Please fill in all fields', 'error');
            return;
        }

        if (username.length < 3) {
            this.showMessage('Username must be at least 3 characters long', 'error');
            return;
        }

        if (password.length < 6) {
            this.showMessage('Password must be at least 6 characters long', 'error');
            return;
        }

        try {
            const response = await fetch(`${API_BASE_URL}/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password }),
            });

            const data = await response.json();

            if (response.ok) {
                this.showMessage('Registration successful! Please login.', 'success');
                this.showLoginForm();
                // Clear the register form
                document.getElementById('register-form').reset();
            } else {
                this.showMessage(data.detail || 'Registration failed', 'error');
            }
        } catch (error) {
            this.showMessage('Network error. Please try again.', 'error');
            console.error('Registration error:', error);
        }
    }

    async handleLogout() {
        if (!this.token) {
            this.showLoginForm();
            return;
        }

        try {
            const response = await fetch(`${API_BASE_URL}/logout`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                },
            });

            const data = await response.json();

            if (response.ok) {
                this.showMessage('Logged out successfully!', 'success');
            } else {
                this.showMessage(data.detail || 'Logout failed', 'error');
            }
        } catch (error) {
            this.showMessage('Network error during logout', 'error');
            console.error('Logout error:', error);
        } finally {
            // Clear token and show login form regardless of API response
            this.token = null;
            localStorage.removeItem('authToken');
            this.showLoginForm();
        }
    }

    async loadProfile() {
        if (!this.token) {
            this.showLoginForm();
            return;
        }

        try {
            const response = await fetch(`${API_BASE_URL}/profile`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                },
            });

            const data = await response.json();

            if (response.ok) {
                this.displayProfile(data);
            } else {
                this.showMessage(data.detail || 'Failed to load profile', 'error');
                this.token = null;
                localStorage.removeItem('authToken');
                this.showLoginForm();
            }
        } catch (error) {
            this.showMessage('Network error. Please try again.', 'error');
            console.error('Profile load error:', error);
            this.showLoginForm();
        }
    }

    displayProfile(profileData) {
        document.getElementById('user-id').textContent = profileData.id;
        document.getElementById('user-username').textContent = profileData.username;
        document.getElementById('user-created').textContent = new Date(profileData.created_at).toLocaleString();
        
        this.showProfileSection();
    }

    showLoginForm() {
        document.getElementById('login-section').style.display = 'block';
        document.getElementById('register-section').style.display = 'none';
        document.getElementById('profile-section').style.display = 'none';
        document.getElementById('login-form').reset();
    }

    showRegisterForm() {
        document.getElementById('login-section').style.display = 'none';
        document.getElementById('register-section').style.display = 'block';
        document.getElementById('profile-section').style.display = 'none';
        document.getElementById('register-form').reset();
    }

    showProfileSection() {
        document.getElementById('login-section').style.display = 'none';
        document.getElementById('register-section').style.display = 'none';
        document.getElementById('profile-section').style.display = 'block';
    }

    showMessage(message, type) {
        const messageElement = document.getElementById('message');
        messageElement.textContent = message;
        messageElement.className = `message ${type}`;
        
        // Clear message after 5 seconds
        setTimeout(() => {
            messageElement.textContent = '';
            messageElement.className = 'message';
        }, 5000);
    }

    checkAuthStatus() {
        if (this.token) {
            this.loadProfile();
        } else {
            this.showLoginForm();
        }
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new AuthApp();
});
