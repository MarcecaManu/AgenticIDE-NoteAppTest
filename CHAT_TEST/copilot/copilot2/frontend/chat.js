// Chat Application JavaScript
const API_BASE_URL = 'http://localhost:8000';
const WS_BASE_URL = 'ws://localhost:8000';

class ChatApp {
    constructor() {
        this.username = localStorage.getItem('username') || '';
        this.currentRoom = null;
        this.websocket = null;
        this.rooms = [];
        this.typingTimeout = null;
        this.isTyping = false;
        
        this.initElements();
        this.attachEventListeners();
        this.init();
    }
    
    initElements() {
        // Username elements
        this.usernameInput = document.getElementById('usernameInput');
        this.setUsernameBtn = document.getElementById('setUsernameBtn');
        
        // Room elements
        this.roomNameInput = document.getElementById('roomNameInput');
        this.createRoomBtn = document.getElementById('createRoomBtn');
        this.roomList = document.getElementById('roomList');
        
        // Chat elements
        this.welcomeScreen = document.getElementById('welcomeScreen');
        this.chatContainer = document.getElementById('chatContainer');
        this.currentRoomName = document.getElementById('currentRoomName');
        this.connectionStatus = document.getElementById('connectionStatus');
        this.messagesContainer = document.getElementById('messagesContainer');
        this.messageInput = document.getElementById('messageInput');
        this.sendMessageBtn = document.getElementById('sendMessageBtn');
        this.typingIndicator = document.getElementById('typingIndicator');
        
        // Users elements
        this.usersList = document.getElementById('usersList');
        this.userCount = document.getElementById('userCount');
    }
    
    attachEventListeners() {
        // Username
        this.setUsernameBtn.addEventListener('click', () => this.setUsername());
        this.usernameInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.setUsername();
        });
        
        // Rooms
        this.createRoomBtn.addEventListener('click', () => this.createRoom());
        this.roomNameInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.createRoom();
        });
        
        // Messages
        this.sendMessageBtn.addEventListener('click', () => this.sendMessage());
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendMessage();
        });
        
        // Typing indicator
        this.messageInput.addEventListener('input', () => this.handleTyping());
    }
    
    async init() {
        if (this.username) {
            this.usernameInput.value = this.username;
            this.usernameInput.disabled = true;
            this.setUsernameBtn.textContent = 'Change';
            this.setupUsernameChangeHandler();
        }
        
        await this.loadRooms();
    }
    
    setupUsernameChangeHandler() {
        // Replace the click handler to allow changing username
        this.setUsernameBtn.onclick = () => {
            if (this.usernameInput.disabled) {
                // Enable editing
                this.usernameInput.disabled = false;
                this.setUsernameBtn.textContent = 'Set';
                this.usernameInput.focus();
                this.usernameInput.select();
            } else {
                // Save the new username
                this.setUsername();
            }
        };
    }
    
    setUsername() {
        const newUsername = this.usernameInput.value.trim();
        
        if (!newUsername) {
            this.showError('Please enter a username');
            return;
        }
        
        if (this.username && this.websocket && newUsername !== this.username) {
            // Disconnect from current room if changing username
            this.disconnectWebSocket();
            this.currentRoom = null;
            this.showWelcomeScreen();
        }
        
        this.username = newUsername;
        localStorage.setItem('username', this.username);
        this.usernameInput.disabled = true;
        this.setUsernameBtn.textContent = 'Change';
        
        // Set up change handler
        this.setupUsernameChangeHandler();
    }
    
    async loadRooms() {
        try {
            const response = await fetch(`${API_BASE_URL}/api/chat/rooms`);
            this.rooms = await response.json();
            this.renderRooms();
        } catch (error) {
            console.error('Error loading rooms:', error);
            this.showError('Failed to load rooms');
        }
    }
    
    renderRooms() {
        this.roomList.innerHTML = '';
        
        this.rooms.forEach(room => {
            const li = document.createElement('li');
            li.className = 'room-item';
            if (this.currentRoom && this.currentRoom.id === room.id) {
                li.classList.add('active');
            }
            
            const roomName = document.createElement('span');
            roomName.textContent = room.name;
            
            const deleteBtn = document.createElement('button');
            deleteBtn.className = 'delete-btn';
            deleteBtn.textContent = 'Delete';
            deleteBtn.onclick = (e) => {
                e.stopPropagation();
                this.deleteRoom(room.id);
            };
            
            li.appendChild(roomName);
            li.appendChild(deleteBtn);
            li.onclick = () => this.joinRoom(room);
            
            this.roomList.appendChild(li);
        });
    }
    
    async createRoom() {
        const roomName = this.roomNameInput.value.trim();
        
        if (!roomName) {
            this.showError('Please enter a room name');
            return;
        }
        
        try {
            const response = await fetch(`${API_BASE_URL}/api/chat/rooms`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ name: roomName }),
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail);
            }
            
            const newRoom = await response.json();
            this.roomNameInput.value = '';
            await this.loadRooms();
            this.joinRoom(newRoom);
        } catch (error) {
            console.error('Error creating room:', error);
            this.showError(error.message || 'Failed to create room');
        }
    }
    
    async deleteRoom(roomId) {
        if (!confirm('Are you sure you want to delete this room?')) {
            return;
        }
        
        try {
            const response = await fetch(`${API_BASE_URL}/api/chat/rooms/${roomId}`, {
                method: 'DELETE',
            });
            
            if (!response.ok) {
                throw new Error('Failed to delete room');
            }
            
            if (this.currentRoom && this.currentRoom.id === roomId) {
                this.disconnectWebSocket();
                this.currentRoom = null;
                this.showWelcomeScreen();
            }
            
            await this.loadRooms();
        } catch (error) {
            console.error('Error deleting room:', error);
            this.showError('Failed to delete room');
        }
    }
    
    async joinRoom(room) {
        if (!this.username) {
            this.showError('Please set your username first');
            return;
        }
        
        // Disconnect from previous room
        if (this.websocket) {
            this.disconnectWebSocket();
        }
        
        this.currentRoom = room;
        this.showChatContainer();
        this.currentRoomName.textContent = room.name;
        this.messagesContainer.innerHTML = '';
        
        // Load message history
        await this.loadMessageHistory(room.id);
        
        // Connect WebSocket
        this.connectWebSocket(room.id);
        
        // Update UI
        this.renderRooms();
    }
    
    async loadMessageHistory(roomId) {
        try {
            const response = await fetch(`${API_BASE_URL}/api/chat/rooms/${roomId}/messages`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const messages = await response.json();
            
            messages.forEach(message => {
                this.displayMessage({
                    ...message,
                    message_type: 'message'
                }, false);
            });
            
            this.scrollToBottom();
        } catch (error) {
            console.error('Error loading message history:', error);
            this.showError('Failed to load message history: ' + error.message);
        }
    }
    
    connectWebSocket(roomId) {
        const wsUrl = `${WS_BASE_URL}/ws/chat/${roomId}?username=${encodeURIComponent(this.username)}`;
        
        this.websocket = new WebSocket(wsUrl);
        
        this.websocket.onopen = () => {
            console.log('WebSocket connected');
            this.updateConnectionStatus(true);
            this.messageInput.disabled = false;
            this.sendMessageBtn.disabled = false;
        };
        
        this.websocket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleWebSocketMessage(data);
        };
        
        this.websocket.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.showError('Connection error occurred');
        };
        
        this.websocket.onclose = () => {
            console.log('WebSocket disconnected');
            this.updateConnectionStatus(false);
            this.messageInput.disabled = true;
            this.sendMessageBtn.disabled = true;
            
            // Try to reconnect after 3 seconds if still in a room
            if (this.currentRoom) {
                setTimeout(() => {
                    if (this.currentRoom && !this.websocket) {
                        console.log('Attempting to reconnect...');
                        this.connectWebSocket(this.currentRoom.id);
                    }
                }, 3000);
            }
        };
    }
    
    disconnectWebSocket() {
        if (this.websocket) {
            this.websocket.close();
            this.websocket = null;
        }
    }
    
    handleWebSocketMessage(data) {
        const messageType = data.message_type;
        
        if (messageType === 'user_list') {
            this.updateUsersList(data.users);
        } else if (messageType === 'typing') {
            this.handleTypingIndicator(data.username, data.is_typing);
        } else if (messageType === 'message' || messageType === 'join' || messageType === 'leave') {
            this.displayMessage(data);
            this.scrollToBottom();
        }
    }
    
    displayMessage(data, animate = true) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message';
        
        const isOwn = data.username === this.username && data.message_type === 'message';
        const isSystem = data.message_type === 'join' || data.message_type === 'leave';
        
        if (isOwn) {
            messageDiv.classList.add('own');
        }
        if (isSystem) {
            messageDiv.classList.add('system');
        }
        
        if (!isSystem) {
            const header = document.createElement('div');
            header.className = 'message-header';
            
            const username = document.createElement('span');
            username.className = 'message-username';
            username.textContent = data.username;
            
            const timestamp = document.createElement('span');
            timestamp.className = 'message-timestamp';
            timestamp.textContent = this.formatTimestamp(data.timestamp);
            
            header.appendChild(username);
            header.appendChild(timestamp);
            messageDiv.appendChild(header);
        }
        
        const content = document.createElement('div');
        content.className = 'message-content';
        content.textContent = data.content;
        messageDiv.appendChild(content);
        
        // Append to messages container
        // Check if typing indicator is in the DOM and is a child of messagesContainer
        if (this.typingIndicator && this.typingIndicator.parentNode === this.messagesContainer) {
            this.messagesContainer.insertBefore(messageDiv, this.typingIndicator);
        } else {
            this.messagesContainer.appendChild(messageDiv);
        }
    }
    
    sendMessage() {
        const content = this.messageInput.value.trim();
        
        if (!content || !this.websocket) {
            return;
        }
        
        const message = {
            message_type: 'message',
            content: content,
        };
        
        this.websocket.send(JSON.stringify(message));
        this.messageInput.value = '';
        
        // Stop typing indicator
        this.sendTypingIndicator(false);
    }
    
    handleTyping() {
        if (!this.websocket) return;
        
        // Start typing
        if (!this.isTyping) {
            this.isTyping = true;
            this.sendTypingIndicator(true);
        }
        
        // Reset timeout
        clearTimeout(this.typingTimeout);
        this.typingTimeout = setTimeout(() => {
            this.isTyping = false;
            this.sendTypingIndicator(false);
        }, 2000);
    }
    
    sendTypingIndicator(isTyping) {
        if (!this.websocket) return;
        
        const message = {
            message_type: 'typing',
            is_typing: isTyping,
        };
        
        this.websocket.send(JSON.stringify(message));
    }
    
    handleTypingIndicator(username, isTyping) {
        if (username === this.username) return;
        
        if (isTyping) {
            this.typingIndicator.textContent = `${username} is typing...`;
            this.typingIndicator.style.display = 'block';
        } else {
            this.typingIndicator.style.display = 'none';
        }
    }
    
    updateUsersList(users) {
        this.usersList.innerHTML = '';
        this.userCount.textContent = users.length;
        
        users.forEach(user => {
            const li = document.createElement('li');
            li.className = 'user-item';
            li.textContent = user;
            this.usersList.appendChild(li);
        });
    }
    
    updateConnectionStatus(connected) {
        if (connected) {
            this.connectionStatus.textContent = 'Connected';
            this.connectionStatus.className = 'connection-status connected';
        } else {
            this.connectionStatus.textContent = 'Disconnected';
            this.connectionStatus.className = 'connection-status disconnected';
        }
    }
    
    showWelcomeScreen() {
        this.welcomeScreen.style.display = 'flex';
        this.chatContainer.style.display = 'none';
        this.usersList.innerHTML = '';
        this.userCount.textContent = '0';
    }
    
    showChatContainer() {
        this.welcomeScreen.style.display = 'none';
        this.chatContainer.style.display = 'flex';
    }
    
    showError(message) {
        // Display error in console for debugging
        console.error('Error:', message);
        
        // Show error message in UI
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = message;
        errorDiv.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #f8d7da;
            color: #721c24;
            padding: 15px 20px;
            border-radius: 5px;
            border: 1px solid #f5c6cb;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            z-index: 9999;
            max-width: 400px;
            animation: slideIn 0.3s ease-out;
        `;
        
        document.body.appendChild(errorDiv);
        
        // Remove error after 5 seconds
        setTimeout(() => {
            errorDiv.style.opacity = '0';
            errorDiv.style.transition = 'opacity 0.3s';
            setTimeout(() => errorDiv.remove(), 300);
        }, 5000);
    }
    
    formatTimestamp(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const isToday = date.toDateString() === now.toDateString();
        
        const timeString = date.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit'
        });
        
        if (isToday) {
            return timeString;
        } else {
            return `${date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })} ${timeString}`;
        }
    }
    
    scrollToBottom() {
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ChatApp();
});
