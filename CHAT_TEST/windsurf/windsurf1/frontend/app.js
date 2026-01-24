const API_BASE_URL = 'http://localhost:8000';
const WS_BASE_URL = 'ws://localhost:8000';

let username = '';
let currentRoomId = null;
let websocket = null;
let typingTimeout = null;

const screens = {
    login: document.getElementById('loginScreen'),
    room: document.getElementById('roomScreen'),
    chat: document.getElementById('chatScreen')
};

const elements = {
    usernameInput: document.getElementById('usernameInput'),
    setUsernameBtn: document.getElementById('setUsernameBtn'),
    newRoomInput: document.getElementById('newRoomInput'),
    createRoomBtn: document.getElementById('createRoomBtn'),
    refreshRoomsBtn: document.getElementById('refreshRoomsBtn'),
    roomList: document.getElementById('roomList'),
    currentRoomName: document.getElementById('currentRoomName'),
    leaveRoomBtn: document.getElementById('leaveRoomBtn'),
    chatMessages: document.getElementById('chatMessages'),
    messageInput: document.getElementById('messageInput'),
    sendMessageBtn: document.getElementById('sendMessageBtn'),
    userList: document.getElementById('userList'),
    userCount: document.getElementById('userCount'),
    typingIndicator: document.getElementById('typingIndicator'),
    connectionStatus: document.getElementById('connectionStatus'),
    errorToast: document.getElementById('errorToast')
};

function showScreen(screenName) {
    Object.values(screens).forEach(screen => screen.classList.remove('active'));
    screens[screenName].classList.add('active');
}

function showError(message) {
    elements.errorToast.textContent = message;
    elements.errorToast.classList.add('show');
    setTimeout(() => {
        elements.errorToast.classList.remove('show');
    }, 3000);
}

function updateConnectionStatus(connected) {
    const statusDot = elements.connectionStatus.querySelector('.status-dot');
    const statusText = elements.connectionStatus.querySelector('.status-text');
    
    if (connected) {
        statusDot.classList.add('connected');
        statusText.textContent = 'Connected';
    } else {
        statusDot.classList.remove('connected');
        statusText.textContent = 'Disconnected';
    }
}

async function fetchRooms() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/chat/rooms`);
        if (!response.ok) throw new Error('Failed to fetch rooms');
        const rooms = await response.json();
        displayRooms(rooms);
    } catch (error) {
        showError('Failed to load chat rooms');
        console.error('Error fetching rooms:', error);
    }
}

function displayRooms(rooms) {
    if (rooms.length === 0) {
        elements.roomList.innerHTML = '<div class="empty-state"><p>No chat rooms yet. Create one to get started!</p></div>';
        return;
    }
    
    elements.roomList.innerHTML = rooms.map(room => `
        <div class="room-card" data-room-id="${room.id}">
            <button class="delete-room" data-room-id="${room.id}" title="Delete room">×</button>
            <h3>${escapeHtml(room.name)}</h3>
            <p>Created: ${new Date(room.created_at).toLocaleDateString()}</p>
        </div>
    `).join('');
    
    document.querySelectorAll('.room-card').forEach(card => {
        card.addEventListener('click', (e) => {
            if (!e.target.classList.contains('delete-room')) {
                const roomId = card.dataset.roomId;
                const roomName = card.querySelector('h3').textContent;
                joinRoom(roomId, roomName);
            }
        });
    });
    
    document.querySelectorAll('.delete-room').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.stopPropagation();
            const roomId = btn.dataset.roomId;
            if (confirm('Are you sure you want to delete this room?')) {
                await deleteRoom(roomId);
            }
        });
    });
}

async function createRoom() {
    const roomName = elements.newRoomInput.value.trim();
    if (!roomName) {
        showError('Please enter a room name');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/chat/rooms`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: roomName })
        });
        
        if (!response.ok) throw new Error('Failed to create room');
        
        elements.newRoomInput.value = '';
        await fetchRooms();
    } catch (error) {
        showError('Failed to create room');
        console.error('Error creating room:', error);
    }
}

async function deleteRoom(roomId) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/chat/rooms/${roomId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) throw new Error('Failed to delete room');
        
        await fetchRooms();
    } catch (error) {
        showError('Failed to delete room');
        console.error('Error deleting room:', error);
    }
}

async function joinRoom(roomId, roomName) {
    currentRoomId = roomId;
    elements.currentRoomName.textContent = roomName;
    showScreen('chat');
    
    await loadMessageHistory(roomId);
    connectWebSocket(roomId);
}

async function loadMessageHistory(roomId) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/chat/rooms/${roomId}/messages`);
        if (!response.ok) throw new Error('Failed to load messages');
        
        const messages = await response.json();
        elements.chatMessages.innerHTML = '';
        
        messages.forEach(message => {
            displayMessage(message);
        });
        
        scrollToBottom();
    } catch (error) {
        showError('Failed to load message history');
        console.error('Error loading messages:', error);
    }
}

function connectWebSocket(roomId) {
    if (websocket) {
        websocket.close();
    }
    
    const wsUrl = `${WS_BASE_URL}/ws/chat/${roomId}?username=${encodeURIComponent(username)}`;
    websocket = new WebSocket(wsUrl);
    
    websocket.onopen = () => {
        updateConnectionStatus(true);
    };
    
    websocket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        if (data.type === 'message') {
            displayMessage(data.message);
            scrollToBottom();
        } else if (data.type === 'system') {
            displaySystemMessage(data.content, data.timestamp);
            scrollToBottom();
        } else if (data.type === 'user_list') {
            updateUserList(data.users);
        } else if (data.type === 'typing') {
            updateTypingIndicator(data.users);
        }
    };
    
    websocket.onerror = (error) => {
        console.error('WebSocket error:', error);
        showError('Connection error occurred');
    };
    
    websocket.onclose = () => {
        updateConnectionStatus(false);
        setTimeout(() => {
            if (currentRoomId === roomId) {
                showError('Connection lost. Attempting to reconnect...');
                connectWebSocket(roomId);
            }
        }, 3000);
    };
}

function displayMessage(message) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message user';
    
    const time = new Date(message.timestamp).toLocaleTimeString([], { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
    
    messageDiv.innerHTML = `
        <div class="message-header">
            <span class="message-username">${escapeHtml(message.username)}</span>
            <span class="message-time">${time}</span>
        </div>
        <div class="message-content">${escapeHtml(message.content)}</div>
    `;
    
    elements.chatMessages.appendChild(messageDiv);
}

function displaySystemMessage(content, timestamp) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message system';
    messageDiv.textContent = content;
    elements.chatMessages.appendChild(messageDiv);
}

function updateUserList(users) {
    elements.userCount.textContent = users.length;
    elements.userList.innerHTML = users.map(user => 
        `<span class="user-badge">${escapeHtml(user)}</span>`
    ).join('');
}

function updateTypingIndicator(typingUsers) {
    const filteredUsers = typingUsers.filter(user => user !== username);
    
    if (filteredUsers.length === 0) {
        elements.typingIndicator.textContent = '';
    } else if (filteredUsers.length === 1) {
        elements.typingIndicator.textContent = `${filteredUsers[0]} is typing...`;
    } else if (filteredUsers.length === 2) {
        elements.typingIndicator.textContent = `${filteredUsers[0]} and ${filteredUsers[1]} are typing...`;
    } else {
        elements.typingIndicator.textContent = `${filteredUsers.length} people are typing...`;
    }
}

function sendMessage() {
    const content = elements.messageInput.value.trim();
    if (!content || !websocket || websocket.readyState !== WebSocket.OPEN) {
        return;
    }
    
    websocket.send(JSON.stringify({
        type: 'message',
        content: content
    }));
    
    elements.messageInput.value = '';
    sendTypingStatus(false);
}

function sendTypingStatus(isTyping) {
    if (websocket && websocket.readyState === WebSocket.OPEN) {
        websocket.send(JSON.stringify({
            type: 'typing',
            is_typing: isTyping
        }));
    }
}

function leaveRoom() {
    if (websocket) {
        websocket.close();
        websocket = null;
    }
    
    currentRoomId = null;
    elements.chatMessages.innerHTML = '';
    elements.userList.innerHTML = '';
    elements.userCount.textContent = '0';
    elements.typingIndicator.textContent = '';
    updateConnectionStatus(false);
    
    showScreen('room');
    fetchRooms();
}

function scrollToBottom() {
    elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

elements.setUsernameBtn.addEventListener('click', () => {
    const inputUsername = elements.usernameInput.value.trim();
    if (!inputUsername) {
        showError('Please enter a username');
        return;
    }
    
    username = inputUsername;
    showScreen('room');
    fetchRooms();
});

elements.usernameInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        elements.setUsernameBtn.click();
    }
});

elements.createRoomBtn.addEventListener('click', createRoom);

elements.newRoomInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        createRoom();
    }
});

elements.refreshRoomsBtn.addEventListener('click', fetchRooms);

elements.leaveRoomBtn.addEventListener('click', leaveRoom);

elements.sendMessageBtn.addEventListener('click', sendMessage);

elements.messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

elements.messageInput.addEventListener('input', () => {
    clearTimeout(typingTimeout);
    sendTypingStatus(true);
    
    typingTimeout = setTimeout(() => {
        sendTypingStatus(false);
    }, 1000);
});

window.addEventListener('beforeunload', () => {
    if (websocket) {
        websocket.close();
    }
});
