from dagster import job, op
import subprocess

@op
def scrape_op():
    subprocess.check_call(["python", "-m", "src.scraper.telegram_scraper"])

@op
def load_op():
    subprocess.check_call(["python", "-m", "src.loader.load_raw_to_postgres"])

@op
def dbt_op():
    subprocess.check_call(["bash", "-lc", "cd dbt && dbt run && dbt test"])

@op
def yolo_op():
    subprocess.check_call(["python", "-m", "src.yolo.detect_and_store"])

@job
def pipeline_job():
    yolo_op(dbt_op(load_op(scrape_op())))