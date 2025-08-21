import os, json, glob, psycopg2
from pathlib import Path
from psycopg2.extras import execute_values
from src.utils.config import DBConfig

def ensure_raw_tables(cfg: DBConfig):
    conn = psycopg2.connect(host=cfg.host, port=cfg.port, dbname=cfg.db, user=cfg.user, password=cfg.pwd)
    cur = conn.cursor()
    cur.execute("create schema if not exists raw;")
    cur.execute("""
    create table if not exists raw.telegram_messages (
      id bigint primary key,
      channel_name text,
      message_text text,
      message_date timestamptz,
      has_image boolean,
      image_path text
    );
    """)
    conn.commit()
    cur.close(); conn.close()

def load_latest_raw_json(base_dir: str | Path = ".") -> dict:
    cfg = DBConfig()
    ensure_raw_tables(cfg)
    conn = psycopg2.connect(host=cfg.host, port=cfg.port, dbname=cfg.db, user=cfg.user, password=cfg.pwd)
    cur = conn.cursor()

    base = Path(base_dir) / "data" / "raw" / "telegram_messages"
    dates = sorted([p for p in base.glob("*") if p.is_dir()])
    if not dates:
        cur.close(); conn.close()
        return {"inserted": 0, "date": None}

    latest = dates[-1]
    files = glob.glob(str(latest / "*.json"))
    inserted = 0
    for f in files:
        rows = []
        data = json.loads(Path(f).read_text(encoding="utf-8"))
        for r in data:
            rows.append((
                int(r["id"]), r.get("channel_name"), r.get("message_text"),
                r.get("message_date"), bool(r.get("has_image")), r.get("image_path"),
            ))
        if rows:
            execute_values(cur, """
              insert into raw.telegram_messages (id, channel_name, message_text, message_date, has_image, image_path)
              values %s
              on conflict (id) do nothing
            """, rows)
            inserted += len(rows)

    conn.commit()
    cur.close(); conn.close()
    return {"inserted": inserted, "date": latest.name}
