from typing import List

from fastapi import FastAPI, Depends, HTTPException, status, Body, Path, Query
from sqlalchemy.orm import Session

from auth import create_access_token, create_refresh_token, verify_refresh_token, get_current_user
from database import get_db
from models import User, Task
from schemas import UserCreate, UserLogin, UserResponse, Token, TaskCreate, TaskResponse, TaskUpdate, TaskFilter


app = FastAPI()


@app.post('/register', response_model=UserResponse)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter((User.email == user_data.email) | (User.username == user_data.username)).first()  # # Проверка на уникальность email или username
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email или username уже существует."
        )

    new_user = User(
        username=user_data.username,
        email=user_data.email
    )

    new_user.set_password(user_data.password)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@app.post('/login/', response_model=Token)
def logen(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == user_data.username).first()

    if not user or not user.check_password(user_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Wrong username or password.',
            headers={'WWW-Authenticate': 'Bearer'}
        )

    access_token = create_access_token(data={'sub': user.username})
    refresh_token_str = create_refresh_token(data={'sub': user.username})

    return {'access_token': access_token, 'refresh_token': refresh_token_str, 'token_type': 'bearer'}


@app.post('/refresh', response_model=Token)
def refresh_access_token(refresh_token: str = Body(..., embed=True)):
    username = verify_refresh_token(refresh_token)
    access_token = create_access_token(data={'sub': username})

    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'bearer'
    }


@app.post('/tasks', response_model=TaskResponse)
def create_task(task_data: TaskCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_task = Task(
        title=task_data.title,
        description=task_data.description,
        status=task_data.status,
        priority=task_data.priority,
        owner_id=current_user.id
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task


@app.put('/tasks/{task_id}', response_model=TaskResponse)
def task_update(task_id: int = Path(..., title='Task ID for update'), task_data: TaskUpdate = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id, Task.owner_id == current_user.id).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or you don't have permission"
        )

    if task_data.title is not None:
        task.title = task_data.title
    if task_data.description is not None:
        task.description = task_data.description
    if task_data.priority is not None:
        task.priority = task_data.priority
    if task_data.status is not None:
        task.status = task_data.status

    db.commit()
    db.refresh(task)
    return task


@app.get('/tasks', response_model=List[TaskResponse])
def get_tasks(filters: TaskFilter = Depends(), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(Task).filter(Task.owner_id == current_user.id)

    if filters.status:
        query = query.filter(Task.status == filters.status)
    if filters.priority:
        query = query.filter(Task.priority == filters.priority)
    if filters.created_from:
        query = query.filter(Task.created_at >= filters.created_from)
    if filters.created_to:
        query = query.filter(Task.created_at <= filters.created_to)

    tasks = query.all()
    return tasks


@app.get('/tasks/search', response_model=List[TaskResponse])
def search_tasks(q: str = Query(..., min_length=1, description='Search'), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(Task).filter(Task.owner_id == current_user.id, (Task.title.ilike(f'%{q}%')) | (Task.description.ilike(f'%{q}%')))
    tasks = query.all()
    return tasks
