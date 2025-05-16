from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from models import TaskStatus


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str='bearer'


class TaskCreate(BaseModel):
    title: str
    description: str
    priority: int
    status: TaskStatus = TaskStatus.pending


class TaskResponse(BaseModel):
    id: int
    title: str
    description: str
    status: TaskStatus
    priority: int
    created_at: datetime
    owner_id: int

    class Config:
        from_attributes = True


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[int] = None
    status: Optional[TaskStatus] = None


class TaskFilter(BaseModel):
    status: Optional[TaskStatus] = Field(None, description='Status filter')
    priority: Optional[int] = Field(None, description='Priority filter')
    created_from: Optional[datetime] = Field(None, description='From date')
    created_to: Optional[datetime] = Field(None, description='To date')