import httpx


METADATA_API_BASE_URL = "http://metadata-api:8000"


def test_root_endpoint():
    res = httpx.get(
        url=f"{METADATA_API_BASE_URL}/"
    )

    assert res.status_code == 200

    payload = res.json()

    assert "title" in payload
    assert "description" in payload
    assert "links" in payload
    assert "datasets" in payload


def test_example_dataset():
    res = httpx.get(
        url=f"{METADATA_API_BASE_URL}/dataset/broke-west-fish"
    )

    assert res.status_code == 200
    assert res.headers["Content-Type"] == "application/ld+json"

    payload = res.json()

    assert "licensed" in payload["dataset"]
    assert "geographicCoverage" in payload["dataset"]["coverage"]
    assert "temporalCoverage" in payload["dataset"]["coverage"]
    #
    assert "citation" in payload["additionalMetadata"]["metadata"]["gbif"]


def test_nonexistant_dataset():
    res = httpx.get(
        url=f"{METADATA_API_BASE_URL}/dataset/nonexistant-dataset"
    )

    assert res.status_code == 404


def test_metadata_search():
    res = httpx.get(
        url=f"{METADATA_API_BASE_URL}/datasets/search",
        params={
            "min_lon": "-180.0",
            "min_lat": "-90.0",
            "max_lon": "180.0",
            "max_lat": "90.0",
            "begin_date": "0001-01-01",
            "end_date": "2100-12-31",
        }
    )

    assert res.status_code == 200
    assert res.json() is not None


def test_metadata_search_licenses():
    res = httpx.get(
        url=f"{METADATA_API_BASE_URL}/datasets/search",
        params={
            "licenses": ["CC0-1.0", "CC-BY-4.0"],
        }
    )

    assert res.status_code == 200