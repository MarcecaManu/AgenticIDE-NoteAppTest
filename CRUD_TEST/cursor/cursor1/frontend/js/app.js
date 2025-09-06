// API endpoints
const API_BASE_URL = 'http://localhost:8000/api/notes';

// DOM elements
const notesGrid = document.getElementById('notesGrid');
const searchInput = document.getElementById('searchInput');
const newNoteBtn = document.getElementById('newNoteBtn');
const noteModal = document.getElementById('noteModal');
const noteTitleInput = document.getElementById('noteTitle');
const noteContentInput = document.getElementById('noteContent');
const closeModalBtn = document.getElementById('closeModal');
const saveNoteBtn = document.getElementById('saveNote');

// State
let currentNoteId = null;
let notes = [];

// Event listeners
window.addEventListener('load', () => loadNotes());
searchInput.addEventListener('input', handleSearch);
newNoteBtn.addEventListener('click', () => openModal());
closeModalBtn.addEventListener('click', closeModal);
saveNoteBtn.addEventListener('click', handleSaveNote);

// Functions
async function loadNotes(searchTerm = '') {
    try {
        const url = searchTerm
            ? `${API_BASE_URL}/?search=${encodeURIComponent(searchTerm)}`
            : API_BASE_URL + '/';
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error('Failed to load notes');
        }
        notes = await response.json();
        renderNotes();
    } catch (error) {
        console.error('Error loading notes:', error);
        alert('Failed to load notes. Please try again.');
    }
}

function renderNotes() {
    notesGrid.innerHTML = notes.map(note => `
        <div class="note-card">
            <h3>${escapeHtml(note.title)}</h3>
            <p>${escapeHtml(note.content)}</p>
            <div class="note-actions">
                <button class="btn edit-btn" onclick="openModal(${note.id})">Edit</button>
                <button class="btn delete-btn" onclick="deleteNote(${note.id})">Delete</button>
            </div>
            <div class="timestamp">
                Last updated: ${new Date(note.updated_at).toLocaleString()}
            </div>
        </div>
    `).join('');
}

function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

async function handleSearch(event) {
    const searchTerm = event.target.value.trim();
    await loadNotes(searchTerm);
}

function openModal(noteId = null) {
    currentNoteId = noteId;
    if (noteId) {
        const note = notes.find(n => n.id === noteId);
        if (note) {
            noteTitleInput.value = note.title;
            noteContentInput.value = note.content;
        }
    } else {
        noteTitleInput.value = '';
        noteContentInput.value = '';
    }
    noteModal.style.display = 'block';
}

function closeModal() {
    noteModal.style.display = 'none';
    currentNoteId = null;
    noteTitleInput.value = '';
    noteContentInput.value = '';
}

async function handleSaveNote() {
    const title = noteTitleInput.value.trim();
    const content = noteContentInput.value.trim();

    if (!title || !content) {
        alert('Please fill in both title and content.');
        return;
    }

    try {
        const method = currentNoteId ? 'PUT' : 'POST';
        const url = currentNoteId 
            ? `${API_BASE_URL}/${currentNoteId}`
            : API_BASE_URL + '/';

        const response = await fetch(url, {
            method,
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ title, content }),
        });

        if (!response.ok) {
            throw new Error('Failed to save note');
        }

        closeModal();
        await loadNotes(searchInput.value.trim());
    } catch (error) {
        console.error('Error saving note:', error);
        alert('Failed to save note. Please try again.');
    }
}

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

        await loadNotes(searchInput.value.trim());
    } catch (error) {
        console.error('Error deleting note:', error);
        alert('Failed to delete note. Please try again.');
    }
} 