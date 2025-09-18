class AuthApp {
    constructor() {
        this.apiBaseUrl = 'http://localhost:8000/api/auth';
        this.token = localStorage.getItem('authToken');
        this.init();
    }

    init() {
        this.bindEvents();
        this.checkAuthStatus();
    }

    bindEvents() {
        // Form submissions
        document.getElementById('loginForm').addEventListener('submit', (e) => this.handleLogin(e));
        document.getElementById('registerForm').addEventListener('submit', (e) => this.handleRegister(e));
        
        // Form switching
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
                const response = await this.apiCall('/profile', 'GET');
                if (response.ok) {
                    const profile = await response.json();
                    this.showProfile(profile);
                } else {
                    this.clearToken();
                    this.showLoginForm();
                }
            } catch (error) {
                this.clearToken();
                this.showLoginForm();
            }
        } else {
            this.showLoginForm();
        }
    }

    async apiCall(endpoint, method = 'GET', data = null) {
        const url = `${this.apiBaseUrl}${endpoint}`;
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json',
            },
        };

        if (this.token) {
            options.headers['Authorization'] = `Bearer ${this.token}`;
        }

        if (data) {
            options.body = JSON.stringify(data);
        }

        return fetch(url, options);
    }

    async handleLogin(e) {
        e.preventDefault();
        const formData = new FormData(e.target);
        const loginData = {
            username: formData.get('username'),
            password: formData.get('password')
        };

        try {
            const response = await this.apiCall('/login', 'POST', loginData);
            const result = await response.json();

            if (response.ok) {
                this.token = result.access_token;
                localStorage.setItem('authToken', this.token);
                this.showMessage('Login successful!', 'success');
                
                // Get profile and show it
                const profileResponse = await this.apiCall('/profile', 'GET');
                if (profileResponse.ok) {
                    const profile = await profileResponse.json();
                    this.showProfile(profile);
                }
            } else {
                this.showMessage(result.detail || 'Login failed', 'error');
            }
        } catch (error) {
            this.showMessage('Network error. Please try again.', 'error');
        }
    }

    async handleRegister(e) {
        e.preventDefault();
        const formData = new FormData(e.target);
        const password = formData.get('password');
        const confirmPassword = formData.get('confirmPassword');

        if (password !== confirmPassword) {
            this.showMessage('Passwords do not match', 'error');
            return;
        }

        const registerData = {
            username: formData.get('username'),
            password: password
        };

        try {
            const response = await this.apiCall('/register', 'POST', registerData);
            const result = await response.json();

            if (response.ok) {
                this.showMessage('Registration successful! Please log in.', 'success');
                this.showLoginForm();
                // Clear the register form
                document.getElementById('registerForm').reset();
            } else {
                this.showMessage(result.detail || 'Registration failed', 'error');
            }
        } catch (error) {
            this.showMessage('Network error. Please try again.', 'error');
        }
    }

    async handleLogout() {
        try {
            if (this.token) {
                await this.apiCall('/logout', 'POST');
            }
        } catch (error) {
            console.error('Logout error:', error);
        } finally {
            this.clearToken();
            this.showMessage('Logged out successfully', 'success');
            this.showLoginForm();
        }
    }

    clearToken() {
        this.token = null;
        localStorage.removeItem('authToken');
    }

    showLoginForm() {
        document.getElementById('login-form').classList.remove('hidden');
        document.getElementById('register-form').classList.add('hidden');
        document.getElementById('profile-view').classList.add('hidden');
        
        document.getElementById('header-title').textContent = 'Welcome Back';
        document.getElementById('header-subtitle').textContent = 'Please sign in to continue';
        
        // Clear forms
        document.getElementById('loginForm').reset();
    }

    showRegisterForm() {
        document.getElementById('login-form').classList.add('hidden');
        document.getElementById('register-form').classList.remove('hidden');
        document.getElementById('profile-view').classList.add('hidden');
        
        document.getElementById('header-title').textContent = 'Create Account';
        document.getElementById('header-subtitle').textContent = 'Join us today';
        
        // Clear forms
        document.getElementById('registerForm').reset();
    }

    showProfile(profile) {
        document.getElementById('login-form').classList.add('hidden');
        document.getElementById('register-form').classList.add('hidden');
        document.getElementById('profile-view').classList.remove('hidden');
        
        document.getElementById('header-title').textContent = `Hello, ${profile.username}!`;
        document.getElementById('header-subtitle').textContent = 'Welcome to your dashboard';
        
        // Populate profile data
        document.getElementById('profile-id').textContent = profile.id;
        document.getElementById('profile-username').textContent = profile.username;
        document.getElementById('profile-created').textContent = new Date(profile.created_at).toLocaleDateString();
    }

    showMessage(message, type) {
        const messageContainer = document.getElementById('message-container');
        messageContainer.innerHTML = `<div class="message ${type}">${message}</div>`;
        
        // Auto-hide success messages after 3 seconds
        if (type === 'success') {
            setTimeout(() => {
                messageContainer.innerHTML = '';
            }, 3000);
        }
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new AuthApp();
});
