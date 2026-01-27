const API_BASE = 'http://localhost:8000';
const WS_BASE = 'ws://localhost:8000';

let currentRoom = null;
let websocket = null;
let currentUsername = 'User';
let typingTimeout = null;
let onlineUsers = [];
let intentionalDisconnect = false;

const elements = {
    usernameInput: document.getElementById('usernameInput'),
    roomsList: document.getElementById('roomsList'),
    createRoomBtn: document.getElementById('createRoomBtn'),
    chatHeader: document.getElementById('chatHeader'),
    chatTitle: document.getElementById('chatTitle'),
    onlineUsers: document.getElementById('onlineUsers'),
    onlineCount: document.getElementById('onlineCount'),
    messagesContainer: document.getElementById('messagesContainer'),
    messageInputContainer: document.getElementById('messageInputContainer'),
    messageInput: document.getElementById('messageInput'),
    sendBtn: document.getElementById('sendBtn'),
    typingIndicator: document.getElementById('typingIndicator'),
    connectionStatus: document.getElementById('connectionStatus'),
    createRoomModal: document.getElementById('createRoomModal'),
    roomNameInput: document.getElementById('roomNameInput'),
    cancelBtn: document.getElementById('cancelBtn'),
    confirmCreateBtn: document.getElementById('confirmCreateBtn')
};

async function loadRooms() {
    try {
        const response = await fetch(`${API_BASE}/api/chat/rooms`);
        const rooms = await response.json();
        
        elements.roomsList.innerHTML = '';
        
        if (rooms.length === 0) {
            elements.roomsList.innerHTML = '<div style="padding: 20px; text-align: center; color: #999;">No rooms yet. Create one!</div>';
            return;
        }
        
        rooms.forEach(room => {
            const roomElement = document.createElement('div');
            roomElement.className = 'room-item';
            if (currentRoom && currentRoom.id === room.id) {
                roomElement.classList.add('active');
            }
            
            const date = new Date(room.created_at);
            const timeStr = date.toLocaleString();
            
            roomElement.innerHTML = `
                <div class="room-name">${escapeHtml(room.name)}</div>
                <div class="room-time">${timeStr}</div>
            `;
            
            roomElement.addEventListener('click', () => joinRoom(room));
            elements.roomsList.appendChild(roomElement);
        });
    } catch (error) {
        console.error('Failed to load rooms:', error);
        showConnectionStatus('Failed to load rooms', 'disconnected');
    }
}

async function createRoom(name) {
    try {
        const response = await fetch(`${API_BASE}/api/chat/rooms`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name })
        });
        
        if (!response.ok) {
            throw new Error('Failed to create room');
        }
        
        const room = await response.json();
        await loadRooms();
        joinRoom(room);
    } catch (error) {
        console.error('Failed to create room:', error);
        alert('Failed to create room. Please try again.');
    }
}

async function joinRoom(room) {
    if (websocket) {
        intentionalDisconnect = true;
        websocket.close();
    }
    
    currentRoom = room;
    elements.chatTitle.textContent = room.name;
    elements.chatHeader.style.display = 'flex';
    elements.messageInputContainer.style.display = 'block';
    elements.messagesContainer.innerHTML = '';
    
    await loadRooms();
    
    try {
        const response = await fetch(`${API_BASE}/api/chat/rooms/${room.id}/messages`);
        const messages = await response.json();
        
        messages.forEach(message => {
            displayMessage(message);
        });
        
        scrollToBottom();
    } catch (error) {
        console.error('Failed to load messages:', error);
    }
    
    connectWebSocket(room.id);
}

function connectWebSocket(roomId) {
    intentionalDisconnect = false;
    showConnectionStatus('Connecting...', '');
    
    const username = elements.usernameInput.value.trim() || 'User';
    currentUsername = username;
    
    websocket = new WebSocket(`${WS_BASE}/ws/chat/${roomId}?username=${encodeURIComponent(username)}`);
    
    websocket.onopen = () => {
        showConnectionStatus('Connected', 'connected');
        setTimeout(() => {
            elements.connectionStatus.style.display = 'none';
        }, 2000);
    };
    
    websocket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        if (data.type === 'message') {
            displayMessage(data);
            scrollToBottom();
        } else if (data.type === 'user_joined') {
            displaySystemMessage(`${data.username} joined the room`);
            onlineUsers = data.online_users;
            updateOnlineUsers();
            scrollToBottom();
        } else if (data.type === 'user_left') {
            displaySystemMessage(`${data.username} left the room`);
            onlineUsers = data.online_users;
            updateOnlineUsers();
            scrollToBottom();
        } else if (data.type === 'typing') {
            if (data.username !== currentUsername) {
                showTypingIndicator(data.username, data.is_typing);
            }
        }
    };
    
    websocket.onerror = (error) => {
        console.error('WebSocket error:', error);
        showConnectionStatus('Connection error', 'disconnected');
    };
    
    websocket.onclose = () => {
        if (intentionalDisconnect) {
            intentionalDisconnect = false;
            return;
        }
        
        showConnectionStatus('Disconnected', 'disconnected');
        setTimeout(() => {
            if (currentRoom && !intentionalDisconnect) {
                connectWebSocket(currentRoom.id);
            }
        }, 3000);
    };
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

function displayMessage(message) {
    const messageElement = document.createElement('div');
    messageElement.className = 'message';
    
    if (message.username === currentUsername) {
        messageElement.classList.add('own');
    }
    
    const date = new Date(message.timestamp);
    const timeStr = date.toLocaleTimeString();
    
    messageElement.innerHTML = `
        <div class="message-header">
            <span class="message-username">${escapeHtml(message.username)}</span>
            <span class="message-time">${timeStr}</span>
        </div>
        <div class="message-content">${escapeHtml(message.content)}</div>
    `;
    
    elements.messagesContainer.appendChild(messageElement);
}

function displaySystemMessage(text) {
    const messageElement = document.createElement('div');
    messageElement.className = 'system-message';
    messageElement.textContent = text;
    elements.messagesContainer.appendChild(messageElement);
}

function showTypingIndicator(username, isTyping) {
    if (isTyping) {
        elements.typingIndicator.textContent = `${username} is typing...`;
        elements.typingIndicator.style.display = 'block';
    } else {
        elements.typingIndicator.style.display = 'none';
    }
}

function updateOnlineUsers() {
    const count = onlineUsers.length;
    elements.onlineCount.textContent = `${count} online`;
}

function showConnectionStatus(message, status) {
    elements.connectionStatus.textContent = message;
    elements.connectionStatus.className = `connection-status ${status}`;
    elements.connectionStatus.style.display = 'block';
}

function scrollToBottom() {
    elements.messagesContainer.scrollTop = elements.messagesContainer.scrollHeight;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

elements.createRoomBtn.addEventListener('click', () => {
    elements.createRoomModal.classList.add('active');
    elements.roomNameInput.value = '';
    elements.roomNameInput.focus();
});

elements.cancelBtn.addEventListener('click', () => {
    elements.createRoomModal.classList.remove('active');
});

elements.confirmCreateBtn.addEventListener('click', () => {
    const name = elements.roomNameInput.value.trim();
    if (name) {
        createRoom(name);
        elements.createRoomModal.classList.remove('active');
    }
});

elements.roomNameInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        elements.confirmCreateBtn.click();
    }
});

elements.sendBtn.addEventListener('click', sendMessage);

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

elements.usernameInput.addEventListener('change', () => {
    const newUsername = elements.usernameInput.value.trim() || 'User';
    if (newUsername !== currentUsername && currentRoom) {
        currentUsername = newUsername;
        if (websocket) {
            intentionalDisconnect = true;
            websocket.close();
        }
        connectWebSocket(currentRoom.id);
    }
});

loadRooms();
setInterval(loadRooms, 30000);
