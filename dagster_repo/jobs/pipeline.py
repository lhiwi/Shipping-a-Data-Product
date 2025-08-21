from dagster import job
from dagster_repo.ops.scrape import scrape_telegram_data
from dagster_repo.ops.load_raw import load_raw_to_postgres
from dagster_repo.ops.run_dbt import run_dbt_models
from dagster_repo.ops.run_yolo import run_yolo_enrichment

@job(tags={"owner": "you", "project": "telegram-data-product"})
def daily_pipeline():
    # Order: scrape -> load -> dbt -> yolo -> dbt (optional second pass for detection marts)
    s = scrape_telegram_data()
    l = load_raw_to_postgres()
    d = run_dbt_models()
    y = run_yolo_enrichment()
   
