import os
from loguru import logger
from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from datetime import datetime
import json
from pathlib import Path
import asyncio

API_ID = int(os.getenv("TELEGRAM_API_ID", "0"))
API_HASH = os.getenv("TELEGRAM_API_HASH", "")
SESSION = os.getenv("TELEGRAM_SESSION", "telegram_session")

OUTPUT_DIR = Path("data/raw/telegram_messages")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

async def fetch_channel(client: TelegramClient, channel: str, limit: int = 200):
    logger.info(f"Scraping {channel} ...")
    result = await client(GetHistoryRequest(peer=channel, limit=limit, offset_date=None, add_offset=0, max_id=0, min_id=0, hash=0))
    messages = []
    for m in result.messages:
        messages.append({
            "id": int(m.id),
            "channel_name": channel,
            "message_text": getattr(m, 'message', None),
            "message_date": m.date.isoformat() if m.date else None,
            "has_image": bool(getattr(m, 'media', None)),
            "image_path": None
        })
    day = datetime.utcnow().strftime('%Y-%m-%d')
    out = OUTPUT_DIR / day / f"{channel.strip('@').replace('/', '_')}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open('w', encoding='utf-8') as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)
    logger.info(f"Saved {len(messages)} messages → {out}")

async def main(channels: list[str]):
    async with TelegramClient(SESSION, API_ID, API_HASH) as client:
        for ch in channels:
            await fetch_channel(client, ch)

if __name__ == "__main__":
    channels = ["@lobelia4cosmetics", "@tikvahpharma"]
    asyncio.run(main(channels))