// Configuration
const API_BASE = 'http://localhost:8000';
const WS_BASE = 'ws://localhost:8000';

// State
let currentRoom = null;
let currentUsername = null;
let websocket = null;
let typingTimeout = null;
let reconnectAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 5;

// DOM Elements
const roomSelectionScreen = document.getElementById('roomSelection');
const chatScreen = document.getElementById('chatScreen');
const usernameInput = document.getElementById('usernameInput');
const newRoomNameInput = document.getElementById('newRoomName');
const createRoomBtn = document.getElementById('createRoomBtn');
const roomList = document.getElementById('roomList');
const roomNameDisplay = document.getElementById('roomName');
const connectionStatus = document.getElementById('connectionStatus');
const leaveRoomBtn = document.getElementById('leaveRoomBtn');
const usersList = document.getElementById('usersList');
const typingIndicator = document.getElementById('typingIndicator');
const messageContainer = document.getElementById('messageContainer');
const messageInput = document.getElementById('messageInput');
const sendMessageBtn = document.getElementById('sendMessageBtn');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadRooms();
    setupEventListeners();
});

// Event Listeners
function setupEventListeners() {
    createRoomBtn.addEventListener('click', createRoom);
    newRoomNameInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') createRoom();
    });
    
    leaveRoomBtn.addEventListener('click', leaveRoom);
    
    sendMessageBtn.addEventListener('click', sendMessage);
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });
    
    messageInput.addEventListener('input', handleTyping);
}

// API Functions
async function loadRooms() {
    try {
        const response = await fetch(`${API_BASE}/api/chat/rooms`);
        const rooms = await response.json();
        displayRooms(rooms);
    } catch (error) {
        console.error('Error loading rooms:', error);
        roomList.innerHTML = '<p class="error">Failed to load rooms. Please try again.</p>';
    }
}

async function createRoom() {
    const roomName = newRoomNameInput.value.trim();
    const username = usernameInput.value.trim();
    
    if (!roomName) {
        alert('Please enter a room name');
        return;
    }
    
    if (!username) {
        alert('Please enter your username');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/api/chat/rooms`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name: roomName }),
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to create room');
        }
        
        const room = await response.json();
        newRoomNameInput.value = '';
        joinRoom(room.id, room.name, username);
    } catch (error) {
        console.error('Error creating room:', error);
        alert(error.message);
    }
}

function displayRooms(rooms) {
    if (rooms.length === 0) {
        roomList.innerHTML = '<p class="no-users">No rooms available. Create one!</p>';
        return;
    }
    
    roomList.innerHTML = rooms.map(room => `
        <div class="room-item" onclick="joinRoomFromList(${room.id}, '${room.name}')">
            <h3>${escapeHtml(room.name)}</h3>
            <div class="room-meta">Created: ${formatDate(room.created_at)}</div>
        </div>
    `).join('');
}

function joinRoomFromList(roomId, roomName) {
    const username = usernameInput.value.trim();
    
    if (!username) {
        alert('Please enter your username');
        return;
    }
    
    joinRoom(roomId, roomName, username);
}

// Chat Functions
async function joinRoom(roomId, roomName, username) {
    currentRoom = { id: roomId, name: roomName };
    currentUsername = username;
    
    // Switch to chat screen
    roomSelectionScreen.classList.remove('active');
    chatScreen.classList.add('active');
    roomNameDisplay.textContent = roomName;
    
    // Load message history
    await loadMessages(roomId);
    
    // Connect WebSocket
    connectWebSocket(roomId, username);
    
    // Enable input
    messageInput.disabled = false;
    sendMessageBtn.disabled = false;
    messageInput.focus();
}

async function loadMessages(roomId) {
    try {
        const response = await fetch(`${API_BASE}/api/chat/rooms/${roomId}/messages`);
        const messages = await response.json();
        
        messageContainer.innerHTML = '';
        
        if (messages.length === 0) {
            messageContainer.innerHTML = '<p class="no-users">No messages yet. Start the conversation!</p>';
        } else {
            messages.forEach(msg => displayMessage(msg));
            scrollToBottom();
        }
    } catch (error) {
        console.error('Error loading messages:', error);
        messageContainer.innerHTML = '<p class="error">Failed to load messages.</p>';
    }
}

function connectWebSocket(roomId, username) {
    updateConnectionStatus('connecting');
    
    websocket = new WebSocket(`${WS_BASE}/ws/chat/${roomId}?username=${encodeURIComponent(username)}`);
    
    websocket.onopen = () => {
        console.log('WebSocket connected');
        updateConnectionStatus('connected');
        reconnectAttempts = 0;
    };
    
    websocket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleWebSocketMessage(data);
    };
    
    websocket.onerror = (error) => {
        console.error('WebSocket error:', error);
        updateConnectionStatus('disconnected');
    };
    
    websocket.onclose = () => {
        console.log('WebSocket disconnected');
        updateConnectionStatus('disconnected');
        
        // Attempt to reconnect
        if (currentRoom && reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
            reconnectAttempts++;
            console.log(`Reconnection attempt ${reconnectAttempts}/${MAX_RECONNECT_ATTEMPTS}`);
            setTimeout(() => {
                if (currentRoom) {
                    connectWebSocket(currentRoom.id, currentUsername);
                }
            }, 2000 * reconnectAttempts);
        } else if (reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
            showError('Connection lost. Please refresh the page.');
        }
    };
}

function handleWebSocketMessage(data) {
    switch (data.type) {
        case 'message':
            displayMessage(data);
            scrollToBottom();
            break;
        
        case 'join':
            displaySystemMessage(data.content);
            scrollToBottom();
            break;
        
        case 'leave':
            displaySystemMessage(data.content);
            scrollToBottom();
            break;
        
        case 'user_list':
            updateUsersList(data.users);
            break;
        
        case 'typing':
            updateTypingIndicator(data.users);
            break;
    }
}

function sendMessage() {
    const content = messageInput.value.trim();
    
    if (!content || !websocket || websocket.readyState !== WebSocket.OPEN) {
        return;
    }
    
    websocket.send(JSON.stringify({
        type: 'message',
        content: content
    }));
    
    messageInput.value = '';
    
    // Stop typing indicator
    if (typingTimeout) {
        clearTimeout(typingTimeout);
        typingTimeout = null;
    }
    websocket.send(JSON.stringify({
        type: 'typing',
        is_typing: false
    }));
}

function handleTyping() {
    if (!websocket || websocket.readyState !== WebSocket.OPEN) {
        return;
    }
    
    // Send typing indicator
    websocket.send(JSON.stringify({
        type: 'typing',
        is_typing: true
    }));
    
    // Clear previous timeout
    if (typingTimeout) {
        clearTimeout(typingTimeout);
    }
    
    // Stop typing after 2 seconds of inactivity
    typingTimeout = setTimeout(() => {
        websocket.send(JSON.stringify({
            type: 'typing',
            is_typing: false
        }));
    }, 2000);
}

function leaveRoom() {
    if (websocket) {
        websocket.close();
        websocket = null;
    }
    
    currentRoom = null;
    currentUsername = null;
    reconnectAttempts = 0;
    
    // Switch back to room selection
    chatScreen.classList.remove('active');
    roomSelectionScreen.classList.add('active');
    
    // Reset UI
    messageContainer.innerHTML = '';
    messageInput.value = '';
    messageInput.disabled = true;
    sendMessageBtn.disabled = true;
    
    // Reload rooms
    loadRooms();
}

// UI Update Functions
function displayMessage(message) {
    const isOwnMessage = message.username === currentUsername;
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isOwnMessage ? 'own' : ''}`;
    
    const time = formatTime(message.timestamp);
    
    messageDiv.innerHTML = `
        <div class="message-header">
            <span class="message-username">${escapeHtml(message.username)}</span>
            <span class="message-time">${time}</span>
        </div>
        <div class="message-content">${escapeHtml(message.content)}</div>
    `;
    
    messageContainer.appendChild(messageDiv);
}

function displaySystemMessage(content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'system-message';
    messageDiv.textContent = content;
    messageContainer.appendChild(messageDiv);
}

function updateUsersList(users) {
    if (users.length === 0) {
        usersList.innerHTML = '<p class="no-users">No users online</p>';
        return;
    }
    
    usersList.innerHTML = users.map(user => `
        <div class="user-item">${escapeHtml(user)}</div>
    `).join('');
}

function updateTypingIndicator(typingUsers) {
    const filtered = typingUsers.filter(u => u !== currentUsername);
    
    if (filtered.length === 0) {
        typingIndicator.textContent = '';
    } else if (filtered.length === 1) {
        typingIndicator.textContent = `${filtered[0]} is typing...`;
    } else {
        typingIndicator.textContent = `${filtered.length} people are typing...`;
    }
}

function updateConnectionStatus(status) {
    connectionStatus.className = `status ${status}`;
    
    const statusText = {
        'connected': 'Connected',
        'disconnected': 'Disconnected',
        'connecting': 'Connecting...'
    };
    
    connectionStatus.textContent = statusText[status] || status;
}

function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error';
    errorDiv.textContent = message;
    messageContainer.appendChild(errorDiv);
    scrollToBottom();
}

function scrollToBottom() {
    messageContainer.scrollTop = messageContainer.scrollHeight;
}

// Utility Functions
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

function formatTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}
