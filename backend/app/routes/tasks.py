from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from app.db import get_session
from app.middleware.auth import enforce_user_access, get_current_user
from app.models.task import TaskCreate, TaskResponse, TaskUpdate
from app.services import task_service

router = APIRouter(prefix="/api/{user_id}/tasks", tags=["tasks"])


@router.get("", response_model=list[TaskResponse])
async def list_tasks(
    user_id: str,
    status_filter: str = Query(
        "all",
        alias="status",
        pattern="^(all|pending|completed)$",
    ),
    sort: str = Query("created", pattern="^(created|title)$"),
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    """List all tasks for the authenticated user with optional filtering and sorting."""
    enforce_user_access(user_id, current_user)
    return task_service.get_tasks(session, user_id, status=status_filter, sort=sort)


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    user_id: str,
    data: TaskCreate,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    """Create a new task for the authenticated user."""
    enforce_user_access(user_id, current_user)
    return task_service.create_task(session, user_id, data)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    user_id: str,
    task_id: int,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    """Get a single task by ID, ensuring it belongs to the authenticated user."""
    enforce_user_access(user_id, current_user)
    task = task_service.get_task(session, user_id, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    user_id: str,
    task_id: int,
    data: TaskUpdate,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    """Update a task's title or description. At least one field must be provided."""
    enforce_user_access(user_id, current_user)

    # Validate that at least one field was provided in the request body
    if not data.model_fields_set:
        raise HTTPException(
            status_code=422,
            detail="At least one field must be provided",
        )

    task = task_service.update_task(
        session,
        user_id,
        task_id,
        data,
        data.model_fields_set,
    )
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    user_id: str,
    task_id: int,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    """Delete a task. Returns 204 No Content on success."""
    enforce_user_access(user_id, current_user)
    deleted = task_service.delete_task(session, user_id, task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")
    return None


@router.patch("/{task_id}/complete", response_model=TaskResponse)
async def toggle_complete(
    user_id: str,
    task_id: int,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    """Toggle the completion status of a task."""
    enforce_user_access(user_id, current_user)
    task = task_service.toggle_complete(session, user_id, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
