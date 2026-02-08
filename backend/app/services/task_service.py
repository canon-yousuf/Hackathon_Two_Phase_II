from datetime import datetime, timezone

from sqlmodel import Session, col, select

from app.models.task import Task, TaskCreate, TaskUpdate


def get_tasks(
    session: Session,
    user_id: str,
    status: str = "all",
    sort: str = "created",
) -> list[Task]:
    """List tasks for a user with optional filtering and sorting.

    Args:
        session: Database session
        user_id: User ID to filter tasks
        status: Filter by completion status ("all", "pending", "completed")
        sort: Sort order ("created" for created_at desc, "title" for title asc)

    Returns:
        List of Task objects matching the criteria
    """
    statement = select(Task).where(Task.user_id == user_id)

    # Filter by status
    if status == "pending":
        statement = statement.where(Task.completed == False)
    elif status == "completed":
        statement = statement.where(Task.completed == True)

    # Sort
    if sort == "title":
        statement = statement.order_by(col(Task.title))
    elif sort == "created":
        statement = statement.order_by(col(Task.created_at).desc())

    return session.exec(statement).all()


def get_task(session: Session, user_id: str, task_id: int) -> Task | None:
    """Get a single task, ensuring it belongs to the user.

    Args:
        session: Database session
        user_id: User ID to verify ownership
        task_id: Task ID to retrieve

    Returns:
        Task object if found and belongs to user, None otherwise
    """
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    return session.exec(statement).first()


def create_task(session: Session, user_id: str, data: TaskCreate) -> Task:
    """Create a new task for the user.

    Args:
        session: Database session
        user_id: User ID to own the task
        data: Task creation data (title, description)

    Returns:
        Created Task object
    """
    task = Task(
        user_id=user_id,
        title=data.title,
        description=data.description,
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


def update_task(
    session: Session,
    user_id: str,
    task_id: int,
    data: TaskUpdate,
    fields_set: set[str],
) -> Task | None:
    """Update a task's title or description.

    Args:
        session: Database session
        user_id: User ID to verify ownership
        task_id: Task ID to update
        data: Task update data (title, description - all optional)
        fields_set: Set of field names that were explicitly provided in request

    Returns:
        Updated Task object if found and belongs to user, None otherwise
    """
    task = get_task(session, user_id, task_id)
    if not task:
        return None

    # Only update fields that were explicitly set in the request
    if "title" in fields_set:
        task.title = data.title
    if "description" in fields_set:
        task.description = data.description

    task.updated_at = datetime.now(timezone.utc)

    session.add(task)
    session.commit()
    session.refresh(task)
    return task


def delete_task(session: Session, user_id: str, task_id: int) -> bool:
    """Delete a task.

    Args:
        session: Database session
        user_id: User ID to verify ownership
        task_id: Task ID to delete

    Returns:
        True if deleted successfully, False if not found or doesn't belong to user
    """
    task = get_task(session, user_id, task_id)
    if not task:
        return False
    session.delete(task)
    session.commit()
    return True


def toggle_complete(session: Session, user_id: str, task_id: int) -> Task | None:
    """Toggle the completed status of a task.

    Args:
        session: Database session
        user_id: User ID to verify ownership
        task_id: Task ID to toggle

    Returns:
        Updated Task object if found and belongs to user, None otherwise
    """
    task = get_task(session, user_id, task_id)
    if not task:
        return None
    task.completed = not task.completed
    task.updated_at = datetime.now(timezone.utc)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task
