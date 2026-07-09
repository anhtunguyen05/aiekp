import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Create a separate SQLite DB for auth/tenants
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUTH_DB_PATH = os.path.join(BASE_DIR, "..", "auth.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{AUTH_DB_PATH}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def init_auth_db():
    Base.metadata.create_all(bind=engine)

def get_auth_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
