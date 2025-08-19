import os
import json
from pathlib import Path
from loguru import logger
from sqlalchemy import text
from api.database import engine

RAW_SCHEMA = os.getenv("DBT_RAW_SCHEMA", "raw")
DATA_DIR = Path("data/raw/telegram_messages")

DDL = f"""create schema if not exists {RAW_SCHEMA};
create table if not exists {RAW_SCHEMA}.telegram_messages (
  id bigint primary key,
  channel_name text,
  message_text text,
  message_date timestamp,
  has_image boolean,
  image_path text
);
"""

INSERT = text(
    f"""    insert into {RAW_SCHEMA}.telegram_messages
    (id, channel_name, message_text, message_date, has_image, image_path)
    values (:id, :channel_name, :message_text, :message_date, :has_image, :image_path)
    on conflict (id) do nothing
    """
)

def load():
    with engine.begin() as conn:
        conn.exec_driver_sql(DDL)
        if not DATA_DIR.exists():
            logger.warning(f"No data dir {DATA_DIR}.")
            return
        files = list(DATA_DIR.rglob("*.json"))
        logger.info(f"Found {len(files)} json files")
        for fp in files:
            rows = json.loads(fp.read_text(encoding="utf-8"))
            for r in rows:
                conn.execute(INSERT, {
                    "id": r.get("id"),
                    "channel_name": r.get("channel_name"),
                    "message_text": r.get("message_text"),
                    "message_date": r.get("message_date"),
                    "has_image": r.get("has_image"),
                    "image_path": r.get("image_path"),
                })
            logger.info(f"Loaded {len(rows)} rows from {fp}")

if __name__ == "__main__":
    load()