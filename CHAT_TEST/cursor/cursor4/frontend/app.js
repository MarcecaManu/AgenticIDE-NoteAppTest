// Real-time Chat Application
// Main application logic

class ChatApp {
    constructor() {
        this.username = '';
        this.currentRoom = null;
        this.websocket = null;
        this.typingTimeout = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        
        this.initializeElements();
        this.attachEventListeners();
    }
    
    initializeElements() {
        // Screens
        this.loginScreen = document.getElementById('loginScreen');
        this.roomScreen = document.getElementById('roomScreen');
        this.chatScreen = document.getElementById('chatScreen');
        
        // Login elements
        this.usernameInput = document.getElementById('usernameInput');
        this.joinBtn = document.getElementById('joinBtn');
        
        // Room elements
        this.roomNameInput = document.getElementById('roomNameInput');
        this.createRoomBtn = document.getElementById('createRoomBtn');
        this.roomList = document.getElementById('roomList');
        
        // Chat elements
        this.roomName = document.getElementById('roomName');
        this.backBtn = document.getElementById('backBtn');
        this.messages = document.getElementById('messages');
        this.messageInput = document.getElementById('messageInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.userList = document.getElementById('userList');
        this.userCount = document.getElementById('userCount');
        this.typingIndicator = document.getElementById('typingIndicator');
        this.connectionStatus = document.getElementById('connectionStatus');
    }
    
    attachEventListeners() {
        // Login
        this.joinBtn.addEventListener('click', () => this.handleLogin());
        this.usernameInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.handleLogin();
        });
        
        // Room creation
        this.createRoomBtn.addEventListener('click', () => this.createRoom());
        this.roomNameInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.createRoom();
        });
        
        // Chat
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendMessage();
        });
        this.messageInput.addEventListener('input', () => this.handleTyping());
        this.backBtn.addEventListener('click', () => this.leaveRoom());
    }
    
    showScreen(screen) {
        [this.loginScreen, this.roomScreen, this.chatScreen].forEach(s => {
            s.classList.remove('active');
        });
        screen.classList.add('active');
    }
    
    handleLogin() {
        const username = this.usernameInput.value.trim();
        if (!username) {
            alert('Please enter a username');
            return;
        }
        
        this.username = username;
        this.showScreen(this.roomScreen);
        this.loadRooms();
    }
    
    async loadRooms() {
        try {
            this.roomList.innerHTML = '<div class="loading">Loading rooms...</div>';
            const response = await fetch('/api/chat/rooms');
            const data = await response.json();
            
            if (data.rooms.length === 0) {
                this.roomList.innerHTML = '<div class="loading">No rooms yet. Create one!</div>';
                return;
            }
            
            this.roomList.innerHTML = '';
            data.rooms.forEach(room => {
                const roomItem = document.createElement('div');
                roomItem.className = 'room-item';
                roomItem.innerHTML = `
                    <div class="room-item-info">
                        <h3>${this.escapeHtml(room.name)}</h3>
                        <p>Created ${new Date(room.created_at).toLocaleDateString()}</p>
                    </div>
                    <button class="delete-room-btn" onclick="app.deleteRoom(${room.id}, event)">Delete</button>
                `;
                roomItem.addEventListener('click', () => this.joinRoom(room));
                this.roomList.appendChild(roomItem);
            });
        } catch (error) {
            console.error('Error loading rooms:', error);
            this.roomList.innerHTML = '<div class="error-message">Failed to load rooms</div>';
        }
    }
    
    async createRoom() {
        const roomName = this.roomNameInput.value.trim();
        if (!roomName) {
            alert('Please enter a room name');
            return;
        }
        
        try {
            const response = await fetch('/api/chat/rooms', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: roomName })
            });
            
            if (!response.ok) {
                const error = await response.json();
                alert(error.detail || 'Failed to create room');
                return;
            }
            
            this.roomNameInput.value = '';
            this.loadRooms();
        } catch (error) {
            console.error('Error creating room:', error);
            alert('Failed to create room');
        }
    }
    
    async deleteRoom(roomId, event) {
        event.stopPropagation();
        
        if (!confirm('Are you sure you want to delete this room?')) {
            return;
        }
        
        try {
            const response = await fetch(`/api/chat/rooms/${roomId}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                this.loadRooms();
            } else {
                alert('Failed to delete room');
            }
        } catch (error) {
            console.error('Error deleting room:', error);
            alert('Failed to delete room');
        }
    }
    
    async joinRoom(room) {
        this.currentRoom = room;
        this.roomName.textContent = room.name;
        this.showScreen(this.chatScreen);
        this.messages.innerHTML = '<div class="system-message">Loading messages...</div>';
        
        // Load message history
        await this.loadMessages(room.id);
        
        // Connect WebSocket
        this.connectWebSocket(room.id);
    }
    
    async loadMessages(roomId) {
        try {
            const response = await fetch(`/api/chat/rooms/${roomId}/messages`);
            const messages = await response.json();
            
            this.messages.innerHTML = '';
            messages.forEach(msg => {
                this.displayMessage({
                    username: msg.username,
                    content: msg.content,
                    timestamp: msg.timestamp
                }, false);
            });
            
            this.scrollToBottom();
        } catch (error) {
            console.error('Error loading messages:', error);
            this.messages.innerHTML = '<div class="error-message">Failed to load messages</div>';
        }
    }
    
    connectWebSocket(roomId) {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/chat/${roomId}?username=${encodeURIComponent(this.username)}`;
        
        this.websocket = new WebSocket(wsUrl);
        
        this.websocket.onopen = () => {
            console.log('WebSocket connected');
            this.reconnectAttempts = 0;
            this.updateConnectionStatus(true);
        };
        
        this.websocket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleWebSocketMessage(data);
        };
        
        this.websocket.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.updateConnectionStatus(false);
        };
        
        this.websocket.onclose = () => {
            console.log('WebSocket disconnected');
            this.updateConnectionStatus(false);
            this.attemptReconnect();
        };
    }
    
    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'message':
                this.displayMessage(data, true);
                break;
            case 'join':
            case 'leave':
                this.displaySystemMessage(data.content);
                break;
            case 'users_list':
                this.updateUserList(data.users);
                break;
            case 'typing':
                this.showTypingIndicator(data.username);
                break;
        }
    }
    
    displayMessage(data, scroll = true) {
        const messageDiv = document.createElement('div');
        const isOwnMessage = data.username === this.username;
        messageDiv.className = `message ${isOwnMessage ? 'own' : 'other'}`;
        
        const time = data.timestamp ? new Date(data.timestamp).toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit'
        }) : '';
        
        messageDiv.innerHTML = `
            <div class="message-header">${this.escapeHtml(data.username)}</div>
            <div class="message-content">${this.escapeHtml(data.content)}</div>
            ${time ? `<div class="message-time">${time}</div>` : ''}
        `;
        
        this.messages.appendChild(messageDiv);
        if (scroll) this.scrollToBottom();
    }
    
    displaySystemMessage(content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'system-message';
        messageDiv.textContent = content;
        this.messages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    updateUserList(users) {
        this.userList.innerHTML = '';
        this.userCount.textContent = users.length;
        
        users.forEach(user => {
            const li = document.createElement('li');
            li.textContent = user;
            if (user === this.username) {
                li.style.fontWeight = 'bold';
            }
            this.userList.appendChild(li);
        });
    }
    
    showTypingIndicator(username) {
        this.typingIndicator.querySelector('span').textContent = username;
        this.typingIndicator.style.display = 'block';
        
        clearTimeout(this.typingTimeout);
        this.typingTimeout = setTimeout(() => {
            this.typingIndicator.style.display = 'none';
        }, 3000);
    }
    
    handleTyping() {
        if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
            this.websocket.send(JSON.stringify({ type: 'typing' }));
        }
    }
    
    sendMessage() {
        const content = this.messageInput.value.trim();
        if (!content || !this.websocket || this.websocket.readyState !== WebSocket.OPEN) {
            return;
        }
        
        this.websocket.send(JSON.stringify({
            type: 'message',
            content: content
        }));
        
        this.messageInput.value = '';
    }
    
    updateConnectionStatus(connected) {
        const statusDot = this.connectionStatus.querySelector('.status-dot');
        const statusText = this.connectionStatus.querySelector('.status-text');
        
        if (connected) {
            statusDot.classList.remove('disconnected');
            statusText.textContent = 'Connected';
        } else {
            statusDot.classList.add('disconnected');
            statusText.textContent = 'Disconnected';
        }
    }
    
    attemptReconnect() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            this.displaySystemMessage('Connection lost. Please refresh the page.');
            return;
        }
        
        this.reconnectAttempts++;
        const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 10000);
        
        setTimeout(() => {
            if (this.currentRoom) {
                console.log(`Reconnecting... (attempt ${this.reconnectAttempts})`);
                this.connectWebSocket(this.currentRoom.id);
            }
        }, delay);
    }
    
    leaveRoom() {
        if (this.websocket) {
            this.websocket.close();
            this.websocket = null;
        }
        
        this.currentRoom = null;
        this.showScreen(this.roomScreen);
        this.loadRooms();
    }
    
    scrollToBottom() {
        this.messages.scrollTop = this.messages.scrollHeight;
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize app
const app = new ChatApp();


