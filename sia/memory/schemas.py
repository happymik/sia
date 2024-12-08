from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import uuid4

class SiaMessageGeneratedSchema(BaseModel):
    conversation_id: Optional[str] = None
    content: str
    platform: str
    author: str
    character: Optional[str] = None
    response_to: Optional[str] = None
    flagged: Optional[bool] = Field(default=False)
    message_metadata: Optional[dict] = None

    class Config:
        # orm_mode = True
        from_attributes = True

class SiaMessageSchema(SiaMessageGeneratedSchema):
    id: str
    wen_posted: datetime = Field(default_factory=lambda: datetime.now())
    original_data: Optional[dict] = None

    class Config:
        # orm_mode = True
        from_attributes = True

class SiaCharacterSettingsSchema(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    character_name_id: str
    character_settings: dict

    class Config:
        # orm_mode = True
        from_attributes = True
