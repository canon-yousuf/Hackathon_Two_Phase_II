from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Column, ForeignKey, String
from sqlmodel import Field, SQLModel


class TaskBase(SQLModel):
    """Shared fields for Task creation and response."""

    title: str = Field(max_length=200, min_length=1)
    description: Optional[str] = Field(default=None, max_length=1000)


class Task(TaskBase, table=True):
    """Database table model for tasks."""

    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(
        sa_column=Column(
            String,
            ForeignKey("user.id", ondelete="CASCADE"),
            index=True,
            nullable=False,
        ),
    )
    completed: bool = Field(default=False, index=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )


class TaskCreate(TaskBase):
    """Request schema for creating a task."""

    pass


class TaskUpdate(SQLModel):
    """Request schema for updating a task. All fields optional."""

    title: Optional[str] = Field(default=None, max_length=200, min_length=1)
    description: Optional[str] = Field(default=None, max_length=1000)


class TaskResponse(TaskBase):
    """Response schema for a single task."""

    id: int
    user_id: str
    completed: bool
    created_at: datetime
    updated_at: datetime
