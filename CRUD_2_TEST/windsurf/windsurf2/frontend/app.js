const API_BASE_URL = 'http://localhost:8000/api/notes';

let allNotes = [];

async function fetchNotes() {
    try {
        const response = await fetch(API_BASE_URL + '/');
        if (!response.ok) {
            throw new Error('Failed to fetch notes');
        }
        allNotes = await response.json();
        renderNotes(allNotes);
    } catch (error) {
        console.error('Error fetching notes:', error);
        showMessage('createMessage', 'Failed to load notes. Please try again.', 'error');
    }
}

function renderNotes(notes) {
    const notesGrid = document.getElementById('notesGrid');
    
    if (notes.length === 0) {
        notesGrid.innerHTML = `
            <div class="empty-state" style="grid-column: 1 / -1;">
                <h2>No notes found</h2>
                <p>Create your first note to get started!</p>
            </div>
        `;
        return;
    }
    
    notesGrid.innerHTML = notes.map(note => `
        <div class="note-card" data-note-id="${note.id}">
            <h3>${escapeHtml(note.title)}</h3>
            <p>${escapeHtml(note.content)}</p>
            <div class="note-meta">
                Created: ${formatDate(note.createdAt)}<br>
                Updated: ${formatDate(note.updatedAt)}
            </div>
            <div class="note-actions">
                <button class="btn btn-edit" onclick="openEditModal(${note.id})">Edit</button>
                <button class="btn btn-danger" onclick="deleteNote(${note.id})">Delete</button>
            </div>
        </div>
    `).join('');
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString();
}

document.getElementById('createNoteForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const title = document.getElementById('noteTitle').value.trim();
    const content = document.getElementById('noteContent').value.trim();
    
    if (!title || !content) {
        showMessage('createMessage', 'Please fill in all fields', 'error');
        return;
    }
    
    try {
        const response = await fetch(API_BASE_URL + '/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ title, content }),
        });
        
        if (!response.ok) {
            throw new Error('Failed to create note');
        }
        
        const newNote = await response.json();
        showMessage('createMessage', 'Note created successfully!', 'success');
        
        document.getElementById('noteTitle').value = '';
        document.getElementById('noteContent').value = '';
        
        await fetchNotes();
    } catch (error) {
        console.error('Error creating note:', error);
        showMessage('createMessage', 'Failed to create note. Please try again.', 'error');
    }
});

async function openEditModal(noteId) {
    try {
        const response = await fetch(`${API_BASE_URL}/${noteId}`);
        if (!response.ok) {
            throw new Error('Failed to fetch note');
        }
        
        const note = await response.json();
        
        document.getElementById('editNoteId').value = note.id;
        document.getElementById('editNoteTitle').value = note.title;
        document.getElementById('editNoteContent').value = note.content;
        
        document.getElementById('editModal').classList.add('active');
    } catch (error) {
        console.error('Error fetching note:', error);
        showMessage('createMessage', 'Failed to load note for editing.', 'error');
    }
}

function closeEditModal() {
    document.getElementById('editModal').classList.remove('active');
    document.getElementById('editMessage').classList.remove('show');
}

document.getElementById('editNoteForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const noteId = document.getElementById('editNoteId').value;
    const title = document.getElementById('editNoteTitle').value.trim();
    const content = document.getElementById('editNoteContent').value.trim();
    
    if (!title || !content) {
        showMessage('editMessage', 'Please fill in all fields', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/${noteId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ title, content }),
        });
        
        if (!response.ok) {
            throw new Error('Failed to update note');
        }
        
        showMessage('editMessage', 'Note updated successfully!', 'success');
        
        setTimeout(() => {
            closeEditModal();
            fetchNotes();
        }, 1000);
    } catch (error) {
        console.error('Error updating note:', error);
        showMessage('editMessage', 'Failed to update note. Please try again.', 'error');
    }
});

async function deleteNote(noteId) {
    if (!confirm('Are you sure you want to delete this note?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/${noteId}`, {
            method: 'DELETE',
        });
        
        if (!response.ok) {
            throw new Error('Failed to delete note');
        }
        
        showMessage('createMessage', 'Note deleted successfully!', 'success');
        await fetchNotes();
    } catch (error) {
        console.error('Error deleting note:', error);
        showMessage('createMessage', 'Failed to delete note. Please try again.', 'error');
    }
}

document.getElementById('searchInput').addEventListener('input', (e) => {
    const searchTerm = e.target.value.toLowerCase().trim();
    
    if (searchTerm === '') {
        renderNotes(allNotes);
    } else {
        const filteredNotes = allNotes.filter(note => 
            note.title.toLowerCase().includes(searchTerm)
        );
        renderNotes(filteredNotes);
    }
});

function showMessage(elementId, message, type) {
    const messageElement = document.getElementById(elementId);
    messageElement.textContent = message;
    messageElement.className = `message ${type} show`;
    
    setTimeout(() => {
        messageElement.classList.remove('show');
    }, 3000);
}

document.getElementById('editModal').addEventListener('click', (e) => {
    if (e.target.id === 'editModal') {
        closeEditModal();
    }
});

fetchNotes();
