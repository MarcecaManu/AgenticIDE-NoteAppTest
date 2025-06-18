from tinydb import TinyDB, Query
from datetime import datetime
from backend.models import Note, NoteCreate, NoteUpdate

db = TinyDB('notes.json')
notes_table = db.table('notes')
Note_Query = Query()

def get_next_id() -> int:
    all_notes = notes_table.all()
    if not all_notes:
        return 1
    return max(note['id'] for note in all_notes) + 1

def create_note(note: NoteCreate) -> Note:
    current_time = datetime.utcnow()
    note_id = get_next_id()
    note_dict = {
        'id': note_id,
        'title': note.title,
        'content': note.content,
        'created_at': current_time.isoformat(),
        'updated_at': current_time.isoformat()
    }
    notes_table.insert(note_dict)
    return Note(**note_dict)

def get_all_notes() -> list[Note]:
    notes = notes_table.all()
    return [Note(**note) for note in notes]

def get_note(note_id: int) -> Note | None:
    note = notes_table.get(Note_Query.id == note_id)
    return Note(**note) if note else None

def update_note(note_id: int, note_update: NoteUpdate) -> Note | None:
    existing_note = notes_table.get(Note_Query.id == note_id)
    if not existing_note:
        return None
    
    update_data = note_update.model_dump(exclude_unset=True)
    if update_data:
        update_data['updated_at'] = datetime.utcnow().isoformat()
        notes_table.update(update_data, Note_Query.id == note_id)
        updated_note = notes_table.get(Note_Query.id == note_id)
        return Note(**updated_note)
    return Note(**existing_note)

def delete_note(note_id: int) -> bool:
    removed = notes_table.remove(Note_Query.id == note_id)
    return len(removed) > 0 