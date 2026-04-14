import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


def _get_default_db_url() -> str:
    # Ścieżka względna od lokalizacji pliku – działa na każdej maszynie
    base = Path(__file__).resolve().parents[4] / "data" / "cycling.db"
    return f"sqlite:///{base}"


def _get_secret_key() -> str:
    key = os.getenv("SECRET_KEY", "")
    if not key:
        if os.getenv("FLASK_ENV") != "development":
            print(
                "[ERROR] SECRET_KEY nie jest ustawiony.",
                file=sys.stderr
            )
            sys.exit(1)
        key = "dev-only-insecure-key"
    return key


class Config:
    DATABASE_URL: str = os.getenv("DATABASE_URL", _get_default_db_url())
    SECRET_KEY: str = _get_secret_key()
    DEBUG: bool = os.getenv("FLASK_ENV") == "development"
