import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
else:
    if os.getenv("VERCEL"):
        tmp_db = Path("/tmp/school.db")
        if not tmp_db.exists():
            source_db = BASE_DIR / "school.db" if (BASE_DIR / "school.db").exists() else BASE_DIR.parent / "school.db"
            if source_db.exists():
                try:
                    shutil.copy2(source_db, tmp_db)
                except Exception:
                    pass
        DATABASE_URL = f"sqlite:///{tmp_db.as_posix()}"
    else:
        db_file = BASE_DIR / "school.db" if (BASE_DIR / "school.db").exists() else BASE_DIR.parent / "school.db"
        DATABASE_URL = f"sqlite:///{db_file.as_posix()}"

connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
