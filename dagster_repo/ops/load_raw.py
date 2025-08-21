from dagster import op, get_dagster_logger
import os, json, glob
from pathlib import Path
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import execute_values

@op
def load_raw_to_postgres(context):
    """Load JSON files from data/raw/telegram_messages/<date> into raw.telegram_messages."""
    log = get_dagster_logger()
    load_dotenv(".env")

    host = os.getenv("POSTGRES_HOST", "localhost")
    port = int(os.getenv("POSTGRES_PORT", "5432"))
    db   = os.getenv("POSTGRES_DB", "telegram_dw")
    user = os.getenv("POSTGRES_USER", "postgres")
    pwd  = os.getenv("POSTGRES_PASSWORD", "postgres")

    conn = psycopg2.connect(host=host, port=port, dbname=db, user=user, password=pwd)
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

    base = Path("data/raw/telegram_messages")
    dates = sorted([p for p in base.glob("*") if p.is_dir()])
    if not dates:
        log.warning("No telegram_messages date folders found.")
        cur.close(); conn.close()
        return {"inserted": 0}

    latest = dates[-1]
    files = glob.glob(str(latest / "*.json"))
    inserted = 0
    for f in files:
        rows = []
        data = json.loads(Path(f).read_text(encoding="utf-8"))
        for r in data:
            rows.append((
                int(r["id"]),
                r.get("channel_name"),
                r.get("message_text"),
                r.get("message_date"),
                bool(r.get("has_image")),
                r.get("image_path"),
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
    log.info(f"Inserted {inserted} rows into raw.telegram_messages from {latest}")
    return {"inserted": inserted, "date": latest.name}
