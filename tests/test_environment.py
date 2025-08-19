import os
import pytest
import psycopg2

def test_env_vars_present():
    required = [
        "POSTGRES_HOST","POSTGRES_PORT","POSTGRES_DB","POSTGRES_USER","POSTGRES_PASSWORD"
    ]
    for k in required:
        assert os.getenv(k), f"Missing env var: {k}"

@pytest.mark.integration
def test_postgres_connection():
    conn = psycopg2.connect(
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
    )
    cur = conn.cursor()
    cur.execute("select 1")
    assert cur.fetchone()[0] == 1
    conn.close()