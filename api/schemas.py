from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Message(BaseModel):
    message_id: int
    channel_name: str
    message_text: Optional[str]
    message_timestamp: datetime
    has_image: bool
    image_path: Optional[str]

class TopProduct(BaseModel):
    product: str
    mentions: int