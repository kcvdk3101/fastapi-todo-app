from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.url import todo
from app.core.database import get_db_context
from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate, TaskOut
from app.services.auth import get_current_user

router = APIRouter(prefix=todo["prefix"], tags=todo["tags"])

def _ensure_access(task: Task, current_user: User):
    if task.company_id != current_user.company_id:
        raise HTTPException(status_code=403, detail="Cross-company access denied")
    if not current_user.is_admin and task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

# Get task list
@router.get(todo["urls"]["list_tasks"], response_model=list[TaskOut])
def list_tasks(
    status_filter: str | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db_context),
    current_user: User = Depends(get_current_user),
):
    q = db.query(Task).filter(Task.company_id == current_user.company_id)
    if not current_user.is_admin:
        q = q.filter(Task.user_id == current_user.id)
    if status_filter:
        q = q.filter(Task.status == status_filter)
    return q.all()

# Get task detail
@router.get(todo["urls"]["get_task_by_id"], response_model=TaskOut)
def get_task(
    task_id: UUID,
    db: Session = Depends(get_db_context),
    current_user: User = Depends(get_current_user),
):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    _ensure_access(task, current_user)
    return task

# Create task
@router.post(todo["urls"]["create_task"], response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(
    payload: TaskCreate,
    db: Session = Depends(get_db_context),
    current_user: User = Depends(get_current_user),
):
    task = Task(
        **payload.model_dump(),
        user_id=current_user.id,
        company_id=current_user.company_id,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

# Update task
@router.put(todo["urls"]["update_task"], response_model=TaskOut)
def update_task(
    task_id: UUID,
    payload: TaskUpdate,
    db: Session = Depends(get_db_context),
    current_user: User = Depends(get_current_user),
):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    _ensure_access(task, current_user)

    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(task, k, v)
    db.commit()
    db.refresh(task)
    return task

# Delete task
@router.delete(todo["urls"]["delete_task"], status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: UUID,
    db: Session = Depends(get_db_context),
    current_user: User = Depends(get_current_user),
):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    _ensure_access(task, current_user)
    db.delete(task)
    db.commit()
