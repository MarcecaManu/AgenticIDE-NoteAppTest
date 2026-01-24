/**
 * Real-time Chat Application - Frontend JavaScript
 */

const API_BASE = 'http://localhost:8000';
const WS_BASE = 'ws://localhost:8000';

// Application state
const state = {
    username: null,
    currentRoom: null,
    websocket: null,
    rooms: [],
    messages: [],
    users: [],
    typingTimeout: null
};

// DOM elements
const elements = {
    loginScreen: document.getElementById('login-screen'),
    roomScreen: document.getElementById('room-screen'),
    chatScreen: document.getElementById('chat-screen'),
    usernameInput: document.getElementById('username-input'),
    loginBtn: document.getElementById('login-btn'),
    currentUsername: document.getElementById('current-username'),
    logoutBtn: document.getElementById('logout-btn'),
    roomNameInput: document.getElementById('room-name-input'),
    createRoomBtn: document.getElementById('create-room-btn'),
    roomsContainer: document.getElementById('rooms-container'),
    backBtn: document.getElementById('back-btn'),
    deleteRoomBtn: document.getElementById('delete-room-btn'),
    roomTitle: document.getElementById('room-title'),
    connectionIndicator: document.getElementById('connection-indicator'),
    connectionText: document.getElementById('connection-text'),
    messagesContainer: document.getElementById('messages-container'),
    typingIndicator: document.getElementById('typing-indicator'),
    usersList: document.getElementById('users-list'),
    userCount: document.getElementById('user-count'),
    messageInput: document.getElementById('message-input'),
    sendBtn: document.getElementById('send-btn')
};

// Initialize application
function init() {
    setupEventListeners();
    showScreen('login');
}

// Setup event listeners
function setupEventListeners() {
    elements.loginBtn.addEventListener('click', handleLogin);
    elements.usernameInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleLogin();
    });
    
    elements.logoutBtn.addEventListener('click', handleLogout);
    elements.createRoomBtn.addEventListener('click', handleCreateRoom);
    elements.roomNameInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleCreateRoom();
    });
    
    elements.backBtn.addEventListener('click', handleBackToRooms);
    elements.deleteRoomBtn.addEventListener('click', handleDeleteRoom);
    
    elements.sendBtn.addEventListener('click', handleSendMessage);
    elements.messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleSendMessage();
    });
    
    elements.messageInput.addEventListener('input', handleTyping);
}

// Screen management
function showScreen(screen) {
    elements.loginScreen.classList.add('hidden');
    elements.roomScreen.classList.add('hidden');
    elements.chatScreen.classList.add('hidden');
    
    if (screen === 'login') {
        elements.loginScreen.classList.remove('hidden');
    } else if (screen === 'rooms') {
        elements.roomScreen.classList.remove('hidden');
        loadRooms();
    } else if (screen === 'chat') {
        elements.chatScreen.classList.remove('hidden');
    }
}

// Login handler
function handleLogin() {
    const username = elements.usernameInput.value.trim();
    if (!username) {
        alert('Please enter a username');
        return;
    }
    
    state.username = username;
    elements.currentUsername.textContent = username;
    showScreen('rooms');
}

// Logout handler
function handleLogout() {
    disconnectWebSocket();
    state.username = null;
    state.currentRoom = null;
    elements.usernameInput.value = '';
    showScreen('login');
}

// Load rooms
async function loadRooms() {
    try {
        const response = await fetch(`${API_BASE}/api/chat/rooms`);
        if (!response.ok) throw new Error('Failed to load rooms');
        
        state.rooms = await response.json();
        renderRooms();
    } catch (error) {
        console.error('Error loading rooms:', error);
        elements.roomsContainer.innerHTML = '<p class="loading">Failed to load rooms. Please try again.</p>';
    }
}

// Render rooms
function renderRooms() {
    if (state.rooms.length === 0) {
        elements.roomsContainer.innerHTML = '<p class="loading">No rooms available. Create one to get started!</p>';
        return;
    }
    
    elements.roomsContainer.innerHTML = state.rooms.map(room => `
        <div class="room-item" onclick="joinRoom('${room.id}', '${room.name}')">
            <h3>${escapeHtml(room.name)}</h3>
            <p>Created: ${formatDate(room.created_at)}</p>
        </div>
    `).join('');
}

// Create room
async function handleCreateRoom() {
    const roomName = elements.roomNameInput.value.trim();
    if (!roomName) {
        alert('Please enter a room name');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/api/chat/rooms`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name: roomName })
        });
        
        if (!response.ok) throw new Error('Failed to create room');
        
        const room = await response.json();
        elements.roomNameInput.value = '';
        await loadRooms();
        joinRoom(room.id, room.name);
    } catch (error) {
        console.error('Error creating room:', error);
        alert('Failed to create room. Please try again.');
    }
}

// Delete room
async function handleDeleteRoom() {
    if (!confirm('Are you sure you want to delete this room? This action cannot be undone.')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/api/chat/rooms/${state.currentRoom.id}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) throw new Error('Failed to delete room');
        
        disconnectWebSocket();
        showScreen('rooms');
    } catch (error) {
        console.error('Error deleting room:', error);
        alert('Failed to delete room. Please try again.');
    }
}

// Join room
async function joinRoom(roomId, roomName) {
    state.currentRoom = { id: roomId, name: roomName };
    elements.roomTitle.textContent = roomName;
    showScreen('chat');
    
    // Load message history
    await loadMessages(roomId);
    
    // Connect WebSocket
    connectWebSocket(roomId);
}

// Load messages
async function loadMessages(roomId) {
    try {
        const response = await fetch(`${API_BASE}/api/chat/rooms/${roomId}/messages`);
        if (!response.ok) throw new Error('Failed to load messages');
        
        state.messages = await response.json();
        renderMessages();
    } catch (error) {
        console.error('Error loading messages:', error);
        elements.messagesContainer.innerHTML = '<p class="system-message">Failed to load message history.</p>';
    }
}

// Render messages
function renderMessages() {
    elements.messagesContainer.innerHTML = state.messages.map(msg => {
        const isOwn = msg.username === state.username;
        return `
            <div class="message ${isOwn ? 'own' : 'other'}">
                <div class="message-header">
                    <span class="message-username">${escapeHtml(msg.username)}</span>
                    <span class="message-time">${formatTime(msg.timestamp)}</span>
                </div>
                <div class="message-content">${escapeHtml(msg.content)}</div>
            </div>
        `;
    }).join('');
    
    scrollToBottom();
}

// Connect WebSocket
function connectWebSocket(roomId) {
    const wsUrl = `${WS_BASE}/ws/chat/${roomId}?username=${encodeURIComponent(state.username)}`;
    
    state.websocket = new WebSocket(wsUrl);
    
    state.websocket.onopen = () => {
        console.log('WebSocket connected');
        updateConnectionStatus(true);
    };
    
    state.websocket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleWebSocketMessage(data);
    };
    
    state.websocket.onerror = (error) => {
        console.error('WebSocket error:', error);
        updateConnectionStatus(false);
    };
    
    state.websocket.onclose = () => {
        console.log('WebSocket disconnected');
        updateConnectionStatus(false);
        
        // Attempt to reconnect after 3 seconds if still on chat screen
        setTimeout(() => {
            if (state.currentRoom && !elements.chatScreen.classList.contains('hidden')) {
                console.log('Attempting to reconnect...');
                connectWebSocket(state.currentRoom.id);
            }
        }, 3000);
    };
}

// Disconnect WebSocket
function disconnectWebSocket() {
    if (state.websocket) {
        state.websocket.close();
        state.websocket = null;
    }
}

// Handle WebSocket messages
function handleWebSocketMessage(data) {
    switch (data.type) {
        case 'message':
            state.messages.push(data.message);
            renderMessages();
            break;
        
        case 'join':
            addSystemMessage(`${data.username} joined the room`);
            break;
        
        case 'leave':
            addSystemMessage(`${data.username} left the room`);
            break;
        
        case 'user_list':
            state.users = data.users;
            renderUsers();
            break;
        
        case 'typing':
            if (data.username !== state.username) {
                showTypingIndicator(data.username);
            }
            break;
        
        case 'room_deleted':
            alert('This room has been deleted');
            disconnectWebSocket();
            showScreen('rooms');
            break;
    }
}

// Add system message
function addSystemMessage(text) {
    const messageHtml = `<div class="system-message">${escapeHtml(text)}</div>`;
    elements.messagesContainer.insertAdjacentHTML('beforeend', messageHtml);
    scrollToBottom();
}

// Render users
function renderUsers() {
    elements.userCount.textContent = state.users.length;
    elements.usersList.innerHTML = state.users.map(username => `
        <div class="user-item">${escapeHtml(username)}</div>
    `).join('');
}

// Update connection status
function updateConnectionStatus(connected) {
    if (connected) {
        elements.connectionIndicator.classList.remove('disconnected');
        elements.connectionIndicator.classList.add('connected');
        elements.connectionText.textContent = 'Connected';
    } else {
        elements.connectionIndicator.classList.remove('connected');
        elements.connectionIndicator.classList.add('disconnected');
        elements.connectionText.textContent = 'Disconnected';
    }
}

// Handle send message
function handleSendMessage() {
    const content = elements.messageInput.value.trim();
    if (!content || !state.websocket) return;
    
    try {
        state.websocket.send(JSON.stringify({
            type: 'message',
            content: content
        }));
        
        elements.messageInput.value = '';
    } catch (error) {
        console.error('Error sending message:', error);
        alert('Failed to send message. Please check your connection.');
    }
}

// Handle typing
function handleTyping() {
    if (!state.websocket) return;
    
    // Clear existing timeout
    if (state.typingTimeout) {
        clearTimeout(state.typingTimeout);
    }
    
    // Send typing indicator
    try {
        state.websocket.send(JSON.stringify({
            type: 'typing'
        }));
    } catch (error) {
        console.error('Error sending typing indicator:', error);
    }
    
    // Set timeout to clear typing indicator
    state.typingTimeout = setTimeout(() => {
        state.typingTimeout = null;
    }, 1000);
}

// Show typing indicator
function showTypingIndicator(username) {
    elements.typingIndicator.textContent = `${username} is typing...`;
    elements.typingIndicator.classList.remove('hidden');
    
    // Hide after 2 seconds
    setTimeout(() => {
        elements.typingIndicator.classList.add('hidden');
    }, 2000);
}

// Handle back to rooms
function handleBackToRooms() {
    disconnectWebSocket();
    state.currentRoom = null;
    state.messages = [];
    state.users = [];
    showScreen('rooms');
}

// Utility functions
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatDate(isoString) {
    const date = new Date(isoString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

function formatTime(isoString) {
    const date = new Date(isoString);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function scrollToBottom() {
    elements.messagesContainer.scrollTop = elements.messagesContainer.scrollHeight;
}

// Initialize app on load
window.addEventListener('DOMContentLoaded', init);

