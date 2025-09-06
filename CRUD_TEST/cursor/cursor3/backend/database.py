from tinydb import TinyDB
from datetime import datetime
from models import Note, NoteCreate, NoteUpdate

db = TinyDB('notes.json')
notes_table = db.table('notes')

def create_note(note: NoteCreate) -> Note:
    current_time = datetime.now()
    note_id = notes_table.insert({
        'title': note.title,
        'content': note.content,
        'created_at': current_time.isoformat(),
        'updated_at': current_time.isoformat()
    })
    return Note(
        id=note_id,
        title=note.title,
        content=note.content,
        created_at=current_time,
        updated_at=current_time
    )

def get_all_notes() -> list[Note]:
    notes = []
    for note_id, note_data in enumerate(notes_table.all()):
        notes.append(Note(
            id=note_data.doc_id,
            title=note_data['title'],
            content=note_data['content'],
            created_at=datetime.fromisoformat(note_data['created_at']),
            updated_at=datetime.fromisoformat(note_data['updated_at'])
        ))
    return notes

def get_note(note_id: int) -> Note | None:
    note_data = notes_table.get(doc_id=note_id)
    if note_data is None:
        return None
    return Note(
        id=note_id,
        title=note_data['title'],
        content=note_data['content'],
        created_at=datetime.fromisoformat(note_data['created_at']),
        updated_at=datetime.fromisoformat(note_data['updated_at'])
    )

def update_note(note_id: int, note_update: NoteUpdate) -> Note | None:
    note_data = notes_table.get(doc_id=note_id)
    if note_data is None:
        return None
    
    update_data = {}
    if note_update.title is not None:
        update_data['title'] = note_update.title
    if note_update.content is not None:
        update_data['content'] = note_update.content
    
    if update_data:
        update_data['updated_at'] = datetime.now().isoformat()
        notes_table.update(update_data, doc_ids=[note_id])
        note_data = notes_table.get(doc_id=note_id)
    
    return Note(
        id=note_id,
        title=note_data['title'],
        content=note_data['content'],
        created_at=datetime.fromisoformat(note_data['created_at']),
        updated_at=datetime.fromisoformat(note_data['updated_at'])
    )

def delete_note(note_id: int) -> bool:
    return notes_table.remove(doc_ids=[note_id]) != [] 