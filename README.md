#  Shipping a Data Product: From Raw Telegram Data to Analytical API

This project (10 Academy Week 7) demonstrates the full lifecycle of building and shipping a production-ready **data product** — from raw unstructured data collection to an orchestrated analytical pipeline.

---

##  Project Overview
The project involves designing a data pipeline that ingests raw messages from Ethiopian medical business Telegram channels, enriches them with **YOLOv8 object detection**, structures them into a **dimensional warehouse (dbt)**, and exposes insights via an **analytical API** orchestrated with **Dagster**.

The pipeline supports:

* **Scraping** Telegram messages and images.
* **Transforming** data into warehouse-ready models.
* **Enriching** images with object detection.
* **Serving** insights with FastAPI endpoints.
* **Orchestrating** pipelines with Dagster schedules.

---

##  Repository Structure

```
Shipping-a-Data-Product/
│
├── notebooks/                # Jupyter notebooks for exploration & enrichment
│   ├── 01_bootstrap_session.ipynb
│   ├── 02_scrape_channels.ipynb
│   ├── 03_load_to_postgres.ipynb
│   └── 04_yolo_enrichment.ipynb
│
├── scripts/                  # Python scripts for ETL tasks
│   ├── scrape.py
│   ├── load.py
│   ├── enrich.py
│   └── validate_notebooks.py
│
├── dbt/                      # dbt project for data warehouse
│   ├── models/
│   │   ├── staging/
│   │   ├── marts/
│   │   └── ...
│   ├── dbt_project.yml
│   └── profiles.yml
│
├── api/                      # FastAPI app
│   ├── main.py
│   └── routers/
│
├── dagster_repo/             # Dagster orchestration repo
│   ├── repository.py
│   └── jobs.py
│
├── requirements.txt          # Python dependencies
└── README.md                 # Project documentation
```

---

## 🛠️ Setup & Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/<your-username>/Shipping-a-Data-Product.git
   cd Shipping-a-Data-Product
   ```

2. **Create and activate virtual environment**

   ```bash
   python -m venv .venv
   .venv\Scripts\activate   # Windows
   source .venv/bin/activate # Linux/Mac
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**

   * Add `.env` with your Postgres and Telegram credentials.

---

## Pipeline Workflow

### 1 Scraping Telegram Data

* Bootstrap Telegram client session.
* Scrape messages and images from target channels.
* Store raw data in Postgres (`raw_telegram_messages`).

### 2 Data Warehouse (dbt)

* Transform raw data into staging + mart models.
* Run tests for data quality and integrity.

```bash
cd dbt
dbt debug --profiles-dir .
dbt run   --profiles-dir .
dbt test  --profiles-dir .
```

### 3 YOLOv8 Enrichment

* Run object detection on scraped images.
* Store enriched results in `image_detections` tables.

### 4 API (FastAPI)

* Serve insights at `http://127.0.0.1:8000/docs`.
* Example endpoints:

  * `/messages` → Query channel messages.
  * `/detections` → Query object detections.

```bash
uvicorn api.main:app --reload
```

### 5️ Orchestration (Dagster)

* Define jobs and schedules in `dagster_repo/`.
* Start Dagster UI:

  ```bash
  dagit -w workspace.yaml
  ```
* Monitor and trigger pipelines via Dagster dashboard.

---

