import enum
from datetime import datetime

from passlib.context import CryptContext
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')   # Настроим хеширование паролей с использованием bcrypt


class TaskStatus(str, enum.Enum):
    pending = 'pending'
    done = 'done'


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)

    tasks = relationship("Task", back_populates="owner")  # Связь с задачами

    def set_password(self, password: str):
        self.hashed_password = pwd_context.hash(password)   #  Хешируем пароль с использованием bcrypt

    def check_password(self, password: str):
        return pwd_context.verify(password, self.hashed_password)   # Проверяем, совпадает ли введенный пароль с хешем


class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(Enum(TaskStatus), default=TaskStatus.pending, nullable=False)
    priority = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    owner = relationship("User", back_populates="tasks")



