from dagster import ScheduleDefinition
from dagster_repo.jobs.pipeline import daily_pipeline

# Runs every day at 09:00 local time
daily_schedule = ScheduleDefinition(
    name="daily_0900",
    cron_schedule="0 9 * * *",
    job=daily_pipeline,
)
