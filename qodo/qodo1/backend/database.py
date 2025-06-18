from datetime import datetime
from typing import List, Optional
from tinydb import TinyDB, Query
from pathlib import Path
import threading
import time

class Database:
    _lock = threading.Lock()
    _instances = {}
    
    def __new__(cls, db_path=None):
        if db_path is None:
            db_path = Path(__file__).parent / "notes.json"
        
        db_path = Path(db_path)
        if str(db_path) not in cls._instances:
            instance = super(Database, cls).__new__(cls)
            instance._db = None
            instance._db_path = db_path
            cls._instances[str(db_path)] = instance
        return cls._instances[str(db_path)]

    def __init__(self, db_path=None):
        if db_path is None:
            db_path = Path(__file__).parent / "notes.json"
        self._db_path = Path(db_path)
        self._connect_db()

    def _connect_db(self):
        if self._db is None:
            retries = 3
            while retries > 0:
                try:
                    with self._lock:
                        self._db = TinyDB(self._db_path)
                        self.notes = self._db.table('notes')
                        self.Note = Query()
                    break
                except Exception as e:
                    retries -= 1
                    if retries == 0:
                        raise
                    time.sleep(0.1)

    def _ensure_connected(self):
        if self._db is None:
            self._connect_db()

    def create_note(self, title: str, content: str) -> dict:
        self._ensure_connected()
        with self._lock:
            now = datetime.utcnow()
            note = {
                'id': self._get_next_id(),
                'title': title,
                'content': content,
                'created_at': now.isoformat(),
                'updated_at': now.isoformat()
            }
            self.notes.insert(note)
            return note

    def get_all_notes(self) -> List[dict]:
        self._ensure_connected()
        with self._lock:
            return self.notes.all()

    def get_note(self, note_id: int) -> Optional[dict]:
        self._ensure_connected()
        with self._lock:
            return self.notes.get(self.Note.id == note_id)

    def update_note(self, note_id: int, title: Optional[str], content: Optional[str]) -> Optional[dict]:
        self._ensure_connected()
        with self._lock:
            note = self.notes.get(self.Note.id == note_id)
            if note:
                update_data = {}
                if title is not None:
                    update_data['title'] = title
                if content is not None:
                    update_data['content'] = content
                update_data['updated_at'] = datetime.utcnow().isoformat()
                
                self.notes.update(update_data, self.Note.id == note_id)
                return self.notes.get(self.Note.id == note_id)
            return None

    def delete_note(self, note_id: int) -> bool:
        self._ensure_connected()
        with self._lock:
            return self.notes.remove(self.Note.id == note_id) != []

    def _get_next_id(self) -> int:
        with self._lock:
            notes = self.notes.all()
            return max([note['id'] for note in notes], default=0) + 1
            
    def close(self):
        with self._lock:
            if self._db is not None:
                self._db.close()
                self._db = None

    def __del__(self):
        self.close()
