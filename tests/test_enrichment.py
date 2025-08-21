import psycopg2
import pytest
from src.utils.config import DBConfig
from src.enrichment.yolo import ensure_detection_table

@pytest.mark.integration
def test_detection_table_creation_smoke():
    cfg = DBConfig()
    try:
        # Try to connect; if it fails, skip (no DB running locally)
        conn = psycopg2.connect(
            host=cfg.host, port=cfg.port, dbname=cfg.db, user=cfg.user, password=cfg.pwd, connect_timeout=3
        )
        conn.close()
    except Exception as e:
        pytest.skip(f"Skipping: Postgres not available ({e})")

    # If we got here, DB is reachable; the call should not raise
    ensure_detection_table(cfg)
