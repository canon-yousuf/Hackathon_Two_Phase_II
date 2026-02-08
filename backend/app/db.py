import os

from sqlalchemy import MetaData, text
from sqlmodel import SQLModel, Session, create_engine

DATABASE_URL = os.environ.get("DATABASE_URL", "")
if not DATABASE_URL:
    raise ValueError(
        "Required environment variable 'DATABASE_URL' is not set. "
        "Check your .env file or environment configuration."
    )

_engine_kwargs: dict = dict(echo=False)
if DATABASE_URL.startswith("sqlite"):
    _engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    _engine_kwargs.update(
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
        pool_recycle=300,
    )

engine = create_engine(DATABASE_URL, **_engine_kwargs)


def create_db_and_tables() -> None:
    """Create all SQLModel tables. Called on app startup.

    The 'user' table is managed by Better Auth (frontend). We reflect
    existing tables first so SQLAlchemy can resolve the FK reference
    from tasks.user_id -> user.id without needing to own the user model.
    """
    # Reflect existing tables (including Better Auth's 'user' table)
    # so SQLAlchemy can resolve foreign key references
    SQLModel.metadata.reflect(bind=engine, only=["user"], extend_existing=True)
    SQLModel.metadata.create_all(engine)


def get_session():
    """FastAPI dependency — yields a database session."""
    with Session(engine) as session:
        yield session
