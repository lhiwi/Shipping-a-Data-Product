from fastapi import FastAPI, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text

from .database import get_db
from .schemas import HealthOut, ProductCount, ChannelActivityPoint, MessageHit
from . import crud

app = FastAPI(title="Telegram Analytics API", version="0.1.0")

# CORS (permissive for local dev / Streamlit)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- Core endpoints ----------------

@app.get("/api/health", response_model=HealthOut)
def health():
    return HealthOut()

@app.get("/api/reports/top-products", response_model=list[ProductCount])
def top_products(
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    rows = crud.top_terms(db, limit=limit)
    return [{"term": t, "hits": h} for t, h in rows]

@app.get("/api/channels/{channel}/activity", response_model=list[ChannelActivityPoint])
def channel_activity(channel: str, db: Session = Depends(get_db)):
    rows = crud.channel_activity(db, channel)
    return [{"date": d, "messages": m} for d, m in rows]

@app.get("/api/search/messages", response_model=list[MessageHit])
def search_messages(
    query: str,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    rows = crud.search_messages(db, query, limit=limit)
    return [
        {
            "message_id": r[0],
            "channel_name": r[1],
            "message_ts": r[2].isoformat() if r[2] else None,
            "message_text": r[3],
        }
        for r in rows
    ]

@app.get("/")
def root():
    return {"message": "Telegram Analytics API", "docs": "/docs", "health": "/api/health"}


# ---------------- Transparency / Explainability ----------------

@app.get("/api/metrics/ingestion")
def metrics_ingestion(db: Session = Depends(get_db)) -> dict:
    """
    Live ingestion coverage: totals, last timestamp, last 14d daily counts, and per-channel volume.
    """
    # total messages
    total_msgs = db.execute(
        text("select count(*) from analytics.fct_messages")
    ).scalar() or 0

    # last message timestamp
    last_ts = db.execute(
        text("select max(message_ts) from analytics.fct_messages")
    ).scalar()

    # messages per day (last 14 days)  <-- FIXED QUERY (use WHERE then GROUP BY)
    last14 = db.execute(text("""
        select d::date as d, count(*) as c
        from (
          select date_trunc('day', message_ts) as d
          from analytics.fct_messages
          where message_ts >= now() - interval '14 days'
        ) t
        group by 1
        order by 1
    """)).all()
    msgs_daily = [{"date": str(r[0]), "count": int(r[1])} for r in last14]

    # per-channel totals
    by_channel = db.execute(text("""
        select lower(channel_name) as channel, count(*) as c
        from analytics.fct_messages
        group by 1
        order by 2 desc
    """)).all()
    channels = [{"channel": r[0], "count": int(r[1])} for r in by_channel]

    return {
        "total_messages": int(total_msgs),
        "last_message_ts": last_ts.isoformat() if last_ts else None,
        "messages_per_day_14d": msgs_daily,
        "messages_by_channel": channels,
    }


@app.get("/api/metrics/detections")
def metrics_detections(db: Session = Depends(get_db)) -> dict:
    """
    YOLO enrichment transparency: total detections, confidence histogram, top classes.
    Returns 'has_table=False' if enrichment not yet run.
    """
    # Table existence check (safe if enrichment not yet run)
    exists = db.execute(text("select to_regclass('raw.image_detections')")).scalar()
    if not exists:
        return {
            "has_table": False,
            "total_detections": 0,
            "conf_hist": [],
            "top_classes": [],
        }

    total_det = db.execute(
        text("select count(*) from raw.image_detections")
    ).scalar() or 0

    # Confidence histogram (10 bins: 0.0..1.0)
    conf_rows = db.execute(text("""
        with binned as (
          select width_bucket(confidence, 0.0, 1.0, 10) as b
          from raw.image_detections
        )
        select b, count(*) from binned
        group by 1
        order by 1
    """)).all()
    conf_hist = [{"bucket": int(r[0]), "count": int(r[1])} for r in conf_rows]

    # Top classes
    top_cls = db.execute(text("""
        select class_name, count(*) as c
        from raw.image_detections
        group by 1
        order by 2 desc
        limit 20
    """)).all()
    top_classes = [{"class": r[0], "count": int(r[1])} for r in top_cls]

    return {
        "has_table": True,
        "total_detections": int(total_det),
        "conf_hist": conf_hist,
        "top_classes": top_classes,
    }
