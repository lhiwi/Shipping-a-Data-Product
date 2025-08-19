from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from api.database import SessionLocal
from api import crud

app = FastAPI(title="Telegram Analytical API", version="0.1.0")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/api/reports/top-products")
def top_products(limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_top_products(db, limit)

@app.get("/api/channels/{channel_name}/activity")
def channel_activity(channel_name: str, db: Session = Depends(get_db)):
    return crud.get_channel_activity(db, channel_name)

@app.get("/api/search/messages")
def search(query: str, db: Session = Depends(get_db)):
    return crud.search_messages(db, query)