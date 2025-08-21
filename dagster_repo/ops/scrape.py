from dagster import op, get_dagster_logger
import os, json, datetime, asyncio
from pathlib import Path
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.tl.types import MessageMediaPhoto

# Reuse your channel list for Task-1
CHANNELS = ["@CheMed123", "@lobelia4cosmetics", "@tikvahpharma"]

def _load_state(state_file: Path) -> dict:
    if state_file.exists():
        try:
            return json.loads(state_file.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}

def _save_state(state_file: Path, state: dict):
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text(json.dumps(state, indent=2), encoding="utf-8")

@op
def scrape_telegram_data():
    """Incremental scrape of Telegram channels (messages + images)."""
    log = get_dagster_logger()
    load_dotenv(".env")

    api_id = int(os.getenv("TELEGRAM_API_ID"))
    api_hash = os.getenv("TELEGRAM_API_HASH")
    session_name = os.getenv("TELEGRAM_SESSION", "telegram_session")

    today = datetime.date.today().isoformat()
    base = Path(".")
    msg_dir = base / "data" / "raw" / "telegram_messages" / today
    img_dir = base / "data" / "raw" / "images" / today
    state_file = base / ".state" / "scrape_state.json"

    msg_dir.mkdir(parents=True, exist_ok=True)
    img_dir.mkdir(parents=True, exist_ok=True)

    state = _load_state(state_file)

    async def _run():
        async with TelegramClient(session_name, api_id, api_hash) as client:
            for channel in CHANNELS:
                ch_name = channel.strip("@")
                ch_state = state.get(channel) or {}
                since_id = ch_state.get("last_id")
                out = []
                ch_img_dir = img_dir / ch_name
                ch_img_dir.mkdir(parents=True, exist_ok=True)

                log.info(f"Scraping {channel} (since_id={since_id})")
                async for msg in client.iter_messages(channel, limit=1000, min_id=(since_id or 0)):
                    rec = {
                        "id": int(msg.id),
                        "channel_name": ch_name,
                        "message_text": getattr(msg, "message", None),
                        "message_date": msg.date.isoformat() if msg.date else None,
                        "has_image": False,
                        "image_path": None,
                    }
                    if isinstance(msg.media, MessageMediaPhoto):
                        try:
                            saved = await msg.download_media(file=(ch_img_dir / f"{msg.id}").as_posix())
                            if saved:
                                rel = Path(saved).resolve().relative_to(Path(".").resolve())
                                rec["has_image"] = True
                                rec["image_path"] = rel.as_posix()
                        except Exception as e:
                            log.warning(f"{channel} msg {msg.id}: image download failed: {e}")
                    out.append(rec)

                (msg_dir / f"{ch_name}.json").write_text(
                    json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
                )
                log.info(f"Saved {len(out)} messages for {channel}")

                if out:
                    max_id = max(m["id"] for m in out)
                    state[channel] = {"last_id": max_id, "last_run": datetime.datetime.utcnow().isoformat()}
                    _save_state(state_file, state)

    asyncio.run(_run())
    return {"date": today, "channels": CHANNELS}
