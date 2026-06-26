import httpx

def test_metadata_api_health():
    response = httpx.get(url="http://metadata-api:8000/health")

    assert response.status_code == 200