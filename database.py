# File: database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Local database URL matching our docker-compose environment
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://admin:localpassword@localhost:5432/triage_development"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Dependency helper for FastAPI routes to manage session lifecycles."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()