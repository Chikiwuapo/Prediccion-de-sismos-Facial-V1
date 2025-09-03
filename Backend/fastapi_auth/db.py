from pathlib import Path
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / 'user.db'

# Permitir configurar base de datos por env (Render u otros proveedores)
DATABASE_URL = os.getenv("DATABASE_URL") or f"sqlite:///{DB_PATH}"

is_sqlite = DATABASE_URL.startswith("sqlite")

engine = create_engine(
    DATABASE_URL,
    connect_args=(
        {"check_same_thread": False, "timeout": 10} if is_sqlite else {}
    ),
    pool_pre_ping=True,
)

# Sólo para SQLite: configurar PRAGMAs y limpiar -wal/-shm
if is_sqlite:
    with engine.connect() as conn:
        try:
            conn.execute(text("PRAGMA wal_checkpoint(TRUNCATE)"))
            conn.execute(text("PRAGMA journal_mode=DELETE"))
            conn.execute(text("PRAGMA synchronous=FULL"))
            conn.execute(text("PRAGMA busy_timeout=5000"))  # milisegundos
        except Exception:
            pass

        try:
            wal_path = str(DB_PATH) + "-wal"
            shm_path = str(DB_PATH) + "-shm"
            Path(wal_path).unlink(missing_ok=True)
            Path(shm_path).unlink(missing_ok=True)
        except Exception:
            pass

        # Migración simple: asegurar columna 'role' en tabla users
        try:
            res = conn.execute(text("PRAGMA table_info(users)"))
            cols = [row[1] for row in res.fetchall()]  # (cid, name, type, ...)
            if 'role' not in cols:
                conn.execute(text("ALTER TABLE users ADD COLUMN role TEXT NOT NULL DEFAULT 'Usuario'"))
            try:
                conn.execute(text("UPDATE users SET role='CEO' WHERE username IN ('Eduard','Leonel')"))
            except Exception:
                pass
        except Exception:
            pass

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
