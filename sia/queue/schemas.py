from datetime import datetime
from uuid import UUID, uuid4
from pydantic import BaseModel, Field


class SiaQueueItem(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    action: str
    to_execute_at: datetime
    created_at: datetime
