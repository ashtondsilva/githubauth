from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from config import SQLALCHEMY_DATABASE_URI

# Create SQLAlchemy engine and session
engine = create_engine(SQLALCHEMY_DATABASE_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create declarative base
Base = declarative_base()

class Token(Base):
    __tablename__ = 'tokens'
    
    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    access_token = Column(String, nullable=False)
    token_type = Column(String)
    scope = Column(String)
    created_at = Column(DateTime, default=datetime.now)
    expires_at = Column(DateTime)
    refresh_token = Column(String)
    
    def is_expired(self) -> bool:
        """Check if the token is expired"""
        if not self.expires_at:
            return True
        return datetime.now() > self.expires_at

# Database Dependency
def get_db() -> Session:
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create all tables
Base.metadata.create_all(bind=engine)