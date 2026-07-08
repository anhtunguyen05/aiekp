import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base

# By default use SQLite in the current working directory or a path from env
db_path = os.environ.get("TELEMETRY_DB_PATH", "telemetry.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_path}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_telemetry_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
