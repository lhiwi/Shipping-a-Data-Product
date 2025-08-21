from fastapi import FastAPI, Depends, Query
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os

DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "postgres")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "telegram_dw")
DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI(title="Telegram Analytics API", version="1.0.0")

@app.get("/")
def root():
    return {"message": "Telegram Analytics API", "docs": "/docs", "health": "/api/health"}

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.get("/api/reports/top-products")
def top_products(limit: int = Query(10, ge=1, le=100)):
    with engine.connect() as conn:
        rows = conn.execute(text("""
            with tokens as (
              select lower(unnest(string_to_array(regexp_replace(message_text, '[^a-zA-Z0-9 ]', ' ', 'g'), ' '))) as term
              from analytics.fct_messages
              where message_text is not null and length(message_text) > 0
            )
            select term, count(*) as hits
            from tokens
            where length(term) >= 3
            group by 1
            order by hits desc
            limit :limit
        """), {"limit": limit}).all()
        return [{"term": r[0], "hits": r[1]} for r in rows]

@app.get("/api/channels/{channel}/activity")
def channel_activity(channel: str):
    with engine.connect() as conn:
        rows = conn.execute(text("""
            select to_char(message_ts::date, 'YYYY-MM-DD') as d, count(*) as messages
            from analytics.fct_messages
            where lower(channel_name) = lower(:channel)
            group by 1 order by 1
        """), {"channel": channel}).all()
        return [{"date": r[0], "messages": r[1]} for r in rows]

@app.get("/api/search/messages")
def search_messages(query: str, limit: int = Query(50, ge=1, le=200)):
    with engine.connect() as conn:
        rows = conn.execute(text("""
            select message_id, channel_name, message_ts, substring(coalesce(message_text, ''), 1, 300) as snippet
            from analytics.fct_messages
            where message_text ilike :q
            order by message_ts desc
            limit :limit
        """), {"q": f"%{query}%", "limit": limit}).all()
        return [
            {
                "message_id": r[0],
                "channel_name": r[1],
                "message_ts": r[2].isoformat() if r[2] else None,
                "message_text": r[3],
            } for r in rows
        ]
