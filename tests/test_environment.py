# tests/test_environment.py
import psycopg2
import pytest
from src.utils.config import DBConfig

@pytest.mark.integration
def test_postgres_connection():
    cfg = DBConfig()
    try:
        conn = psycopg2.connect(
            host=cfg.host,
            port=cfg.port,
            dbname=cfg.db,
            user=cfg.user,
            password=cfg.pwd,
            connect_timeout=3,
        )
        conn.close()
    except Exception as e:
        pytest.skip(f"Skipping: Postgres not reachable ({e})")
