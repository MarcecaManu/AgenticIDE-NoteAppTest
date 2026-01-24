const API_BASE_URL = 'http://localhost:8000/api/notes';

let notes = [];
let editingNoteId = null;

const elements = {
    notesList: document.getElementById('notesList'),
    searchInput: document.getElementById('searchInput'),
    newNoteBtn: document.getElementById('newNoteBtn'),
    noteModal: document.getElementById('noteModal'),
    modalTitle: document.getElementById('modalTitle'),
    noteTitle: document.getElementById('noteTitle'),
    noteContent: document.getElementById('noteContent'),
    saveBtn: document.getElementById('saveBtn'),
    cancelBtn: document.getElementById('cancelBtn'),
    closeModal: document.getElementById('closeModal'),
    notification: document.getElementById('notification')
};

async function fetchNotes() {
    try {
        const response = await fetch(API_BASE_URL);
        if (!response.ok) throw new Error('Failed to fetch notes');
        notes = await response.json();
        renderNotes();
    } catch (error) {
        showNotification('Error loading notes: ' + error.message, 'error');
    }
}

function renderNotes() {
    const searchTerm = elements.searchInput.value.toLowerCase();
    const filteredNotes = notes.filter(note => 
        note.title.toLowerCase().includes(searchTerm)
    );

    if (filteredNotes.length === 0) {
        elements.notesList.innerHTML = `
            <div class="empty-state">
                <h3>No notes found</h3>
                <p>${searchTerm ? 'Try a different search term' : 'Create your first note to get started!'}</p>
            </div>
        `;
        return;
    }

    elements.notesList.innerHTML = filteredNotes.map(note => `
        <div class="note-card" data-id="${note.id}">
            <div class="note-header">
                <h3 class="note-title">${escapeHtml(note.title)}</h3>
                <div class="note-actions">
                    <button class="btn btn-edit" onclick="editNote(${note.id})">Edit</button>
                    <button class="btn btn-danger" onclick="deleteNote(${note.id})">Delete</button>
                </div>
            </div>
            <div class="note-content">${escapeHtml(note.content)}</div>
            <div class="note-meta">
                <div>Created: ${formatDate(note.createdAt)}</div>
                <div>Updated: ${formatDate(note.updatedAt)}</div>
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
    return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function openModal(isEdit = false, note = null) {
    editingNoteId = isEdit ? note.id : null;
    elements.modalTitle.textContent = isEdit ? 'Edit Note' : 'Create Note';
    elements.noteTitle.value = isEdit ? note.title : '';
    elements.noteContent.value = isEdit ? note.content : '';
    elements.noteModal.classList.add('active');
}

function closeModalHandler() {
    elements.noteModal.classList.remove('active');
    editingNoteId = null;
    elements.noteTitle.value = '';
    elements.noteContent.value = '';
}

async function saveNote() {
    const title = elements.noteTitle.value.trim();
    const content = elements.noteContent.value.trim();

    if (!title || !content) {
        showNotification('Please fill in both title and content', 'error');
        return;
    }

    try {
        if (editingNoteId) {
            const response = await fetch(`${API_BASE_URL}/${editingNoteId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title, content })
            });
            if (!response.ok) throw new Error('Failed to update note');
            showNotification('Note updated successfully!');
        } else {
            const response = await fetch(API_BASE_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title, content })
            });
            if (!response.ok) throw new Error('Failed to create note');
            showNotification('Note created successfully!');
        }
        
        closeModalHandler();
        await fetchNotes();
    } catch (error) {
        showNotification('Error saving note: ' + error.message, 'error');
    }
}

async function editNote(id) {
    const note = notes.find(n => n.id === id);
    if (note) {
        openModal(true, note);
    }
}

async function deleteNote(id) {
    if (!confirm('Are you sure you want to delete this note?')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/${id}`, {
            method: 'DELETE'
        });
        if (!response.ok) throw new Error('Failed to delete note');
        showNotification('Note deleted successfully!');
        await fetchNotes();
    } catch (error) {
        showNotification('Error deleting note: ' + error.message, 'error');
    }
}

function showNotification(message, type = 'success') {
    elements.notification.textContent = message;
    elements.notification.className = `notification ${type} show`;
    
    setTimeout(() => {
        elements.notification.classList.remove('show');
    }, 3000);
}

elements.searchInput.addEventListener('input', renderNotes);
elements.newNoteBtn.addEventListener('click', () => openModal(false));
elements.saveBtn.addEventListener('click', saveNote);
elements.cancelBtn.addEventListener('click', closeModalHandler);
elements.closeModal.addEventListener('click', closeModalHandler);

elements.noteModal.addEventListener('click', (e) => {
    if (e.target === elements.noteModal) {
        closeModalHandler();
    }
});

fetchNotes();
