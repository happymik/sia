from pydantic import BaseModel
from datetime import datetime


class SiaTelegramSettingsSchema(BaseModel):
    posting_enabled: bool
    posting_frequency: int
    response_frequency: str
    next_post_after: datetime
    posting_examples: list[str]
    response_examples: list[str]
    response_filtering_rules: list[str]
