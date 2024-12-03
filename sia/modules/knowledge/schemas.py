from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime


class KnowledgeModuleSettingsSchema(BaseModel):
    id: Optional[str] = None
    character_name_id: Optional[str]
    module_name: Optional[str]
    module_settings: Optional[Dict] = {}
    created_at: Optional[datetime] = datetime.now()
