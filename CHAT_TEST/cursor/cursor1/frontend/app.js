// Real-time Chat Application JavaScript

// State management
const state = {
    ws: null,
    currentRoom: null,
    username: null,
    rooms: [],
    messages: [],
    users: [],
    typingTimeout: null,
    reconnectAttempts: 0,
    maxReconnectAttempts: 5
};

// API Configuration
const API_BASE = window.location.origin;
const WS_BASE = API_BASE.replace('http', 'ws');

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
});

async function initializeApp() {
    setupEventListeners();
    await loadRooms();
}

function setupEventListeners() {
    // Create room button
    document.getElementById('createRoomBtn').addEventListener('click', showCreateRoomModal);
    
    // Send message
    document.getElementById('sendBtn').addEventListener('click', sendMessage);
    document.getElementById('messageInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
    
    // Typing indicator
    document.getElementById('messageInput').addEventListener('input', handleTyping);
    
    // Leave room
    document.getElementById('leaveRoomBtn').addEventListener('click', leaveRoom);
}

// Room Management

async function loadRooms() {
    try {
        const response = await fetch(`${API_BASE}/api/chat/rooms`);
        if (!response.ok) throw new Error('Failed to load rooms');
        
        state.rooms = await response.json();
        renderRooms();
    } catch (error) {
        console.error('Error loading rooms:', error);
        showError('Failed to load chat rooms');
    }
}

function renderRooms() {
    const roomsList = document.getElementById('roomsList');
    
    if (state.rooms.length === 0) {
        roomsList.innerHTML = '<div class="loading">No rooms available. Create one to get started!</div>';
        return;
    }
    
    roomsList.innerHTML = state.rooms.map(room => `
        <div class="room-item ${state.currentRoom?.id === room.id ? 'active' : ''}" 
             onclick="selectRoom(${room.id})">
            <h3>${escapeHtml(room.name)}</h3>
            <p>${escapeHtml(room.description || 'No description')}</p>
            <div class="room-actions">
                <button class="btn-danger" onclick="event.stopPropagation(); deleteRoom(${room.id})">Delete</button>
            </div>
        </div>
    `).join('');
}

function showCreateRoomModal() {
    document.getElementById('createRoomModal').classList.add('active');
    document.getElementById('roomName').focus();
}

function closeCreateRoomModal() {
    document.getElementById('createRoomModal').classList.remove('active');
    document.getElementById('roomName').value = '';
    document.getElementById('roomDescription').value = '';
    document.getElementById('createRoomError').style.display = 'none';
}

async function createRoom() {
    const name = document.getElementById('roomName').value.trim();
    const description = document.getElementById('roomDescription').value.trim();
    
    if (!name) {
        showModalError('createRoomError', 'Room name is required');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/api/chat/rooms`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name, description })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to create room');
        }
        
        await loadRooms();
        closeCreateRoomModal();
    } catch (error) {
        console.error('Error creating room:', error);
        showModalError('createRoomError', error.message);
    }
}

async function deleteRoom(roomId) {
    if (!confirm('Are you sure you want to delete this room? All messages will be lost.')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/api/chat/rooms/${roomId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) throw new Error('Failed to delete room');
        
        if (state.currentRoom?.id === roomId) {
            leaveRoom();
        }
        
        await loadRooms();
    } catch (error) {
        console.error('Error deleting room:', error);
        showError('Failed to delete room');
    }
}

function selectRoom(roomId) {
    const room = state.rooms.find(r => r.id === roomId);
    if (!room) return;
    
    state.currentRoom = room;
    showJoinRoomModal();
}

// User Authentication

function showJoinRoomModal() {
    document.getElementById('joinRoomModal').classList.add('active');
    document.getElementById('username').focus();
    
    // Pre-fill username if available
    if (state.username) {
        document.getElementById('username').value = state.username;
    }
}

function cancelJoinRoom() {
    document.getElementById('joinRoomModal').classList.remove('active');
    document.getElementById('username').value = '';
    document.getElementById('joinRoomError').style.display = 'none';
    state.currentRoom = null;
    renderRooms();
}

async function confirmJoinRoom() {
    const username = document.getElementById('username').value.trim();
    
    if (!username) {
        showModalError('joinRoomError', 'Username is required');
        return;
    }
    
    state.username = username;
    document.getElementById('joinRoomModal').classList.remove('active');
    
    await joinRoom();
}

// WebSocket Connection

async function joinRoom() {
    if (!state.currentRoom || !state.username) return;
    
    // Close existing connection
    if (state.ws) {
        state.ws.close();
    }
    
    // Load message history
    await loadMessageHistory();
    
    // Show chat screen
    document.getElementById('welcomeScreen').style.display = 'none';
    document.getElementById('chatScreen').style.display = 'flex';
    document.getElementById('currentRoomName').textContent = state.currentRoom.name;
    document.getElementById('currentRoomDescription').textContent = state.currentRoom.description || '';
    
    // Enable input
    document.getElementById('messageInput').disabled = false;
    document.getElementById('sendBtn').disabled = false;
    document.getElementById('messageInput').focus();
    
    // Render rooms to update active state
    renderRooms();
    
    // Connect WebSocket
    connectWebSocket();
}

function connectWebSocket() {
    const wsUrl = `${WS_BASE}/ws/chat/${state.currentRoom.id}`;
    state.ws = new WebSocket(wsUrl);
    
    state.ws.onopen = () => {
        console.log('WebSocket connected');
        updateConnectionStatus(true);
        state.reconnectAttempts = 0;
        
        // Send authentication
        state.ws.send(JSON.stringify({
            username: state.username
        }));
    };
    
    state.ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleWebSocketMessage(data);
    };
    
    state.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        updateConnectionStatus(false);
    };
    
    state.ws.onclose = () => {
        console.log('WebSocket disconnected');
        updateConnectionStatus(false);
        
        // Attempt reconnection
        if (state.currentRoom && state.reconnectAttempts < state.maxReconnectAttempts) {
            state.reconnectAttempts++;
            setTimeout(() => {
                console.log(`Reconnection attempt ${state.reconnectAttempts}/${state.maxReconnectAttempts}`);
                connectWebSocket();
            }, 2000 * state.reconnectAttempts);
        } else if (state.reconnectAttempts >= state.maxReconnectAttempts) {
            showError('Connection lost. Please refresh the page to reconnect.');
        }
    };
}

function handleWebSocketMessage(data) {
    switch (data.type) {
        case 'connected':
            console.log('Successfully connected as', data.username);
            break;
        
        case 'message':
            addMessage(data);
            break;
        
        case 'system':
            addSystemMessage(data.content);
            break;
        
        case 'users_list':
            updateUsersList(data.users);
            break;
        
        case 'typing':
            updateTypingIndicator(data.users);
            break;
        
        case 'room_deleted':
            showError(data.message);
            leaveRoom();
            break;
        
        case 'error':
            showError(data.content);
            break;
    }
}

function updateConnectionStatus(connected) {
    const statusEl = document.getElementById('connectionStatus');
    const statusText = document.getElementById('statusText');
    
    if (connected) {
        statusEl.className = 'status-connected';
        statusText.textContent = 'Connected';
    } else {
        statusEl.className = 'status-disconnected';
        statusText.textContent = 'Disconnected';
    }
}

// Message Management

async function loadMessageHistory() {
    try {
        const response = await fetch(`${API_BASE}/api/chat/rooms/${state.currentRoom.id}/messages`);
        if (!response.ok) throw new Error('Failed to load messages');
        
        const messages = await response.json();
        state.messages = messages;
        renderMessages();
    } catch (error) {
        console.error('Error loading messages:', error);
        showError('Failed to load message history');
    }
}

function renderMessages() {
    const messagesList = document.getElementById('messagesList');
    
    if (state.messages.length === 0) {
        messagesList.innerHTML = '<div class="system-message">No messages yet. Start the conversation!</div>';
        return;
    }
    
    messagesList.innerHTML = state.messages.map(msg => createMessageHTML(msg)).join('');
    scrollToBottom();
}

function addMessage(message) {
    state.messages.push(message);
    
    const messagesList = document.getElementById('messagesList');
    
    // Remove "no messages" placeholder if exists
    const placeholder = messagesList.querySelector('.system-message');
    if (placeholder) {
        placeholder.remove();
    }
    
    messagesList.insertAdjacentHTML('beforeend', createMessageHTML(message));
    scrollToBottom();
}

function createMessageHTML(message) {
    const isOwn = message.username === state.username;
    const timestamp = new Date(message.timestamp).toLocaleTimeString([], { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
    
    return `
        <div class="message ${isOwn ? 'own' : ''}">
            <div class="message-header">
                <span class="message-username">${escapeHtml(message.username)}</span>
                <span class="message-timestamp">${timestamp}</span>
            </div>
            <div class="message-content">${escapeHtml(message.content)}</div>
        </div>
    `;
}

function addSystemMessage(content) {
    const messagesList = document.getElementById('messagesList');
    messagesList.insertAdjacentHTML('beforeend', `
        <div class="system-message">${escapeHtml(content)}</div>
    `);
    scrollToBottom();
}

function sendMessage() {
    const input = document.getElementById('messageInput');
    const content = input.value.trim();
    
    if (!content || !state.ws || state.ws.readyState !== WebSocket.OPEN) {
        return;
    }
    
    state.ws.send(JSON.stringify({
        type: 'message',
        content: content
    }));
    
    input.value = '';
    
    // Stop typing indicator
    if (state.typingTimeout) {
        clearTimeout(state.typingTimeout);
        state.typingTimeout = null;
    }
    state.ws.send(JSON.stringify({
        type: 'typing',
        is_typing: false
    }));
}

function handleTyping() {
    if (!state.ws || state.ws.readyState !== WebSocket.OPEN) return;
    
    // Send typing indicator
    state.ws.send(JSON.stringify({
        type: 'typing',
        is_typing: true
    }));
    
    // Clear existing timeout
    if (state.typingTimeout) {
        clearTimeout(state.typingTimeout);
    }
    
    // Set timeout to stop typing indicator
    state.typingTimeout = setTimeout(() => {
        if (state.ws && state.ws.readyState === WebSocket.OPEN) {
            state.ws.send(JSON.stringify({
                type: 'typing',
                is_typing: false
            }));
        }
    }, 1000);
}

// User Management

function updateUsersList(users) {
    state.users = users;
    
    const usersList = document.getElementById('usersList');
    const usersCount = document.getElementById('usersCount');
    
    usersCount.textContent = users.length;
    
    usersList.innerHTML = users.map(user => `
        <div class="user-badge">${escapeHtml(user)}</div>
    `).join('');
}

function updateTypingIndicator(typingUsers) {
    const indicator = document.getElementById('typingIndicator');
    const typingText = document.getElementById('typingText');
    
    // Filter out current user
    const others = typingUsers.filter(user => user !== state.username);
    
    if (others.length === 0) {
        indicator.style.display = 'none';
        return;
    }
    
    indicator.style.display = 'flex';
    
    if (others.length === 1) {
        typingText.textContent = `${others[0]} is typing...`;
    } else if (others.length === 2) {
        typingText.textContent = `${others[0]} and ${others[1]} are typing...`;
    } else {
        typingText.textContent = `${others.length} people are typing...`;
    }
}

// Room Exit

function leaveRoom() {
    if (state.ws) {
        state.ws.close();
        state.ws = null;
    }
    
    state.currentRoom = null;
    state.messages = [];
    state.users = [];
    
    document.getElementById('chatScreen').style.display = 'none';
    document.getElementById('welcomeScreen').style.display = 'flex';
    document.getElementById('messageInput').disabled = true;
    document.getElementById('sendBtn').disabled = true;
    
    updateConnectionStatus(false);
    renderRooms();
}

// Utility Functions

function scrollToBottom() {
    const messagesList = document.getElementById('messagesList');
    messagesList.scrollTop = messagesList.scrollHeight;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showError(message) {
    // Simple alert for now, could be replaced with a nicer notification system
    alert(message);
}

function showModalError(elementId, message) {
    const errorEl = document.getElementById(elementId);
    errorEl.textContent = message;
    errorEl.style.display = 'block';
    
    setTimeout(() => {
        errorEl.style.display = 'none';
    }, 5000);
}

