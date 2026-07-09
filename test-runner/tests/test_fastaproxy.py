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
#
ASK_QUERY = "PREFIX dwc: <http://rs.tdwg.org/dwc/terms/> ASK { ?occ a dwc:Occurrence }"
CONSTRUCT_QUERY = "PREFIX dwc: <http://rs.tdwg.org/dwc/terms/> CONSTRUCT { ?occ a dwc:Occurrence . } WHERE { ?occ a dwc:Occurrence . } LIMIT 1"


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


def test_sparql_ask_query():
    res = httpx.post(
        url=f"{FASTAPROXY_BASE_URL}/sparql",
        json={
            "query": ASK_QUERY,
        },
        timeout=TIMEOUT_VAL,
    )

    assert res.status_code == 200

    body = res.json()

    assert "head" in body
    assert "boolean" in body

    assert body["head"] == {}
    assert isinstance(body["boolean"], bool)


# TODO: Maybe expand verification using rdflib
#
def test_sparql_construct_query():
    res = httpx.post(
        url=f"{FASTAPROXY_BASE_URL}/sparql",
        json={
            "query": CONSTRUCT_QUERY,
        },
        timeout=TIMEOUT_VAL,
    )

    assert res.status_code == 200

    body = res.text

    assert "@prefix rdf:" in body


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
            "query": "PREFIX dwc: <http://rs.tdwg.org/dwc/terms/> SELECT ?occ WHERE { ?occ a dwc:Occurrence } LIMIT 1",
            "bbox": [-74.0684, 4.5958, -74.0684],
        },
    )

    body = res.json()

    assert res.status_code == 422
    assert body["detail"][0]["type"] == "value_error"


def test_non_numeric_spatial_value():
    res = httpx.post(
        url=f"{FASTAPROXY_BASE_URL}/sparql",
        json={
            "query": "PREFIX dwc: <http://rs.tdwg.org/dwc/terms/> SELECT ?occ WHERE { ?occ a dwc:Occurrence } LIMIT 1",
            "bbox": [-74.0684, 4.5958, -74.0684, "pumpernickel"],
        },
    )

    body = res.json()

    assert res.status_code == 422
    assert body["detail"][0]["type"] == "float_parsing"


def test_non_iso_8601_date():
    res = httpx.post(
        url=f"{FASTAPROXY_BASE_URL}/sparql",
        json={
            "query": "PREFIX dwc: <http://rs.tdwg.org/dwc/terms/> SELECT ?occ WHERE { ?occ a dwc:Occurrence } LIMIT 1",
            "temporal": ["08/15/89", "08/21/89"],
        },
    )

    body = res.json()

    assert res.status_code == 422
    assert body["detail"][0]["type"] == "value_error"
    assert "dates must be in YYYY-MM-DD format" in body["detail"][0]["msg"]


def test_temporal_start_after_end():
    res = httpx.post(
        url=f"{FASTAPROXY_BASE_URL}/sparql",
        json={
            "query": OCCURRENCE_QUERY,
            "temporal": ["2038-01-19", "1991-09-17"],
        },
        timeout=TIMEOUT_VAL,
    )

    assert res.status_code == 422

    body = res.json()

    assert body["detail"][0]["type"] == "value_error"
    assert body["detail"][0]["loc"] == ["body","temporal"]
    assert "begin_date must be <= end_date" in body["detail"][0]["msg"]


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


def test_sparql_empty_query_string():
    res = httpx.post(
        url=f"{FASTAPROXY_BASE_URL}/sparql",
        json={
            "query": "",
        },
        timeout=TIMEOUT_VAL,
    )

    # WARN: Ontop considers an empty string a 500 error.
    # NOTE: Validated with Pydantic instead.
    #
    assert res.status_code == 422


def test_sparql_too_short_bbox():
    res = httpx.post(
        url=f"{FASTAPROXY_BASE_URL}/sparql",
        json={
            "query": OCCURRENCE_QUERY,
            "bbox": [-74.0684, 4.5958, -74.0684],
        },
        timeout=TIMEOUT_VAL,
    )

    assert res.status_code == 422

    body = res.json()

    assert body["detail"][0]["type"] == "value_error"
    assert body["detail"][0]["loc"] == ["body","bbox"]
    assert "Spatial range bbox must have exactly 4 values" in body["detail"][0]["msg"]


def test_sparql_too_long_bbox():
    res = httpx.post(
        url=f"{FASTAPROXY_BASE_URL}/sparql",
        json={
            "query": OCCURRENCE_QUERY,
            "bbox": [-74.0684, 4.5958, -74.0684, 4.5958, -74.0684],
        },
        timeout=TIMEOUT_VAL,
    )

    assert res.status_code == 422

    body = res.json()

    assert body["detail"][0]["type"] == "value_error"
    assert body["detail"][0]["loc"] == ["body","bbox"]
    assert "Spatial range bbox must have exactly 4 values" in body["detail"][0]["msg"]


def test_sparql_too_short_temporal():
    res = httpx.post(
        url=f"{FASTAPROXY_BASE_URL}/sparql",
        json={
            "query": OCCURRENCE_QUERY,
            "temporal": ["1991-09-17"],
        },
        timeout=TIMEOUT_VAL,
    )

    assert res.status_code == 422

    body = res.json()

    assert body["detail"][0]["type"] == "value_error"
    assert body["detail"][0]["loc"] == ["body","temporal"]
    assert "Temporal range must have exactly 2 values" in body["detail"][0]["msg"]


def test_sparql_too_long_temporal():
    res = httpx.post(
        url=f"{FASTAPROXY_BASE_URL}/sparql",
        json={
            "query": OCCURRENCE_QUERY,
            "temporal": ["1991-09-17", "2038-01-19", "2038-01-19"],
        },
        timeout=TIMEOUT_VAL,
    )

    assert res.status_code == 422

    body = res.json()

    assert body["detail"][0]["type"] == "value_error"
    assert body["detail"][0]["loc"] == ["body","temporal"]
    assert "Temporal range must have exactly 2 values" in body["detail"][0]["msg"]


def test_cache_returns_same_result():
    first_query = httpx.post(
        url=f"{FASTAPROXY_BASE_URL}/sparql",
        json={
            "query": OCCURRENCE_QUERY,
        },
        timeout=TIMEOUT_VAL,
    )
    second_query = httpx.post(
        url=f"{FASTAPROXY_BASE_URL}/sparql",
        json={
            "query": OCCURRENCE_QUERY,
        },
        timeout=TIMEOUT_VAL,
    )

    assert first_query.status_code == 200
    assert second_query.status_code == 200

    assert first_query.json() == second_query.json()


def test_cache_second_request_is_faster():
    t0 = time.monotonic()
    first_query = httpx.post(
        url=f"{FASTAPROXY_BASE_URL}/sparql",
        json={
            "query": EVENT_QUERY,
        },
        timeout=TIMEOUT_VAL,
    )
    first_duration = time.monotonic() - t0

    t0 = time.monotonic()
    second_query = httpx.post(
        url=f"{FASTAPROXY_BASE_URL}/sparql",
        json={
            "query": EVENT_QUERY,
        },
        timeout=TIMEOUT_VAL,
    )
    second_duration = time.monotonic() - t0

    assert first_query.status_code == 200
    assert second_query.status_code == 200

    # WARN: If rerun, the cache is already set, so this test will fail
    #
    assert second_duration < first_duration / 2.0, f"Cache did not accelerate response: first={first_duration:.2f}s second={second_duration:.2f}s"


@pytest.mark.asyncio
async def test_sparql_endpoint_concurrent():
    async with httpx.AsyncClient() as client:
        async def make_request():
            res = await client.post(
                url=f"{FASTAPROXY_BASE_URL}/sparql",
                json={
                    "query": OCCURRENCE_QUERY,
                },
            )

            assert res.status_code == 200

            body = res.json()

            assert "head" in body
            assert "results" in body

        await asyncio.gather(*(make_request() for _ in range(20)))