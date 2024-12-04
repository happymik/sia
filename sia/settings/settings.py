from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import pytz

class PluginSettings(BaseModel):
    probability_of_use: float

class SiaPostingCondition(BaseModel):
    time_of_day: str
    next_post_after: datetime = Field(default_factory=lambda: datetime.now(pytz.UTC))

# class ConditionalSettings(BaseModel):
#     enabled: bool
#     condition: Condition
#     frequency_per_day: int
#     plugins: Dict[str, Dict[str, PluginSettings]]
#     examples: List[str] = Field(None)

class SiaPostingSettings(BaseModel):
    enabled: bool
    condition: SiaPostingCondition = Field(None)
    frequency_per_day: int
    next_post_after: datetime = Field(default_factory=lambda: datetime.now(pytz.UTC))
    examples: List[str] = Field(None)
    plugins: Dict[str, Dict[str, PluginSettings]]
    conditional: Dict[str, 'SiaPostingSettings'] = Field(None)
    
    def get_time_of_day(self, current_time: datetime = datetime.now(pytz.UTC)) -> str:
        hour = current_time.hour
        if 5 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 21:
            return "evening"
        else:
            return "night"

    def should_post_now(self, current_time: datetime = datetime.now(pytz.UTC)) -> Optional['SiaPostingSettings'|None]:
        # Check if posting is enabled
        if not self.enabled:
            print("Posting is not enabled")
            return None

        # Check if the current time is after the next_post_after time
        if current_time+timedelta(seconds=30) <= self.next_post_after:
            print(f"Posting is not enabled because the current time is before the next_post_after time: {self.next_post_after} vs {current_time}")
            return None

        # Determine which conditional settings to use based on the current time
        for key, condition in self.conditional.items():
            print(f"Checking condition: {key}")
            if condition.enabled:
                print(f"Condition {key} is enabled")
                # Check if the current time matches the condition's time_of_day
                print(f"Current time of day: {self.get_time_of_day(current_time)}")
                if condition.condition.time_of_day in self.get_time_of_day():
                    print(f"Condition {key} matches the time of day")
                    # Check if the current time is after the condition's next_post_after time
                    print(f"Current time: {current_time}, next_post_after: {condition.condition.next_post_after}")
                    if current_time+timedelta(seconds=30) >= condition.condition.next_post_after:
                        return condition

        # Default to general posting if no conditions are met
        return self
