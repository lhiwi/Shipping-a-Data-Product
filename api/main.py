from fastapi import FastAPI, Depends, Query
from sqlalchemy.orm import Session
from .database import get_db
from .schemas import HealthOut, ProductCount, ChannelActivityPoint, MessageHit
from . import crud

app = FastAPI(title="Telegram Analytics API", version="0.1.0")
# at top of api/main.py
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)
@app.get("/api/health", response_model=HealthOut)
def health():
    return HealthOut()

@app.get("/api/reports/top-products", response_model=list[ProductCount])
def top_products(limit: int = Query(10, ge=1, le=100), db: Session = Depends(get_db)):
    rows = crud.top_terms(db, limit=limit)
    return [{"term": t, "hits": h} for t, h in rows]

@app.get("/api/channels/{channel}/activity", response_model=list[ChannelActivityPoint])
def channel_activity(channel: str, db: Session = Depends(get_db)):
    rows = crud.channel_activity(db, channel)
    return [{"date": d, "messages": m} for d, m in rows]

@app.get("/api/search/messages", response_model=list[MessageHit])
def search_messages(query: str, limit: int = Query(50, ge=1, le=200), db: Session = Depends(get_db)):
    rows = crud.search_messages(db, query, limit=limit)
    return [
        {
            "message_id": r[0],
            "channel_name": r[1],
            "message_ts": r[2].isoformat() if r[2] else None,
            "message_text": r[3],
        } for r in rows
    ]
@app.get("/")
def root():
    return {"message": "Telegram Analytics API", "docs": "/docs", "health": "/api/health"}
