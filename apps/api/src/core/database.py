from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from core.config import Config
import os

engine = create_engine(
    Config.DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    from infrastructure.db import models  # noqa: F401
    db_path = Config.DATABASE_URL.replace("sqlite:////", "/")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    Base.metadata.create_all(bind=engine)
    print(f"[DB] SQLite initialized: {Config.DATABASE_URL}")


def check_db_connection() -> bool:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
