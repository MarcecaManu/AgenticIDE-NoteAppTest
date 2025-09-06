from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Create the base class for declarative models
Base = declarative_base()

def get_engine(database_url="sqlite:///./notes.db"):
    return create_engine(
        database_url,
        connect_args={"check_same_thread": False}
    )

def get_session_local(engine):
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    engine = get_engine()
    SessionLocal = get_session_local(engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
