import httpx


FASTAPROXY_BASE_URL = "http://fastaproxy:8000"


def test_sparql_endpoint():
    res = httpx.post(
        url=f"{FASTAPROXY_BASE_URL}/sparql",
        json={
            "query": "PREFIX dwc: <http://rs.tdwg.org/dwc/terms/> SELECT ?occ WHERE { ?occ a dwc:Occurrence } LIMIT 1",
        }
    )

    body = res.json()

    assert res.status_code == 200
    #
    assert set(body) == {"head", "results"}
    assert isinstance(body["head"], dict)
    assert isinstance(body["results"], dict)

    assert "vars" in body["head"]
    assert isinstance(body["head"]["vars"], list)

    assert "bindings" in body["results"]
    assert isinstance(body["results"]["bindings"], list)


def test_missing_query():
    res = httpx.post(
        url=f"{FASTAPROXY_BASE_URL}/sparql",
        json={}
    )

    body = res.json()

    assert res.status_code == 422
    assert body["detail"][0]["type"] == "missing"
    assert body["detail"][0]["loc"] == ["body", "query"]


def test_missing_spatial_value():
    res = httpx.post(
        url=f"{FASTAPROXY_BASE_URL}/sparql",
        json={
            "bbox": [1, 2, 3],
            "query": "PREFIX dwc: <http://rs.tdwg.org/dwc/terms/> SELECT ?occ WHERE { ?occ a dwc:Occurrence } LIMIT 1",
        }
    )

    body = res.json()

    assert res.status_code == 422
    assert body["detail"][0]["type"] == "value_error"


def test_non_numeric_spatial_value():
    res = httpx.post(
        url=f"{FASTAPROXY_BASE_URL}/sparql",
        json={
            "bbox": [1, 2, 3, "pumpernickel"],
            "query": "PREFIX dwc: <http://rs.tdwg.org/dwc/terms/> SELECT ?occ WHERE { ?occ a dwc:Occurrence } LIMIT 1",
        }
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
        }
    )

    body = res.json()

    assert res.status_code == 422
    assert body["detail"][0]["type"] == "value_error"


def test_missing_prefix():
    res = httpx.post(
        url=f"{FASTAPROXY_BASE_URL}/sparql",
        json={
            "query": "SELECT ?occ WHERE { ?occ a dwc:Occurrence } LIMIT 1",
        }
    )

    assert res.status_code == 400