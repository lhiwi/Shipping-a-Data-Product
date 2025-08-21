#  Shipping a Data Product: From Raw Telegram Data to Analytical API & Dashboard

A comprehensive data engineering project demonstrating the full lifecycle of building a production-ready data product — from raw unstructured data collection to a dimensional warehouse, enrichment with AI, an analytical API, and transparent explainability features.

---

## 📋 Project Overview

This project ingests raw messages from Ethiopian medical business Telegram channels, enriches them with **YOLOv8 object detection**, structures them into a **dbt-powered dimensional warehouse**, and exposes insights through both:
- a **FastAPI analytical API** (Week 7)
- a **Streamlit dashboard for transparency and explainability** (Week 12)

The pipeline is orchestrated with **Dagster** and tested continuously with **CI/CD (GitHub Actions + pytest)**.

---

##  Repository Structure

```bash
Shipping-a-Data-Product/
├── notebooks/                   # Jupyter notebooks for prototyping & EDA
│   ├── 01_bootstrap_session.ipynb
│   ├── 02_scrape_channels.ipynb
│   ├── 03_load_to_postgres.ipynb
│   └── 04_yolo_enrichment.ipynb
│
├── scripts/                     # ETL scripts (production-ready)
│   ├── scrape.py
│   ├── load.py
│   └── enrich.py
│
├── src/                         # Core Python package
│   ├── utils/                   # Configs & helpers
│   ├── ingestion/               # Data ingestion logic
│   ├── enrichment/              # YOLO object detection
│   └── __init__.py
│
├── dbt/                         # Data transformation layer
│   ├── models/
│   │   ├── staging/
│   │   └── marts/
│   ├── dbt_project.yml
│   └── profiles.yml
│
├── api/                         # FastAPI app
│   ├── main.py                  # API entry point
│   ├── crud.py                  # Database queries
│   ├── schemas.py               # Pydantic models
│   ├── database.py              # DB session config
│   └── routers/                 # Modular endpoints
│
├── streamlit_app.py             # Streamlit dashboard (Week 12)
│
├── dagster_repo/                # Orchestration layer
│   ├── repository.py
│   └── jobs.py
│
├── tests/                       # Unit & integration tests
│   ├── test_api.py
│   ├── test_ingestion.py
│   ├── test_enrichment.py
│   └── test_environment.py
│
├── .github/workflows/ci.yml     # CI/CD pipeline
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
└── README.md                    # Project documentation
````

---

## Pipeline Workflow

### **1. Data Ingestion**

* Scrape Telegram messages and images (`scripts/scrape.py`).
* Load into PostgreSQL (`raw_telegram_messages`).

### **2. Data Transformation (dbt)**

* Staging models for cleaning/normalization.
* Mart models for analytics queries.
* Run with:

  ```bash
  cd dbt
  dbt run --profiles-dir .
  dbt test --profiles-dir .
  ```

### **3. Image Enrichment**

* YOLOv8 detection on scraped images.
* Store detections in `image_detections` table.

### **4. API Service (Week 7)**

* Exposes insights via FastAPI.
* Docs: `http://127.0.0.1:8000/docs`
* Run with:

  ```bash
  uvicorn api.main:app --reload
  ```

### **5. Orchestration**

* Pipelines scheduled and monitored via Dagster.
* Start dashboard:

  ```bash
  dagit -w workspace.yaml
  ```

### **6. Transparency & Dashboard (Week 12)**

* Streamlit dashboard to visualize ingestion trends and detections.
* Run with:

  ```bash
  streamlit run streamlit_app.py
  ```

---

## API Endpoints

| Endpoint                           | Method | Description                            |
| ---------------------------------- | ------ | -------------------------------------- |
| `/api/health`                      | GET    | Service health check                   |
| `/api/reports/top-products`        | GET    | Top mentioned products                 |
| `/api/channels/{channel}/activity` | GET    | Channel activity over time             |
| `/api/search/messages`             | GET    | Full-text search                       |
| `/api/metrics/ingestion`           | GET    | Messages ingested/day (last 14 days)   |
| `/api/metrics/detections`          | GET    | Object detection counts (last 14 days) |

---

##  Tech Stack

* **ETL & Processing**: Python, Pandas, SQLAlchemy
* **Database**: PostgreSQL
* **Data Modeling**: dbt
* **API**: FastAPI
* **Visualization**: Streamlit
* **Orchestration**: Dagster
* **Computer Vision**: YOLOv8 (Ultralytics)
* **CI/CD**: GitHub Actions + pytest

---

##  Week-by-Week

### **Week 7 – Foundations**

* Telegram scraping + ingestion
* dbt warehouse modeling
* YOLOv8 enrichment
* FastAPI analytical endpoints

### **Week 12 – Transparency**

* New explainability endpoints
* Streamlit dashboard
* CI/CD with GitHub Actions

---

## Quick Start

1. **Clone repo**

   ```bash
   git clone https://github.com/<your-username>/Shipping-a-Data-Product.git
   cd Shipping-a-Data-Product
   ```
2. **Setup environment**

   ```bash
   python -m venv .venv
   .venv\Scripts\activate   # Windows
   source .venv/bin/activate # Linux/Mac
   pip install -r requirements.txt
   ```
3. **Configure `.env`**
   Copy `.env.example` → `.env` and fill in credentials.
4. **Run API**

   ```bash
   uvicorn api.main:app --reload
   ```
5. **Run Dashboard**

   ```bash
   streamlit run streamlit_app.py
   ```


