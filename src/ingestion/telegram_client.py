from telethon import TelegramClient
from . import __init__  # noqa
from src.utils.config import TelegramConfig

def get_client(cfg: TelegramConfig) -> TelegramClient:
    return TelegramClient(cfg.session, cfg.api_id, cfg.api_hash)
