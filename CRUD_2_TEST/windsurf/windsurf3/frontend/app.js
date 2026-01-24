const API_BASE_URL = 'http://localhost:8000/api/notes';

let notes = [];
let currentNoteId = null;
let isEditMode = false;

const elements = {
    notesList: document.getElementById('notesList'),
    noteModal: document.getElementById('noteModal'),
    modalTitle: document.getElementById('modalTitle'),
    noteTitle: document.getElementById('noteTitle'),
    noteContent: document.getElementById('noteContent'),
    newNoteBtn: document.getElementById('newNoteBtn'),
    closeModal: document.getElementById('closeModal'),
    cancelBtn: document.getElementById('cancelBtn'),
    saveBtn: document.getElementById('saveBtn'),
    searchInput: document.getElementById('searchInput'),
    notification: document.getElementById('notification')
};

async function fetchNotes() {
    try {
        const response = await fetch(API_BASE_URL);
        if (!response.ok) throw new Error('Failed to fetch notes');
        notes = await response.json();
        renderNotes();
    } catch (error) {
        showNotification('Error loading notes', 'error');
        console.error('Error:', error);
    }
}

function renderNotes(filter = '') {
    const filteredNotes = filter
        ? notes.filter(note => note.title.toLowerCase().includes(filter.toLowerCase()))
        : notes;

    if (filteredNotes.length === 0) {
        elements.notesList.innerHTML = `
            <div class="empty-state">
                <h3>No notes found</h3>
                <p>${filter ? 'Try a different search term' : 'Create your first note to get started!'}</p>
            </div>
        `;
        return;
    }

    elements.notesList.innerHTML = filteredNotes.map(note => `
        <div class="note-card" data-id="${note.id}">
            <h3>${escapeHtml(note.title)}</h3>
            <p>${escapeHtml(note.content)}</p>
            <div class="note-meta">
                Updated: ${formatDate(note.updatedAt)}
            </div>
            <div class="note-actions">
                <button class="btn btn-edit" onclick="editNote(${note.id})">Edit</button>
                <button class="btn btn-danger" onclick="deleteNote(${note.id})">Delete</button>
            </div>
        </div>
    `).join('');
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function openModal(editMode = false) {
    isEditMode = editMode;
    elements.modalTitle.textContent = editMode ? 'Edit Note' : 'Create Note';
    elements.noteModal.classList.add('active');
}

function closeModalHandler() {
    elements.noteModal.classList.remove('active');
    elements.noteTitle.value = '';
    elements.noteContent.value = '';
    currentNoteId = null;
    isEditMode = false;
}

async function saveNote() {
    const title = elements.noteTitle.value.trim();
    const content = elements.noteContent.value.trim();

    if (!title || !content) {
        showNotification('Please fill in all fields', 'error');
        return;
    }

    try {
        let response;
        if (isEditMode && currentNoteId) {
            response = await fetch(`${API_BASE_URL}/${currentNoteId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title, content })
            });
        } else {
            response = await fetch(API_BASE_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title, content })
            });
        }

        if (!response.ok) throw new Error('Failed to save note');

        showNotification(isEditMode ? 'Note updated successfully' : 'Note created successfully', 'success');
        closeModalHandler();
        await fetchNotes();
    } catch (error) {
        showNotification('Error saving note', 'error');
        console.error('Error:', error);
    }
}

async function editNote(id) {
    try {
        const response = await fetch(`${API_BASE_URL}/${id}`);
        if (!response.ok) throw new Error('Failed to fetch note');
        
        const note = await response.json();
        currentNoteId = id;
        elements.noteTitle.value = note.title;
        elements.noteContent.value = note.content;
        openModal(true);
    } catch (error) {
        showNotification('Error loading note', 'error');
        console.error('Error:', error);
    }
}

async function deleteNote(id) {
    if (!confirm('Are you sure you want to delete this note?')) return;

    try {
        const response = await fetch(`${API_BASE_URL}/${id}`, {
            method: 'DELETE'
        });

        if (!response.ok) throw new Error('Failed to delete note');

        showNotification('Note deleted successfully', 'success');
        await fetchNotes();
    } catch (error) {
        showNotification('Error deleting note', 'error');
        console.error('Error:', error);
    }
}

function showNotification(message, type) {
    elements.notification.textContent = message;
    elements.notification.className = `notification ${type} active`;
    
    setTimeout(() => {
        elements.notification.classList.remove('active');
    }, 3000);
}

elements.newNoteBtn.addEventListener('click', () => openModal(false));
elements.closeModal.addEventListener('click', closeModalHandler);
elements.cancelBtn.addEventListener('click', closeModalHandler);
elements.saveBtn.addEventListener('click', saveNote);

elements.searchInput.addEventListener('input', (e) => {
    renderNotes(e.target.value);
});

elements.noteModal.addEventListener('click', (e) => {
    if (e.target === elements.noteModal) {
        closeModalHandler();
    }
});

fetchNotes();
