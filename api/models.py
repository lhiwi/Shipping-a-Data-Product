from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class RawTelegramMessage(Base):
    __tablename__ = "telegram_messages"
    __table_args__ = {"schema": "raw"}

    id = Column(Integer, primary_key=True)
    channel_name = Column(String(255))
    message_text = Column(Text)
    message_date = Column(DateTime)
    has_image = Column(Boolean)
    image_path = Column(String(512))