
import json, datetime, asyncio
from pathlib import Path
from telethon.tl.types import MessageMediaPhoto
from src.utils.config import TelegramConfig
from .telegram_client import get_client

def _load_state(p: Path) -> dict:
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}

def _save_state(p: Path, state: dict) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(state, indent=2), encoding="utf-8")

async def _scrape_async(cfg: TelegramConfig, base_dir: Path) -> dict:
    # folders
    today = datetime.date.today().isoformat()
    msg_dir = base_dir / "data" / "raw" / "telegram_messages" / today
    img_dir = base_dir / "data" / "raw" / "images" / today
    state_file = base_dir / ".state" / "scrape_state.json"
    msg_dir.mkdir(parents=True, exist_ok=True)
    img_dir.mkdir(parents=True, exist_ok=True)
    state = _load_state(state_file)

    async with get_client(cfg) as client:
        for channel in cfg.channels:
            ch_name = channel.strip("@")
            ch_state = state.get(channel) or {}
            since_id = ch_state.get("last_id")
            out = []
            ch_img_dir = img_dir / ch_name
            ch_img_dir.mkdir(parents=True, exist_ok=True)

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
                            rel = Path(saved).resolve().relative_to(base_dir.resolve())
                            rec["has_image"] = True
                            rec["image_path"] = rel.as_posix()
                    except Exception:
                        pass
                out.append(rec)

            (msg_dir / f"{ch_name}.json").write_text(
                json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            if out:
                max_id = max(m["id"] for m in out)
                state[channel] = {"last_id": max_id, "last_run": datetime.datetime.utcnow().isoformat()}
                _save_state(state_file, state)
    return {"date": today, "channels": list(cfg.channels)}

def scrape_to_raw(base_dir: str | Path = ".") -> dict:
    cfg = TelegramConfig()
    return asyncio.run(_scrape_async(cfg, Path(base_dir)))
