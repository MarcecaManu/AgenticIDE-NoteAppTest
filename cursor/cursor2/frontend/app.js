const API_BASE_URL = 'http://localhost:8000/api/notes';

// DOM Elements
const noteForm = document.getElementById('noteForm');
const noteId = document.getElementById('noteId');
const titleInput = document.getElementById('titleInput');
const contentInput = document.getElementById('contentInput');
const submitBtn = document.getElementById('submitBtn');
const cancelBtn = document.getElementById('cancelBtn');
const searchInput = document.getElementById('searchInput');
const notesGrid = document.getElementById('notesGrid');

// State
let notes = [];

// Event Listeners
noteForm.addEventListener('submit', handleSubmit);
cancelBtn.addEventListener('click', resetForm);
searchInput.addEventListener('input', handleSearch);

// Load notes on page load
loadNotes();

async function loadNotes() {
    try {
        const response = await fetch(API_BASE_URL);
        notes = await response.json();
        renderNotes();
    } catch (error) {
        console.error('Error loading notes:', error);
    }
}

function renderNotes(filteredNotes = notes) {
    notesGrid.innerHTML = '';
    filteredNotes.forEach(note => {
        const noteElement = createNoteElement(note);
        notesGrid.appendChild(noteElement);
    });
}

function createNoteElement(note) {
    const div = document.createElement('div');
    div.className = 'note-card';
    
    const createdDate = new Date(note.created_at).toLocaleDateString();
    const updatedDate = new Date(note.updated_at).toLocaleDateString();
    
    div.innerHTML = `
        <div class="note-actions">
            <button onclick="editNote(${note.id})">✏️</button>
            <button onclick="deleteNote(${note.id})">🗑️</button>
        </div>
        <h3>${escapeHtml(note.title)}</h3>
        <p>${escapeHtml(note.content)}</p>
        <div class="date">
            Created: ${createdDate}
            ${createdDate !== updatedDate ? `<br>Updated: ${updatedDate}` : ''}
        </div>
    `;
    
    return div;
}

function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

async function handleSubmit(e) {
    e.preventDefault();
    
    const noteData = {
        title: titleInput.value,
        content: contentInput.value
    };
    
    try {
        if (noteId.value) {
            // Update existing note
            await fetch(`${API_BASE_URL}/${noteId.value}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(noteData)
            });
        } else {
            // Create new note
            await fetch(API_BASE_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(noteData)
            });
        }
        
        resetForm();
        await loadNotes();
    } catch (error) {
        console.error('Error saving note:', error);
    }
}

function editNote(id) {
    const note = notes.find(n => n.id === id);
    if (note) {
        noteId.value = note.id;
        titleInput.value = note.title;
        contentInput.value = note.content;
        submitBtn.textContent = 'Update Note';
        cancelBtn.style.display = 'inline-block';
    }
}

async function deleteNote(id) {
    if (!confirm('Are you sure you want to delete this note?')) return;
    
    try {
        await fetch(`${API_BASE_URL}/${id}`, { method: 'DELETE' });
        await loadNotes();
    } catch (error) {
        console.error('Error deleting note:', error);
    }
}

function resetForm() {
    noteForm.reset();
    noteId.value = '';
    submitBtn.textContent = 'Add Note';
    cancelBtn.style.display = 'none';
}

function handleSearch(e) {
    const searchTerm = e.target.value.toLowerCase();
    const filteredNotes = notes.filter(note => 
        note.title.toLowerCase().includes(searchTerm)
    );
    renderNotes(filteredNotes);
} 