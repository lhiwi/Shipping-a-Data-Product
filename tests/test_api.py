import requests

def test_health_endpoint():
    r = requests.get("http://localhost:8000/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"