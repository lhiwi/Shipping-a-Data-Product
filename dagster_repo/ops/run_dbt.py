from dagster import op, get_dagster_logger
import subprocess, sys, os

@op
def run_dbt_models():
    """Run dbt (staging + marts). Uses dbt/ as the project dir."""
    log = get_dagster_logger()
    project_dir = "dbt"
    profiles_dir = "dbt"
    env = os.environ.copy()

    def _cmd(args):
        log.info("Running: " + " ".join(args))
        proc = subprocess.run(args, env=env, capture_output=True, text=True)
        if proc.returncode != 0:
            log.error(proc.stdout)
            log.error(proc.stderr)
            raise RuntimeError(f"Command failed: {' '.join(args)}")
        log.info(proc.stdout)

    _cmd([sys.executable, "-m", "dbt", "deps", "--project-dir", project_dir, "--profiles-dir", profiles_dir])
    _cmd([sys.executable, "-m", "dbt", "run",  "--project-dir", project_dir, "--profiles-dir", profiles_dir])
    _cmd([sys.executable, "-m", "dbt", "test", "--project-dir", project_dir, "--profiles-dir", profiles_dir])

    return {"status": "ok"}
