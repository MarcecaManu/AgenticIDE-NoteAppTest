class AuthApp {
    constructor() {
        this.apiBase = 'http://localhost:8000/api/auth';
        this.token = localStorage.getItem('authToken');
        this.init();
    }

    init() {
        this.bindEvents();
        this.checkAuthStatus();
    }

    bindEvents() {
        // Form submissions
        document.getElementById('login-form').addEventListener('submit', (e) => this.handleLogin(e));
        document.getElementById('register-form').addEventListener('submit', (e) => this.handleRegister(e));
        
        // Navigation
        document.getElementById('show-register').addEventListener('click', (e) => {
            e.preventDefault();
            this.showRegisterForm();
        });
        
        document.getElementById('show-login').addEventListener('click', (e) => {
            e.preventDefault();
            this.showLoginForm();
        });
        
        // Logout
        document.getElementById('logout-btn').addEventListener('click', () => this.handleLogout());
    }

    async checkAuthStatus() {
        if (this.token) {
            try {
                const profile = await this.getProfile();
                this.showProfile(profile);
            } catch (error) {
                // Token is invalid, remove it
                localStorage.removeItem('authToken');
                this.token = null;
                this.showLoginForm();
            }
        } else {
            this.showLoginForm();
        }
    }

    async handleLogin(e) {
        e.preventDefault();
        
        const username = document.getElementById('login-username').value.trim();
        const password = document.getElementById('login-password').value;
        
        if (!username || !password) {
            this.showMessage('Please fill in all fields', 'error');
            return;
        }

        try {
            const response = await fetch(`${this.apiBase}/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password })
            });

            const data = await response.json();

            if (response.ok) {
                this.token = data.access_token;
                localStorage.setItem('authToken', this.token);
                this.showMessage('Login successful!', 'success');
                
                // Get and show profile
                const profile = await this.getProfile();
                this.showProfile(profile);
            } else {
                this.showMessage(data.detail || 'Login failed', 'error');
            }
        } catch (error) {
            this.showMessage('Network error. Please try again.', 'error');
        }
    }

    async handleRegister(e) {
        e.preventDefault();
        
        const username = document.getElementById('register-username').value.trim();
        const password = document.getElementById('register-password').value;
        const confirmPassword = document.getElementById('register-confirm-password').value;
        
        if (!username || !password || !confirmPassword) {
            this.showMessage('Please fill in all fields', 'error');
            return;
        }

        if (password !== confirmPassword) {
            this.showMessage('Passwords do not match', 'error');
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
            const response = await fetch(`${this.apiBase}/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password })
            });

            const data = await response.json();

            if (response.ok) {
                this.showMessage('Registration successful! Please login.', 'success');
                this.showLoginForm();
                // Clear register form
                document.getElementById('register-form').reset();
            } else {
                this.showMessage(data.detail || 'Registration failed', 'error');
            }
        } catch (error) {
            this.showMessage('Network error. Please try again.', 'error');
        }
    }

    async handleLogout() {
        try {
            await fetch(`${this.apiBase}/logout`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });
        } catch (error) {
            // Even if logout fails on server, we'll clear local token
            console.error('Logout error:', error);
        }

        // Clear local storage and reset UI
        localStorage.removeItem('authToken');
        this.token = null;
        this.showMessage('Logged out successfully', 'success');
        this.showLoginForm();
    }

    async getProfile() {
        const response = await fetch(`${this.apiBase}/profile`, {
            headers: {
                'Authorization': `Bearer ${this.token}`
            }
        });

        if (!response.ok) {
            throw new Error('Failed to get profile');
        }

        return await response.json();
    }

    showLoginForm() {
        document.getElementById('login-section').classList.remove('hidden');
        document.getElementById('register-section').classList.add('hidden');
        document.getElementById('profile-section').classList.add('hidden');
        document.getElementById('user-info').classList.add('hidden');
        
        // Clear forms
        document.getElementById('login-form').reset();
    }

    showRegisterForm() {
        document.getElementById('login-section').classList.add('hidden');
        document.getElementById('register-section').classList.remove('hidden');
        document.getElementById('profile-section').classList.add('hidden');
        document.getElementById('user-info').classList.add('hidden');
        
        // Clear forms
        document.getElementById('register-form').reset();
    }

    showProfile(profile) {
        document.getElementById('login-section').classList.add('hidden');
        document.getElementById('register-section').classList.add('hidden');
        document.getElementById('profile-section').classList.remove('hidden');
        document.getElementById('user-info').classList.remove('hidden');
        
        // Update profile information
        document.getElementById('profile-username').textContent = profile.username;
        document.getElementById('profile-id').textContent = profile.id;
        document.getElementById('username-display').textContent = `Welcome, ${profile.username}!`;
        
        // Clear forms
        document.getElementById('login-form').reset();
        document.getElementById('register-form').reset();
    }

    showMessage(message, type) {
        const messageEl = document.getElementById('message');
        messageEl.textContent = message;
        messageEl.className = `message ${type}`;
        messageEl.classList.remove('hidden');
        
        // Hide message after 5 seconds
        setTimeout(() => {
            messageEl.classList.add('hidden');
        }, 5000);
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new AuthApp();
});