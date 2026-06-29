import asyncio
#
import httpx
import pytest


METADATA_API_BASE_URL = "http://metadata-api:8000"
#
TEST_DATASET_ID = "broke-west-fish"
DEFAULT_SEARCH_VALS = {
    "min_lon": "-180.0",
    "min_lat": "-90.0",
    "max_lon": "180.0",
    "max_lat": "90.0",
    "begin_date": "0001-01-01",
    "end_date": "2038-01-19",
}


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


def test_health_endpoint():
    res = httpx.get(f"{METADATA_API_BASE_URL}/health")

    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


def test_list_datasets_default_page():
    res = httpx.get(f"{METADATA_API_BASE_URL}/datasets")

    assert res.status_code == 200

    payload = res.json()

    assert "page" in payload
    assert "page_size" in payload
    assert "total" in payload
    assert "datasets" in payload
    assert isinstance(payload["datasets"], dict)
    assert payload["page"] == 1
    assert payload["page_size"] == 10


def test_list_datasets_pagination():
    page1 = httpx.get(
        f"{METADATA_API_BASE_URL}/datasets",
        params={"page": 1, "page_size": 2}
    ).json()
    page2 = httpx.get(
        f"{METADATA_API_BASE_URL}/datasets",
        params={"page": 2, "page_size": 2}
    ).json()

    assert page1["total"] == page2["total"]
    assert set(page1["datasets"].keys()).isdisjoint(set(page2["datasets"].keys()))


def test_list_datasets_invalid_page_size():
    res = httpx.get(
        f"{METADATA_API_BASE_URL}/datasets",
        params={"page_size": 9999}
    )

    assert res.status_code == 422


def test_example_dataset():
    res = httpx.get(
        url=f"{METADATA_API_BASE_URL}/dataset/{TEST_DATASET_ID}"
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
        params=DEFAULT_SEARCH_VALS,
    )

    payload = res.json()

    assert "datasets" in payload
    assert isinstance(payload["datasets"], list)
    assert len(payload["datasets"]) > 0


def test_metadata_search_licenses():
    res = httpx.get(
        url=f"{METADATA_API_BASE_URL}/datasets/search",
        params={
            "licenses": ["CC0-1.0", "CC-BY-4.0"],
        }
    )

    assert res.status_code == 200


def test_metadata_search_impossible_license():
    res = httpx.get(
        url=f"{METADATA_API_BASE_URL}/datasets/search",
        params={
            "licenses": ["XYZ-PL0"],
        }
    )

    assert res.status_code == 200
    assert res.json()["datasets"] == []


def test_metadata_search_min_lon_gt_180():
    res = httpx.get(
        url=f"{METADATA_API_BASE_URL}/datasets/search",
        params={
            "min_lon": 195.0,
        }
    )

    assert res.status_code == 422

    body = res.json()

    assert body["detail"][0]["type"] == "less_than_equal"
    assert body["detail"][0]["loc"] == ["query", "min_lon"]
    assert body["detail"][0]["msg"] == "Input should be less than or equal to 180"


def test_metadata_search_min_lon_lt_m180():
    res = httpx.get(
        url=f"{METADATA_API_BASE_URL}/datasets/search",
        params={
            "min_lon": -195.0,
        }
    )

    assert res.status_code == 422

    body = res.json()

    assert body["detail"][0]["type"] == "greater_than_equal"
    assert body["detail"][0]["loc"] == ["query", "min_lon"]
    assert body["detail"][0]["msg"] == "Input should be greater than or equal to -180"


def test_metadata_search_max_lon_gt_180():
    res = httpx.get(
        url=f"{METADATA_API_BASE_URL}/datasets/search",
        params={
            "max_lon": 195.0,
        }
    )

    assert res.status_code == 422

    body = res.json()

    assert body["detail"][0]["type"] == "less_than_equal"
    assert body["detail"][0]["loc"] == ["query", "max_lon"]
    assert body["detail"][0]["msg"] == "Input should be less than or equal to 180"


def test_metadata_search_max_lon_lt_m180():
    res = httpx.get(
        url=f"{METADATA_API_BASE_URL}/datasets/search",
        params={
            "max_lon": -195.0,
        }
    )

    assert res.status_code == 422

    body = res.json()

    assert body["detail"][0]["type"] == "greater_than_equal"
    assert body["detail"][0]["loc"] == ["query", "max_lon"]
    assert body["detail"][0]["msg"] == "Input should be greater than or equal to -180"


def test_metadata_search_min_lat_gt_90():
    res = httpx.get(
        url=f"{METADATA_API_BASE_URL}/datasets/search",
        params={
            "min_lat": 95.0,
        }
    )

    assert res.status_code == 422

    body = res.json()

    assert body["detail"][0]["type"] == "less_than_equal"
    assert body["detail"][0]["loc"] == ["query", "min_lat"]
    assert body["detail"][0]["msg"] == "Input should be less than or equal to 90"


def test_metadata_search_min_lat_lt_m90():
    res = httpx.get(
        url=f"{METADATA_API_BASE_URL}/datasets/search",
        params={
            "min_lat": -95.0,
        }
    )

    assert res.status_code == 422

    body = res.json()

    assert body["detail"][0]["type"] == "greater_than_equal"
    assert body["detail"][0]["loc"] == ["query", "min_lat"]
    assert body["detail"][0]["msg"] == "Input should be greater than or equal to -90"


def test_metadata_search_max_lat_gt_90():
    res = httpx.get(
        url=f"{METADATA_API_BASE_URL}/datasets/search",
        params={
            "max_lat": 95.0,
        }
    )

    assert res.status_code == 422

    body = res.json()

    assert body["detail"][0]["type"] == "less_than_equal"
    assert body["detail"][0]["loc"] == ["query", "max_lat"]
    assert body["detail"][0]["msg"] == "Input should be less than or equal to 90"


def test_metadata_search_max_lat_lt_m90():
    res = httpx.get(
        url=f"{METADATA_API_BASE_URL}/datasets/search",
        params={
            "max_lat": -95.0,
        }
    )

    assert res.status_code == 422

    body = res.json()

    assert body["detail"][0]["type"] == "greater_than_equal"
    assert body["detail"][0]["loc"] == ["query", "max_lat"]
    assert body["detail"][0]["msg"] == "Input should be greater than or equal to -90"


def test_citations_known_dataset():
    res = httpx.post(
        f"{METADATA_API_BASE_URL}/datasets/citations",
        json={
            "dataset_names": [TEST_DATASET_ID],
        },
    )

    assert res.status_code == 200

    payload = res.json()

    assert "citations" in payload
    assert len(payload["citations"]) == 1
    assert payload["citations"][0] is not None


def test_citations_unknown_dataset_returns_empty():
    res = httpx.post(
        f"{METADATA_API_BASE_URL}/datasets/citations",
        json={
            "dataset_names": ["imaginary-key-xyz"],
        },
    )

    assert res.status_code == 200
    assert res.json()["citations"] == []


@pytest.mark.asyncio
async def test_metadata_search_concurrent():
    async with httpx.AsyncClient() as client:
        async def make_request():
            res = await client.get(
                url=f"{METADATA_API_BASE_URL}/datasets/search",
                params=DEFAULT_SEARCH_VALS,
            )

            assert res.status_code == 200
            assert res.json() is not None

        await asyncio.gather(*(make_request() for _ in range(20)))