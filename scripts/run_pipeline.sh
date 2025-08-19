#!/usr/bin/env bash
set -euo pipefail
python -m src.scraper.telegram_scraper
python -m src.loader.load_raw_to_postgres
bash -lc "cd dbt && dbt run && dbt test"
python -m src.yolo.detect_and_store