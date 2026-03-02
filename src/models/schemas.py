from pydantic import BaseModel, Field
from datetime import datetime

class Event(BaseModel):
    id: str
    tipo: str
    payload: dict
    created_at: datetime = Field(default_factory=datetime.utcnow)
