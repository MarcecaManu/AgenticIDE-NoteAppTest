/**
 * Real-time Chat Application Frontend
 */

class ChatApp {
    constructor() {
        this.baseURL = window.location.origin;
        this.wsURL = `ws://${window.location.host}`;
        this.ws = null;
        this.currentRoom = null;
        this.currentUsername = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.typingTimeout = null;
        
        this.init();
    }
    
    init() {
        this.bindElements();
        this.attachEventListeners();
        this.loadRooms();
        
        // Load saved username
        const savedUsername = localStorage.getItem('chat_username');
        if (savedUsername) {
            this.elements.usernameInput.value = savedUsername;
        }
    }
    
    bindElements() {
        this.elements = {
            // Screens
            roomSelection: document.getElementById('roomSelection'),
            chatRoom: document.getElementById('chatRoom'),
            
            // Room selection elements
            usernameInput: document.getElementById('usernameInput'),
            roomNameInput: document.getElementById('roomNameInput'),
            createRoomBtn: document.getElementById('createRoomBtn'),
            roomsList: document.getElementById('roomsList'),
            
            // Chat room elements
            currentRoomName: document.getElementById('currentRoomName'),
            leaveRoomBtn: document.getElementById('leaveRoomBtn'),
            onlineCount: document.getElementById('onlineCount'),
            usersList: document.getElementById('usersList'),
            messagesContainer: document.getElementById('messagesContainer'),
            typingIndicator: document.getElementById('typingIndicator'),
            messageInput: document.getElementById('messageInput'),
            sendMessageBtn: document.getElementById('sendMessageBtn'),
            connectionStatus: document.getElementById('connectionStatus')
        };
    }
    
    attachEventListeners() {
        // Create room
        this.elements.createRoomBtn.addEventListener('click', () => this.createRoom());
        this.elements.roomNameInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.createRoom();
        });
        
        // Leave room
        this.elements.leaveRoomBtn.addEventListener('click', () => this.leaveRoom());
        
        // Send message
        this.elements.sendMessageBtn.addEventListener('click', () => this.sendMessage());
        this.elements.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Typing indicator
        this.elements.messageInput.addEventListener('input', () => this.handleTyping());
    }
    
    // API Methods
    async loadRooms() {
        try {
            const response = await fetch(`${this.baseURL}/api/chat/rooms`);
            const rooms = await response.json();
            this.displayRooms(rooms);
        } catch (error) {
            console.error('Error loading rooms:', error);
            this.elements.roomsList.innerHTML = '<div class="loading">Error loading rooms</div>';
        }
    }
    
    async createRoom() {
        const roomName = this.elements.roomNameInput.value.trim();
        if (!roomName) {
            alert('Please enter a room name');
            return;
        }
        
        try {
            const response = await fetch(`${this.baseURL}/api/chat/rooms`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: roomName })
            });
            
            if (response.ok) {
                const room = await response.json();
                this.elements.roomNameInput.value = '';
                this.loadRooms();
                this.joinRoom(room.id, room.name);
            } else {
                alert('Error creating room');
            }
        } catch (error) {
            console.error('Error creating room:', error);
            alert('Error creating room');
        }
    }
    
    async deleteRoom(roomId, event) {
        event.stopPropagation();
        
        if (!confirm('Are you sure you want to delete this room?')) {
            return;
        }
        
        try {
            const response = await fetch(`${this.baseURL}/api/chat/rooms/${roomId}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                this.loadRooms();
            } else {
                alert('Error deleting room');
            }
        } catch (error) {
            console.error('Error deleting room:', error);
            alert('Error deleting room');
        }
    }
    
    displayRooms(rooms) {
        if (rooms.length === 0) {
            this.elements.roomsList.innerHTML = '<div class="loading">No rooms available. Create one!</div>';
            return;
        }
        
        this.elements.roomsList.innerHTML = rooms.map(room => `
            <div class="room-card" onclick="chatApp.joinRoom('${room.id}', '${this.escapeHtml(room.name)}')">
                <div class="room-card-info">
                    <h4>${this.escapeHtml(room.name)}</h4>
                    <p>Created: ${new Date(room.created_at).toLocaleString()}</p>
                </div>
                <div class="room-card-actions">
                    <button class="btn btn-danger btn-small" onclick="chatApp.deleteRoom('${room.id}', event)">Delete</button>
                </div>
            </div>
        `).join('');
    }
    
    // WebSocket Methods
    joinRoom(roomId, roomName) {
        const username = this.elements.usernameInput.value.trim() || 'Anonymous';
        this.currentUsername = username;
        this.currentRoom = { id: roomId, name: roomName };
        
        // Save username
        localStorage.setItem('chat_username', username);
        
        // Update UI
        this.elements.currentRoomName.textContent = roomName;
        this.showScreen('chatRoom');
        
        // Clear messages
        this.elements.messagesContainer.innerHTML = '';
        
        // Load message history
        this.loadMessageHistory(roomId);
        
        // Connect WebSocket
        this.connectWebSocket(roomId, username);
    }
    
    async loadMessageHistory(roomId) {
        try {
            const response = await fetch(`${this.baseURL}/api/chat/rooms/${roomId}/messages`);
            const messages = await response.json();
            
            messages.forEach(msg => {
                this.displayMessage({
                    type: 'message',
                    id: msg.id,
                    username: msg.username,
                    content: msg.content,
                    timestamp: msg.timestamp
                }, false);
            });
            
            this.scrollToBottom();
        } catch (error) {
            console.error('Error loading message history:', error);
        }
    }
    
    connectWebSocket(roomId, username) {
        if (this.ws) {
            this.ws.close();
        }
        
        const wsUrl = `${this.wsURL}/ws/chat/${roomId}?username=${encodeURIComponent(username)}`;
        this.ws = new WebSocket(wsUrl);
        
        this.ws.onopen = () => {
            console.log('WebSocket connected');
            this.reconnectAttempts = 0;
            this.updateConnectionStatus('connected');
        };
        
        this.ws.onmessage = (event) => {
            const message = JSON.parse(event.data);
            this.handleWebSocketMessage(message);
        };
        
        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.updateConnectionStatus('error');
        };
        
        this.ws.onclose = () => {
            console.log('WebSocket closed');
            this.updateConnectionStatus('disconnected');
            this.attemptReconnect();
        };
    }
    
    handleWebSocketMessage(message) {
        switch (message.type) {
            case 'message':
                this.displayMessage(message);
                break;
            
            case 'join':
                this.displaySystemMessage(message.content);
                this.updateOnlineUsers(message.online_users);
                break;
            
            case 'leave':
                this.displaySystemMessage(message.content);
                this.updateOnlineUsers(message.online_users);
                break;
            
            case 'typing':
                this.displayTypingIndicator(message.username);
                break;
            
            case 'room_deleted':
                alert('This room has been deleted');
                this.leaveRoom();
                break;
        }
    }
    
    sendMessage() {
        const content = this.elements.messageInput.value.trim();
        if (!content || !this.ws || this.ws.readyState !== WebSocket.OPEN) {
            return;
        }
        
        const message = {
            type: 'message',
            content: content
        };
        
        this.ws.send(JSON.stringify(message));
        this.elements.messageInput.value = '';
        this.elements.typingIndicator.textContent = '';
    }
    
    handleTyping() {
        if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
            return;
        }
        
        // Clear previous timeout
        clearTimeout(this.typingTimeout);
        
        // Send typing indicator
        const isTyping = this.elements.messageInput.value.length > 0;
        if (isTyping) {
            this.ws.send(JSON.stringify({
                type: 'typing',
                content: 'typing'
            }));
        }
        
        // Clear typing indicator after 2 seconds of inactivity
        this.typingTimeout = setTimeout(() => {
            if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                this.ws.send(JSON.stringify({
                    type: 'typing',
                    content: ''
                }));
            }
        }, 2000);
    }
    
    displayMessage(message, scroll = true) {
        const isOwn = message.username === this.currentUsername;
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isOwn ? 'own' : 'other'}`;
        
        const time = new Date(message.timestamp).toLocaleTimeString([], { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
        
        messageDiv.innerHTML = `
            <div class="message-header">
                <span class="message-username">${this.escapeHtml(message.username)}</span>
                <span class="message-timestamp">${time}</span>
            </div>
            <div class="message-content">${this.escapeHtml(message.content)}</div>
        `;
        
        this.elements.messagesContainer.appendChild(messageDiv);
        
        if (scroll) {
            this.scrollToBottom();
        }
    }
    
    displaySystemMessage(content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'system-message';
        messageDiv.textContent = content;
        this.elements.messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    displayTypingIndicator(username) {
        if (username === this.currentUsername) {
            return;
        }
        
        this.elements.typingIndicator.textContent = `${username} is typing...`;
        
        // Clear after 3 seconds
        clearTimeout(this.typingIndicatorTimeout);
        this.typingIndicatorTimeout = setTimeout(() => {
            this.elements.typingIndicator.textContent = '';
        }, 3000);
    }
    
    updateOnlineUsers(users) {
        this.elements.onlineCount.textContent = users.length;
        this.elements.usersList.innerHTML = users.map(user => `
            <div class="user-item">${this.escapeHtml(user)}</div>
        `).join('');
    }
    
    updateConnectionStatus(status) {
        const statusEl = this.elements.connectionStatus;
        statusEl.className = 'connection-status';
        
        switch (status) {
            case 'connected':
                statusEl.style.display = 'none';
                break;
            
            case 'error':
                statusEl.classList.add('error');
                statusEl.textContent = 'Connection error. Trying to reconnect...';
                break;
            
            case 'disconnected':
                statusEl.classList.add('reconnecting');
                statusEl.textContent = 'Disconnected. Reconnecting...';
                break;
        }
    }
    
    attemptReconnect() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            alert('Unable to reconnect to chat. Please refresh the page.');
            return;
        }
        
        this.reconnectAttempts++;
        
        setTimeout(() => {
            if (this.currentRoom && this.currentUsername) {
                console.log(`Reconnect attempt ${this.reconnectAttempts}`);
                this.connectWebSocket(this.currentRoom.id, this.currentUsername);
            }
        }, 2000 * this.reconnectAttempts);
    }
    
    leaveRoom() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
        
        this.currentRoom = null;
        this.showScreen('roomSelection');
        this.loadRooms();
    }
    
    // UI Helper Methods
    showScreen(screenName) {
        document.querySelectorAll('.screen').forEach(screen => {
            screen.classList.remove('active');
        });
        
        this.elements[screenName].classList.add('active');
    }
    
    scrollToBottom() {
        this.elements.messagesContainer.scrollTop = this.elements.messagesContainer.scrollHeight;
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize app when DOM is loaded
let chatApp;
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        chatApp = new ChatApp();
    });
} else {
    chatApp = new ChatApp();
}
