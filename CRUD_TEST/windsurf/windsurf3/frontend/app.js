const API_URL = 'http://localhost:8000/api/notes';

// DOM Elements
const notesList = document.getElementById('notesList');
const titleInput = document.getElementById('titleInput');
const contentInput = document.getElementById('contentInput');
const saveButton = document.getElementById('saveButton');
const cancelButton = document.getElementById('cancelButton');
const searchInput = document.getElementById('searchInput');
const noteIdInput = document.getElementById('noteId');

// State
let notes = [];

// Event Listeners
saveButton.addEventListener('click', handleSaveNote);
cancelButton.addEventListener('click', handleCancel);
searchInput.addEventListener('input', handleSearch);

// Functions
async function fetchNotes() {
    try {
        const response = await fetch(API_URL);
        notes = await response.json();
        displayNotes(notes);
    } catch (error) {
        console.error('Error fetching notes:', error);
    }
}

function displayNotes(notesToShow) {
    notesList.innerHTML = '';
    notesToShow.forEach(note => {
        const noteElement = createNoteElement(note);
        notesList.appendChild(noteElement);
    });
}

function createNoteElement(note) {
    const div = document.createElement('div');
    div.className = 'note-card';
    div.innerHTML = `
        <h3>${note.title}</h3>
        <p>${note.content}</p>
        <div class="actions">
            <button class="edit" onclick="handleEdit(${note.id})">Edit</button>
            <button class="delete" onclick="handleDelete(${note.id})">Delete</button>
        </div>
    `;
    return div;
}

async function handleSaveNote() {
    const title = titleInput.value.trim();
    const content = contentInput.value.trim();
    
    if (!title || !content) {
        alert('Please fill in both title and content');
        return;
    }

    const noteData = { title, content };
    const noteId = noteIdInput.value;

    try {
        if (noteId) {
            // Update existing note
            await fetch(`${API_URL}/${noteId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(noteData)
            });
        } else {
            // Create new note
            await fetch(API_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(noteData)
            });
        }

        clearForm();
        await fetchNotes();
    } catch (error) {
        console.error('Error saving note:', error);
    }
}

async function handleDelete(id) {
    if (!confirm('Are you sure you want to delete this note?')) {
        return;
    }

    try {
        await fetch(`${API_URL}/${id}`, { method: 'DELETE' });
        await fetchNotes();
    } catch (error) {
        console.error('Error deleting note:', error);
    }
}

async function handleEdit(id) {
    const note = notes.find(n => n.id === id);
    if (note) {
        titleInput.value = note.title;
        contentInput.value = note.content;
        noteIdInput.value = note.id;
        saveButton.textContent = 'Update Note';
        cancelButton.style.display = 'inline';
    }
}

function handleCancel() {
    clearForm();
}

function clearForm() {
    titleInput.value = '';
    contentInput.value = '';
    noteIdInput.value = '';
    saveButton.textContent = 'Save Note';
    cancelButton.style.display = 'none';
}

function handleSearch(e) {
    const searchTerm = e.target.value.toLowerCase();
    const filteredNotes = notes.filter(note => 
        note.title.toLowerCase().includes(searchTerm)
    );
    displayNotes(filteredNotes);
}

// Initial load
fetchNotes();
