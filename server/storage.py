from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base, Agent, Task, Result
from .utils import log_info

engine = create_engine('sqlite:///bridgesmesh.db', connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
    log_info("Database initialized")

def get_session():
    return SessionLocal()
