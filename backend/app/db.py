import os

from sqlmodel import SQLModel, Session, create_engine

DATABASE_URL = os.environ.get("DATABASE_URL", "")
if not DATABASE_URL:
    raise ValueError(
        "Required environment variable 'DATABASE_URL' is not set. "
        "Check your .env file or environment configuration."
    )

engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    pool_recycle=300,
)


def create_db_and_tables() -> None:
    """Create all SQLModel tables. Called on app startup."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """FastAPI dependency — yields a database session."""
    with Session(engine) as session:
        yield session
