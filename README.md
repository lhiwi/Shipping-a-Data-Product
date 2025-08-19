# Shipping a Data Product (Week 7)
End-to-end ELT product: Telegram scraping → Postgres (raw) → dbt (staging/marts) → YOLOv8 enrichment → FastAPI API → Dagster orchestration.

## 1) Clone & Configure
```bash
git clone <your-repo-url>
cd Shipping-a-Data-Product
cp .env.example .env
# edit .env with your credentials
```

## 2) Bring Up Services
```bash
docker compose up -d db
# wait for DB healthy, then
docker compose up api
# (Optional) Dagster UI
docker compose up dagster
```
- FastAPI docs: http://localhost:8000/docs
- Dagster: http://localhost:3000

## 3) Initialize Database (Raw Table)
```bash
docker compose exec api python -m src.loader.load_raw_to_postgres
```

## 4) Run dbt
```bash
docker compose exec api bash -lc "cd dbt && dbt debug && dbt run && dbt test"
```

## 5) YOLO Enrichment
```bash
docker compose exec api python -m src.yolo.detect_and_store
# then run dbt again if marts depend on enrichment
```

## 6) API Endpoints
- `GET /health`
- `GET /api/reports/top-products?limit=10`
- `GET /api/channels/{channel_name}/activity`
- `GET /api/search/messages?query=paracetamol`

## 7) Dagster Orchestration
Graph: scrape → load → dbt → yolo. Run locally:
```bash
docker compose up dagster
```

## 8) Tests
```bash
docker compose exec api pytest -q
```

## Data Layout
- `data/raw/telegram_messages/YYYY-MM-DD/*.json`
- `data/raw/images/*.jpg`