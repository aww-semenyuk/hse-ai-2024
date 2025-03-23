from sqlmodel import create_engine, Session
from sqlalchemy.orm import sessionmaker

from config import POSTGRES_URL

engine = create_engine(POSTGRES_URL, echo=True)
SessionLocal = sessionmaker(class_=Session, autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
