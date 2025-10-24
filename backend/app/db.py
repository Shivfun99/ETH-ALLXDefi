from sqlalchemy import create_engine, Column, Integer, Float, String, JSON, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings
import datetime

DATABASE_URL = settings.DATABASE_URL

# SQLite-specific kwargs to avoid check_same_thread issues in dev
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Prediction(Base):
    __tablename__ = "predictions"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    input = Column(JSON)
    output = Column(JSON)
    protocol = Column(String, nullable=True)
    user_wallet = Column(String, nullable=True)

def init_db():
    Base.metadata.create_all(bind=engine)

# Simple helper
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
