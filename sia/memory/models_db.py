from sqlalchemy import Column, String, JSON, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from uuid import uuid4

Base = declarative_base()

class SiaMessageModel(Base):
    __tablename__ = 'message'

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    conversation_id = Column(String)
    character = Column(String)
    platform = Column(String, nullable=False)
    author = Column(String, nullable=False)
    content = Column(String, nullable=False)
    response_to = Column(String)
    wen_posted = Column(DateTime, default=lambda: datetime.now())
    original_data = Column(JSON)
    flagged = Column(Boolean, nullable=True, default=False)
    message_metadata = Column(JSON)
