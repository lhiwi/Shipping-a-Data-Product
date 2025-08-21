import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()  # loads .env from repo root

@dataclass(frozen=True)
class DBConfig:
    host: str = os.getenv("POSTGRES_HOST", "localhost")
    port: int = int(os.getenv("POSTGRES_PORT", "5432"))
    db: str = os.getenv("POSTGRES_DB", "telegram_dw")
    user: str = os.getenv("POSTGRES_USER", "postgres")
    pwd: str = os.getenv("POSTGRES_PASSWORD", "postgres")

@dataclass(frozen=True)
class TelegramConfig:
    api_id: int = int(os.getenv("TELEGRAM_API_ID", "0"))
    api_hash: str = os.getenv("TELEGRAM_API_HASH", "")
    session: str = os.getenv("TELEGRAM_SESSION", "telegram_session")
    channels: tuple[str, ...] = tuple(
        (os.getenv("TELEGRAM_CHANNELS") or "@CheMed123,@lobelia4cosmetics").split(",")
    )
