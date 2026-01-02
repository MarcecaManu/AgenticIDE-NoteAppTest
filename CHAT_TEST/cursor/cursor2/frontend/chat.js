/**
 * Real-time Chat System - Frontend JavaScript
 */

class ChatApp {
    constructor() {
        this.ws = null;
        this.currentRoom = null;
        this.currentUsername = null;
        this.rooms = [];
        this.selectedRoomId = null;
        this.typingTimeout = null;
        this.isTyping = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        
        this.init();
    }

    init() {
        // Get DOM elements
        this.setupScreen = document.getElementById('setupScreen');
        this.chatScreen = document.getElementById('chatScreen');
        this.usernameInput = document.getElementById('usernameInput');
        this.roomsList = document.getElementById('roomsList');
        this.newRoomInput = document.getElementById('newRoomInput');
        this.createRoomBtn = document.getElementById('createRoomBtn');
        this.joinRoomBtn = document.getElementById('joinRoomBtn');
        this.leaveRoomBtn = document.getElementById('leaveRoomBtn');
        this.messagesContainer = document.getElementById('messagesContainer');
        this.messageInput = document.getElementById('messageInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.usersList = document.getElementById('usersList');
        this.userCount = document.getElementById('userCount');
        this.roomName = document.getElementById('roomName');
        this.chatRoomName = document.getElementById('chatRoomName');
        this.typingIndicator = document.getElementById('typingIndicator');
        this.connectionStatus = document.getElementById('connectionStatus');
        this.connectionText = document.getElementById('connectionText');

        // Setup event listeners
        this.setupEventListeners();
        
        // Load rooms
        this.loadRooms();
    }

    setupEventListeners() {
        // Setup screen events
        this.createRoomBtn.addEventListener('click', () => this.createRoom());
        this.joinRoomBtn.addEventListener('click', () => this.joinRoom());
        this.newRoomInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.createRoom();
        });

        // Chat screen events
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendMessage();
        });
        this.messageInput.addEventListener('input', () => this.handleTyping());
        this.leaveRoomBtn.addEventListener('click', () => this.leaveRoom());
    }

    async loadRooms() {
        try {
            const response = await fetch('/api/chat/rooms');
            this.rooms = await response.json();
            this.renderRooms();
        } catch (error) {
            console.error('Error loading rooms:', error);
            this.showError('Failed to load rooms');
        }
    }

    renderRooms() {
        if (this.rooms.length === 0) {
            this.roomsList.innerHTML = '<div class="empty-rooms">No rooms available. Create one!</div>';
            return;
        }

        this.roomsList.innerHTML = this.rooms.map(room => {
            const date = new Date(room.created_at);
            const timeStr = date.toLocaleString();
            return `
                <div class="room-item" data-room-id="${room.id}">
                    <div class="room-item-name">${this.escapeHtml(room.name)}</div>
                    <div class="room-item-time">${timeStr}</div>
                </div>
            `;
        }).join('');

        // Add click handlers
        document.querySelectorAll('.room-item').forEach(item => {
            item.addEventListener('click', () => this.selectRoom(item.dataset.roomId));
        });
    }

    selectRoom(roomId) {
        this.selectedRoomId = roomId;
        
        // Update UI
        document.querySelectorAll('.room-item').forEach(item => {
            item.classList.toggle('selected', item.dataset.roomId === roomId);
        });
        
        this.joinRoomBtn.disabled = false;
    }

    async createRoom() {
        const roomName = this.newRoomInput.value.trim();
        if (!roomName) {
            this.showError('Please enter a room name');
            return;
        }

        try {
            const response = await fetch('/api/chat/rooms', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: roomName })
            });

            if (response.ok) {
                const newRoom = await response.json();
                this.rooms.unshift(newRoom);
                this.renderRooms();
                this.newRoomInput.value = '';
                this.selectRoom(newRoom.id);
            } else {
                this.showError('Failed to create room');
            }
        } catch (error) {
            console.error('Error creating room:', error);
            this.showError('Failed to create room');
        }
    }

    async joinRoom() {
        const username = this.usernameInput.value.trim();
        if (!username) {
            this.showError('Please enter a username');
            return;
        }

        if (!this.selectedRoomId) {
            this.showError('Please select a room');
            return;
        }

        this.currentUsername = username;
        this.currentRoom = this.rooms.find(r => r.id === this.selectedRoomId);

        // Load message history
        await this.loadMessageHistory();

        // Connect to WebSocket
        this.connectWebSocket();

        // Switch to chat screen
        this.setupScreen.classList.remove('active');
        this.chatScreen.classList.add('active');
        
        this.roomName.textContent = this.currentRoom.name;
        this.chatRoomName.textContent = this.currentRoom.name;
        
        this.messageInput.focus();
    }

    async loadMessageHistory() {
        try {
            const response = await fetch(`/api/chat/rooms/${this.selectedRoomId}/messages`);
            const messages = await response.json();
            
            this.messagesContainer.innerHTML = '';
            messages.forEach(msg => this.displayMessage(msg));
            this.scrollToBottom();
        } catch (error) {
            console.error('Error loading message history:', error);
        }
    }

    connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/chat/${this.selectedRoomId}?username=${encodeURIComponent(this.currentUsername)}`;
        
        this.updateConnectionStatus('connecting');
        
        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
            console.log('WebSocket connected');
            this.updateConnectionStatus('connected');
            this.reconnectAttempts = 0;
        };

        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleWebSocketMessage(data);
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

    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'message':
                this.displayMessage(data.data);
                this.scrollToBottom();
                break;
            
            case 'join':
                this.displaySystemMessage(data.data.message);
                this.requestUserList();
                break;
            
            case 'leave':
                this.displaySystemMessage(data.data.message);
                this.requestUserList();
                break;
            
            case 'user_list':
                this.updateUserList(data.data.users);
                break;
            
            case 'typing':
                this.handleTypingIndicator(data.data);
                break;
        }
    }

    displayMessage(message) {
        const date = new Date(message.timestamp);
        const timeStr = date.toLocaleTimeString();
        
        const messageEl = document.createElement('div');
        messageEl.className = 'message';
        messageEl.innerHTML = `
            <div class="message-header">
                <span class="message-username">${this.escapeHtml(message.username)}</span>
                <span class="message-time">${timeStr}</span>
            </div>
            <div class="message-content">${this.escapeHtml(message.content)}</div>
        `;
        
        this.messagesContainer.appendChild(messageEl);
    }

    displaySystemMessage(text) {
        const messageEl = document.createElement('div');
        messageEl.className = 'system-message';
        messageEl.textContent = text;
        this.messagesContainer.appendChild(messageEl);
        this.scrollToBottom();
    }

    sendMessage() {
        const content = this.messageInput.value.trim();
        if (!content || !this.ws || this.ws.readyState !== WebSocket.OPEN) {
            return;
        }

        this.ws.send(JSON.stringify({
            type: 'message',
            content: content
        }));

        this.messageInput.value = '';
        
        // Stop typing indicator
        if (this.isTyping) {
            this.sendTypingStatus(false);
            this.isTyping = false;
        }
    }

    handleTyping() {
        if (!this.ws || this.ws.readyState !== WebSocket.OPEN) return;

        // Send typing start
        if (!this.isTyping) {
            this.isTyping = true;
            this.sendTypingStatus(true);
        }

        // Clear existing timeout
        if (this.typingTimeout) {
            clearTimeout(this.typingTimeout);
        }

        // Set timeout to stop typing indicator
        this.typingTimeout = setTimeout(() => {
            this.isTyping = false;
            this.sendTypingStatus(false);
        }, 2000);
    }

    sendTypingStatus(isTyping) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                type: 'typing',
                is_typing: isTyping
            }));
        }
    }

    handleTypingIndicator(data) {
        if (data.username === this.currentUsername) return;

        if (data.is_typing) {
            this.typingIndicator.textContent = `${data.username} is typing...`;
        } else {
            this.typingIndicator.textContent = '';
        }
    }

    requestUserList() {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                type: 'get_users'
            }));
        }
    }

    updateUserList(users) {
        this.usersList.innerHTML = users.map(user => 
            `<li>${this.escapeHtml(user)}</li>`
        ).join('');
        this.userCount.textContent = users.length;
    }

    updateConnectionStatus(status) {
        this.connectionStatus.className = 'status-indicator';
        
        switch (status) {
            case 'connected':
                this.connectionStatus.classList.add('connected');
                this.connectionText.textContent = 'Connected';
                break;
            case 'connecting':
                this.connectionText.textContent = 'Connecting...';
                break;
            case 'disconnected':
                this.connectionStatus.classList.add('disconnected');
                this.connectionText.textContent = 'Disconnected';
                break;
            case 'error':
                this.connectionStatus.classList.add('disconnected');
                this.connectionText.textContent = 'Connection Error';
                break;
        }
    }

    attemptReconnect() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            this.showError('Connection lost. Please refresh the page.');
            return;
        }

        this.reconnectAttempts++;
        const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 10000);
        
        console.log(`Attempting to reconnect in ${delay}ms...`);
        setTimeout(() => {
            if (this.currentRoom && this.chatScreen.classList.contains('active')) {
                this.connectWebSocket();
            }
        }, delay);
    }

    leaveRoom() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }

        this.currentRoom = null;
        this.currentUsername = null;
        this.selectedRoomId = null;
        this.messagesContainer.innerHTML = '';
        this.typingIndicator.textContent = '';

        this.chatScreen.classList.remove('active');
        this.setupScreen.classList.add('active');
        
        this.loadRooms();
    }

    scrollToBottom() {
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    showError(message) {
        alert(message); // Simple error display
    }
}

// Initialize the chat app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new ChatApp();
});

