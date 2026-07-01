# API reference

## fastaproxy-sdc

Base URL: `http://localhost:8000` (default)

---

### POST /sparql

Requests against the `/sparql` endpoint use a JSON POST body, with the SPARQL query as the value associated with the `query` key. Note that this is a convenience deviation from the [SPARQL 1.1 Protocol](https://www.w3.org/TR/2013/REC-sparql11-protocol-20130321/), which does not define a JSON-based request format. Standard SPARQL clients sending `application/x-www-form-urlencoded` or `application/sparql-query` bodies will need to be adapted accordingly.

**Request body** (`application/json`)

| Field | Type | Required | Description |
|---|---|---|---|
| `query` | `string` | Yes | A valid SPARQL 1.1 SELECT query, prefixes must be declared explicitly |
| `bbox` | `[float, float, float, float]` | No | Bounding box as `[min_lon, min_lat, max_lon, max_lat]` in WGS84. Default: `[-180.0, -90.0, 180.0, 90.0]` |
| `temporal` | `[string, string]` | No | Temporal range as `["YYYY-MM-DD", "YYYY-MM-DD"]` (begin, end inclusive). Default: `['0001-01-01', '2038-01-19']` |
| `licenses` | `[string, ...]` | No | SPDX license identifiers to restrict which datasets are loaded, see the [SPDX License List](https://spdx.org/licenses/). Default: `None` |

**Validation rules**

- `bbox`: must contain exactly 4 values, with `min_lon ≤ max_lon` and `min_lat ≤ max_lat`. Each coordinate must be within WGS84 bounds.
- `temporal`: must contain exactly 2 ISO 8601 dates (`YYYY-MM-DD`), with `begin ≤ end`.
- `licenses`: no format validation. Values are matched against the `license_id` field in dataset metadata, which is expected to be a valid SPDX license identifier.

**Response** (`application/sparql-results+json`)

Results follow the standard [SPARQL 1.1 Query Results JSON format](https://www.w3.org/TR/sparql11-results-json/):

```json
{
  "head": { "vars": ["subj", "sciName"] },
  "results": {
    "bindings": [
      {
        "subj": { "type": "uri", "value": "https://biobang.org/occurrence/abc123" },
        "sciName": { "type": "literal", "value": "Acanthurus mata" }
      }
    ]
  }
}
```

**Caching**

Responses are cached in Valkey. The cache key is derived from the set of matched dataset IDs and the SPARQL query text. Two requests with different bounding boxes that resolve to the same dataset combination will share cache entries for identical queries. Cache TTL is controlled by the `TTL_VAL` environment variable (default: 1 week).

**Cold start**

The first request for a new dataset combination triggers ontology files editing, DuckDB view creation, and Ontop container startup. This typically takes 10–30 seconds depending on dataset size and operating system. Subsequent requests for the same combination reuse the running container and are served within seconds. If the request is repeated, then response time is almost instantaneous due to Valkey caching.

---

## metadata-api

Base URL: `http://localhost:7788` (default, mapped to internal port 8000)

---

### GET /datasets

List all registered datasets with pagination.

**Query parameters**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `page` | `int` | `1` | Page number (1-indexed) |
| `page_size` | `int` | `10` | Results per page (max 100) |

---

### GET /dataset/{dataset_id}

Return the full EML JSON-LD metadata record for a single dataset, including its asset list.

**Response** (`application/ld+json`)

The EML document as JSON-LD, augmented with an `assets` array and a `self` link:

```json
{
  "@context": { "..." : "..." },
  "@type": "EML",
  "additionalMetadata": { "..." : "..." },
  "dataset": { "..." : "..." },
  "assets": [
    { "href": "https://storage.example.org/datasets/dataset-id/occurrence.parquet", "mimetype": "application/vnd.apache.parquet" },
    { "href": "https://storage.example.org/datasets/dataset-id/event.parquet", "mimetype": "application/vnd.apache.parquet" }
  ],
  "self": "http://localhost:7788/dataset/dataset-id"
}
```

The media type for the Parquet files is `application/vnd.apache.parquet`, [as registered by the IANA](https://www.iana.org/assignments/media-types/application/vnd.apache.parquet).

---

### GET /datasets/search

Return the identifiers of all datasets whose geographic and temporal coverage intersects the query parameters.

**Query parameters**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `min_lon` | `float` | No | West boundary of query bbox (WGS84). Default: `-180.0` |
| `min_lat` | `float` | No | South boundary of query bbox (WGS84). Default: `-90.0` |
| `max_lon` | `float` | No | East boundary of query bbox (WGS84). Default: `180.0` |
| `max_lat` | `float` | No | North boundary of query bbox (WGS84). Default: `90.0` |
| `begin_date` | `string` | No | Start of temporal range (`YYYY-MM-DD`). Default: `0001-01-01` |
| `end_date` | `string` | No | End of temporal range (`YYYY-MM-DD`). Default: `2038-01-19` |
| `licenses` | `[string]` | No | One or more SPDX license identifiers. Repeatable: `?licenses=CC-BY-4.0&licenses=CC0-1.0` |

**Intersection logic**

A dataset is returned if all of the following hold:

```
dataset.west ≤ max_lon AND dataset.east ≥ min_lon
dataset.south ≤ max_lat AND dataset.north ≥ min_lat
dataset.begin ≤ end_date AND dataset.end ≥ begin_date
```

This is standard interval/rectangle intersection: any spatial or temporal overlap is sufficient.

When `licenses` is provided, only datasets whose declared license matches one of the supplied identifiers are returned.

**Response**

```json
{
  "datasets": [
    "dataset-id-a",
    "dataset-id-b",
    "..."
  ] 
}
```

An empty list is returned (i.e. not a `404`) when no datasets match.

---

### POST /datasets/citations

Return citation strings for a list of dataset identifiers.

**Request body** (`application/json`)

| Field | Type | Required | Description |
|---|---|---|---|
| `dataset_names` | `[string]` | Yes | One or more dataset identifiers |

```json
{
  "dataset_names": ["dataset-a", "dataset-b", "..."]
}
```

**Response**

```json
{
  "citations": [
    "Author et al. (2023). Distribution of species X in location Y. ...",
    "Penman et al. (2018). Sampling surveys studying communities in Z biomes. ...",
    "..."
  ]
}
```

Citations are extracted from the `additionalMetadata.metadata.gbif.citation` field of each dataset's EML record.