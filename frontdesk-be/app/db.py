from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import uuid


# SQLite database setup
DATABASE_URL = "sqlite:///users.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# create enum for status
class StatusEnum(str):
    RESOLVED = "RESOLVED"
    UNRESOLVED = "UNRESOLVED"


# SQLAlchemy User model
class Queries(Base):
    __tablename__ = "queries"
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    query = Column(String)
    status = Column(String, default=StatusEnum.UNRESOLVED)
    response = Column(String, nullable=True)
    created_at = Column(Integer)
    updated_at = Column(Integer)


# Create database tables
Base.metadata.create_all(bind=engine)


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
