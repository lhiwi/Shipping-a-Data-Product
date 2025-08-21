from dagster import Definitions
from dagster_repo.jobs.pipeline import daily_pipeline
from dagster_repo.schedules.daily import daily_schedule

defs = Definitions(
    jobs=[daily_pipeline],
    schedules=[daily_schedule],
)
