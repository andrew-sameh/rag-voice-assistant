import os
from dotenv import load_dotenv
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Sequence
from datetime import datetime 
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Optional
load_dotenv('.env')

# Database setup
DATABASE_URL = f"postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class TextFile(Base):
    __tablename__ = "text_files"

    id = Column(Integer, Sequence('textfiles_id_seq', start=1, increment=1), primary_key=True, index=True)
    file_name = Column(String, nullable=False)
    name = Column(String, nullable=False)
    namespace = Column(String, nullable=False)
    type = Column(String, nullable=False)
    overview = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# Create the table
Base.metadata.create_all(bind=engine)

class TextFileBase(BaseModel):
    file_name: str
    name: str
    namespace: str
    type: str
    overview: str | None = None


class TextFileCreate(TextFileBase):
    pass

class TextFileUpdate(BaseModel):
    file_name: Optional[str] = None
    name: Optional[str] = None
    namespace: Optional[str] = None
    type: Optional[str] = None
    overview: Optional[str] = None


class TextFileResponse(TextFileBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True