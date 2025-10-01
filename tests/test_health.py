def test_health_check(test_client):
    resp = test_client.get("/health")
    assert resp.status_code == 200
