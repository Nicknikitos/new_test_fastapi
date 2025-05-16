from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base


DATABASE_URL = "mysql+pymysql://root:password@localhost/my_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# 👇 Эта строка должна быть после импорта моделей
Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()