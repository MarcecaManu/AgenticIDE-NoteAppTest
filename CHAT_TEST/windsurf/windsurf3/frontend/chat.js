const API_URL = 'http://localhost:8000';
const WS_URL = 'ws://localhost:8000';

let currentRoom = null;
let websocket = null;
let username = 'Anonymous';
let typingTimeout = null;

async function loadRooms() {
    try {
        const response = await fetch(`${API_URL}/api/chat/rooms`);
        const rooms = await response.json();
        
        const roomsList = document.getElementById('roomsList');
        roomsList.innerHTML = '';
        
        rooms.forEach(room => {
            const roomItem = document.createElement('div');
            roomItem.className = 'room-item';
            if (currentRoom && currentRoom.id === room.id) {
                roomItem.classList.add('active');
            }
            
            roomItem.innerHTML = `
                <span class="room-name">${room.name}</span>
                <button class="delete-room" onclick="deleteRoom('${room.id}', event)">Delete</button>
            `;
            
            roomItem.onclick = (e) => {
                if (!e.target.classList.contains('delete-room')) {
                    joinRoom(room);
                }
            };
            
            roomsList.appendChild(roomItem);
        });
    } catch (error) {
        console.error('Error loading rooms:', error);
    }
}

async function createRoom() {
    const roomNameInput = document.getElementById('roomNameInput');
    const roomName = roomNameInput.value.trim();
    
    if (!roomName) {
        alert('Please enter a room name');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/api/chat/rooms`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name: roomName })
        });
        
        if (response.ok) {
            const room = await response.json();
            roomNameInput.value = '';
            await loadRooms();
            joinRoom(room);
        } else {
            alert('Failed to create room');
        }
    } catch (error) {
        console.error('Error creating room:', error);
        alert('Error creating room');
    }
}

async function deleteRoom(roomId, event) {
    event.stopPropagation();
    
    if (!confirm('Are you sure you want to delete this room?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/api/chat/rooms/${roomId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            if (currentRoom && currentRoom.id === roomId) {
                leaveRoom();
            }
            await loadRooms();
        } else {
            alert('Failed to delete room');
        }
    } catch (error) {
        console.error('Error deleting room:', error);
        alert('Error deleting room');
    }
}

async function joinRoom(room) {
    if (currentRoom && currentRoom.id === room.id) {
        return;
    }
    
    leaveRoom();
    
    currentRoom = room;
    username = document.getElementById('usernameInput').value.trim() || 'Anonymous';
    
    document.getElementById('welcomeScreen').style.display = 'none';
    document.getElementById('chatContent').style.display = 'flex';
    document.getElementById('currentRoomName').textContent = room.name;
    
    await loadMessages(room.id);
    
    connectWebSocket(room.id);
    
    await loadRooms();
}

function leaveRoom() {
    if (websocket) {
        websocket.close();
        websocket = null;
    }
    
    currentRoom = null;
    document.getElementById('welcomeScreen').style.display = 'flex';
    document.getElementById('chatContent').style.display = 'none';
    document.getElementById('messagesContainer').innerHTML = '';
}

async function loadMessages(roomId) {
    try {
        const response = await fetch(`${API_URL}/api/chat/rooms/${roomId}/messages`);
        const messages = await response.json();
        
        const messagesContainer = document.getElementById('messagesContainer');
        messagesContainer.innerHTML = '';
        
        messages.forEach(message => {
            displayMessage(message);
        });
        
        scrollToBottom();
    } catch (error) {
        console.error('Error loading messages:', error);
    }
}

function connectWebSocket(roomId) {
    const wsUrl = `${WS_URL}/ws/chat/${roomId}?username=${encodeURIComponent(username)}`;
    websocket = new WebSocket(wsUrl);
    
    websocket.onopen = () => {
        console.log('WebSocket connected');
        updateConnectionStatus(true);
        document.getElementById('messageInput').disabled = false;
        document.getElementById('sendButton').disabled = false;
    };
    
    websocket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        if (data.type === 'message') {
            displayMessage(data);
            scrollToBottom();
        } else if (data.type === 'user_joined') {
            displaySystemMessage(`${data.username} joined the room`);
            updateOnlineUsers(data.online_users);
            scrollToBottom();
        } else if (data.type === 'user_left') {
            displaySystemMessage(`${data.username} left the room`);
            updateOnlineUsers(data.online_users);
            scrollToBottom();
        } else if (data.type === 'typing') {
            handleTypingIndicator(data);
        }
    };
    
    websocket.onclose = () => {
        console.log('WebSocket disconnected');
        updateConnectionStatus(false);
        document.getElementById('messageInput').disabled = true;
        document.getElementById('sendButton').disabled = true;
        
        setTimeout(() => {
            if (currentRoom) {
                console.log('Attempting to reconnect...');
                connectWebSocket(roomId);
            }
        }, 3000);
    };
    
    websocket.onerror = (error) => {
        console.error('WebSocket error:', error);
    };
}

function displayMessage(message) {
    const messagesContainer = document.getElementById('messagesContainer');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message';
    
    if (message.username === username) {
        messageDiv.classList.add('own');
    }
    
    const timestamp = new Date(message.timestamp).toLocaleTimeString();
    
    messageDiv.innerHTML = `
        <div class="message-header">
            <span class="message-username">${message.username}</span>
            <span class="message-time">${timestamp}</span>
        </div>
        <div class="message-content">${escapeHtml(message.content)}</div>
    `;
    
    messagesContainer.appendChild(messageDiv);
}

function displaySystemMessage(text) {
    const messagesContainer = document.getElementById('messagesContainer');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'system-message';
    messageDiv.textContent = text;
    messagesContainer.appendChild(messageDiv);
}

function sendMessage() {
    const messageInput = document.getElementById('messageInput');
    const content = messageInput.value.trim();
    
    if (!content || !websocket || websocket.readyState !== WebSocket.OPEN) {
        return;
    }
    
    websocket.send(JSON.stringify({
        type: 'message',
        content: content
    }));
    
    messageInput.value = '';
    sendTypingIndicator(false);
}

function handleTyping() {
    if (!websocket || websocket.readyState !== WebSocket.OPEN) {
        return;
    }
    
    sendTypingIndicator(true);
    
    clearTimeout(typingTimeout);
    typingTimeout = setTimeout(() => {
        sendTypingIndicator(false);
    }, 2000);
}

function sendTypingIndicator(isTyping) {
    if (websocket && websocket.readyState === WebSocket.OPEN) {
        websocket.send(JSON.stringify({
            type: 'typing',
            is_typing: isTyping
        }));
    }
}

function handleTypingIndicator(data) {
    if (data.username === username) {
        return;
    }
    
    const typingIndicator = document.getElementById('typingIndicator');
    
    if (data.is_typing) {
        typingIndicator.textContent = `${data.username} is typing...`;
    } else {
        typingIndicator.textContent = '';
    }
}

function updateConnectionStatus(connected) {
    const statusDiv = document.getElementById('connectionStatus');
    if (connected) {
        statusDiv.className = 'connection-status connected';
        statusDiv.textContent = 'Connected';
    } else {
        statusDiv.className = 'connection-status disconnected';
        statusDiv.textContent = 'Disconnected - Reconnecting...';
    }
}

function updateOnlineUsers(users) {
    const onlineUsersDiv = document.getElementById('onlineUsers');
    onlineUsersDiv.textContent = `Online: ${users.length} (${users.join(', ')})`;
}

function scrollToBottom() {
    const messagesContainer = document.getElementById('messagesContainer');
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

document.getElementById('messageInput').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    } else {
        handleTyping();
    }
});

document.getElementById('roomNameInput').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        createRoom();
    }
});

document.getElementById('usernameInput').addEventListener('change', (e) => {
    const newUsername = e.target.value.trim() || 'Anonymous';
    if (currentRoom && newUsername !== username) {
        username = newUsername;
        leaveRoom();
        alert('Username changed. Please rejoin the room.');
    }
});

loadRooms();
setInterval(loadRooms, 30000);
