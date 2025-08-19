from dagster import Definitions
from dagster_repo.jobs.pipeline import pipeline_job

repo = Definitions(jobs=[pipeline_job])