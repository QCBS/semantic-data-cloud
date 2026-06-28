import asyncio
import time
#
import httpx
import pytest


FASTAPROXY_BASE_URL = "http://fastaproxy:8000"
TIMEOUT_VAL = 60.0
#
OCCURRENCE_QUERY = "PREFIX dwc: <http://rs.tdwg.org/dwc/terms/> SELECT ?occ WHERE { ?occ a dwc:Occurrence } LIMIT 1"
NAMED_VAR_QUERY = "PREFIX dwc: <http://rs.tdwg.org/dwc/terms/> SELECT ?occ ?sciName WHERE { ?occ a dwc:Occurrence ; dwc:scientificName ?sciName . } LIMIT 5"
EVENT_QUERY = "PREFIX dwc: <http://rs.tdwg.org/dwc/terms/> SELECT ?evt WHERE { ?occ a dwc:Event } LIMIT 1"


def test_health_endpoint():
    res = httpx.get(f"{FASTAPROXY_BASE_URL}/health")

    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


def test_sparql_endpoint():
    res = httpx.post(
        url=f"{FASTAPROXY_BASE_URL}/sparql",
        json={
            "query": OCCURRENCE_QUERY
        },
        timeout=TIMEOUT_VAL,
    )

    body = res.json()

    assert res.status_code == 200
    assert set(body) == {"head", "results"}
    assert isinstance(body["head"], dict)
    assert isinstance(body["results"], dict)

    assert "vars" in body["head"]
    assert isinstance(body["head"]["vars"], list)
    assert "occ" in body["head"]["vars"]

    assert "bindings" in body["results"]
    assert isinstance(body["results"]["bindings"], list)
    assert len(body["results"]["bindings"]) > 0


def test_sparql_response_binding_shape():
    res = httpx.post(
        url=f"{FASTAPROXY_BASE_URL}/sparql",
        json={
            "query": NAMED_VAR_QUERY,
        },
        timeout=TIMEOUT_VAL,
    )

    assert res.status_code == 200

    body = res.json()

    declared_vars = set(body["head"]["vars"])

    for binding in body["results"]["bindings"]:
        assert isinstance(binding, dict)
        assert set(binding.keys()).issubset(declared_vars)
        for val in binding.values():
            assert "type" in val


def test_sparql_with_explicit_default_search_vals():
    res = httpx.post(
        url=f"{FASTAPROXY_BASE_URL}/sparql",
        json={
            "query": OCCURRENCE_QUERY,
            "bbox": [-180.0, -90.0, 180.0, 90.0],
            "temporal": ["0001-01-01", "2038-01-19"],
        },
        timeout=TIMEOUT_VAL,
    )

    assert res.status_code == 200
    body = res.json()
    assert len(body["results"]["bindings"]) > 0


def test_sparql_with_license_filter():
    res = httpx.post(
        url=f"{FASTAPROXY_BASE_URL}/sparql",
        json={
            "query": OCCURRENCE_QUERY,
            "licenses": ["CC0-1.0", "CC-BY-4.0"],
        },
        timeout=TIMEOUT_VAL,
    )

    assert res.status_code in (200, 404)

    if res.status_code == 200:
        body = res.json()
        assert "head" in body
        assert "results" in body


def test_sparql_no_datasets_found_returns_404():
    res = httpx.post(
        url=f"{FASTAPROXY_BASE_URL}/sparql",
        json={
            "query": OCCURRENCE_QUERY,
            "licenses": ["XYZ-PL0"],
        },
        timeout=TIMEOUT_VAL,
    )

    assert res.status_code == 404

    body = res.json()

    assert "detail" in body


def test_missing_query():
    res = httpx.post(
        url=f"{FASTAPROXY_BASE_URL}/sparql",
        json={},
    )

    body = res.json()

    assert res.status_code == 422
    assert body["detail"][0]["type"] == "missing"
    assert body["detail"][0]["loc"] == ["body", "query"]


def test_missing_spatial_value():
    res = httpx.post(
        url=f"{FASTAPROXY_BASE_URL}/sparql",
        json={
            "bbox": [-74.0684, 4.5958, -74.0684],
            "query": "PREFIX dwc: <http://rs.tdwg.org/dwc/terms/> SELECT ?occ WHERE { ?occ a dwc:Occurrence } LIMIT 1",
        },
    )

    body = res.json()

    assert res.status_code == 422
    assert body["detail"][0]["type"] == "value_error"


def test_non_numeric_spatial_value():
    res = httpx.post(
        url=f"{FASTAPROXY_BASE_URL}/sparql",
        json={
            "bbox": [-74.0684, 4.5958, -74.0684, "pumpernickel"],
            "query": "PREFIX dwc: <http://rs.tdwg.org/dwc/terms/> SELECT ?occ WHERE { ?occ a dwc:Occurrence } LIMIT 1",
        },
    )

    body = res.json()

    assert res.status_code == 422
    assert body["detail"][0]["type"] == "float_parsing"


def test_non_iso_8601_date():
    res = httpx.post(
        url=f"{FASTAPROXY_BASE_URL}/sparql",
        json={
            "temporal": ["08/15/89", "08/21/89"],
            "query": "PREFIX dwc: <http://rs.tdwg.org/dwc/terms/> SELECT ?occ WHERE { ?occ a dwc:Occurrence } LIMIT 1",
        },
    )

    body = res.json()

    assert res.status_code == 422
    assert body["detail"][0]["type"] == "value_error"


def test_missing_prefix():
    res = httpx.post(
        url=f"{FASTAPROXY_BASE_URL}/sparql",
        json={
            "query": "SELECT ?occ WHERE { ?occ a dwc:Occurrence } LIMIT 1",
        },
        timeout=TIMEOUT_VAL,
    )

    assert res.status_code == 400
    assert "detail" in res.json()


def test_invalid_sparql_syntax():
    res = httpx.post(
        url=f"{FASTAPROXY_BASE_URL}/sparql",
        json={
            "query": "SPARQL IS SELECT * FROM FUN",
        },
        timeout=TIMEOUT_VAL,
    )

    assert res.status_code == 400


def test_empty_query_string():
    res = httpx.post(
        url=f"{FASTAPROXY_BASE_URL}/sparql",
        json={
            "query": "",
        },
        timeout=TIMEOUT_VAL,
    )

    # WARN: Ontop considers an empty string a 500 error.
    # NOTE: Maybe validate it with Pydantic instead.
    #
    assert res.status_code == 500


def test_cache_returns_same_result():
    payload = {
        "query": OCCURRENCE_QUERY,
    }
 
    first_query = httpx.post(
        url=f"{FASTAPROXY_BASE_URL}/sparql",
        json=payload,
        timeout=TIMEOUT_VAL,
    )
    second_query = httpx.post(
        url=f"{FASTAPROXY_BASE_URL}/sparql",
        json=payload,
        timeout=TIMEOUT_VAL,
    )

    assert first_query.status_code == 200
    assert second_query.status_code == 200

    assert first_query.json() == second_query.json()


def test_cache_second_request_is_faster():
    payload = {
        "query": EVENT_QUERY,
    }

    t0 = time.monotonic()
    first_query = httpx.post(
        url=f"{FASTAPROXY_BASE_URL}/sparql",
        json=payload,
        timeout=TIMEOUT_VAL,
    )
    first_duration = time.monotonic() - t0

    t0 = time.monotonic()
    second_query = httpx.post(
        url=f"{FASTAPROXY_BASE_URL}/sparql",
        json=payload,
        timeout=TIMEOUT_VAL,
    )
    second_duration = time.monotonic() - t0
 
    assert first_query.status_code == 200
    assert second_query.status_code == 200

    # WARN: If rerun, the cache is already set, so this test will fail
    #
    assert second_duration < first_duration / 2, f"Cache did not accelerate response: first={first_duration:.2f}s second={second_duration:.2f}s"


@pytest.mark.asyncio
async def test_sparql_endpoint_concurrent():
    PAYLOAD = {
        "query": "PREFIX dwc: <http://rs.tdwg.org/dwc/terms/> SELECT ?occ WHERE { ?occ a dwc:Occurrence } LIMIT 1", 
    }

    async with httpx.AsyncClient() as client:

        async def make_request():
            res = await client.post(
                url=f"{FASTAPROXY_BASE_URL}/sparql",
                json=PAYLOAD,
            )

            assert res.status_code == 200

            body = res.json()

            assert "head" in body
            assert "results" in body

        await asyncio.gather(*(make_request() for _ in range(20)))