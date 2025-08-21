from pydantic import BaseModel
from typing import Optional, List

class HealthOut(BaseModel):
    status: str = "ok"

class ProductCount(BaseModel):
    term: str
    hits: int

class ChannelActivityPoint(BaseModel):
    date: str
    messages: int

class MessageHit(BaseModel):
    message_id: int
    channel_name: str
    message_ts: str
    message_text: Optional[str] = None
