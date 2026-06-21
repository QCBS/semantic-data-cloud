# Architecture

## Design principles

The system is built around three constraints that shaped every subsequent decision.

  1. **Data stays in place.** Biodiversity datasets and their associated metadata are published and maintained by individual institutions. Centralizing them would create synchronisation problems and duplicate storage. Instead, datasets are referenced as remote Parquet files, the system reads them at query time.

  2. **Entity-based queries.** Biodiversity data is naturally described as a network of occurrences, events, organisms, material entities, and the relationships between them. RDF is therefore a suitable data model, as it represents information directly as entities and relationships rather than requiring users to reason about relational structures.

  3. **Machine-readability first.** Data should be structured according to a shared conceptual model, with clearly defined concepts and relationships that can be interpreted consistently by both humans and machines. In this application, that model is provided by the Darwin Core Conceptual Model and its associated vocabularies.

---

## Components

### Dataset discovery layer: metadata-fast-api

A FastAPI service that stores dataset-level EML metadata as JSON-LD in a DuckDB instance. Rather than relying on verbose and difficult to parse `.xml` files, EML files are converted into [JSON-LD](https://www.w3.org/TR/json-ld11/) during ingestion.

This makes the information more API-friendly and allows metadata fields to be extracted succinctly using [DuckDB JSON extraction functions](https://duckdb.org/docs/current/data/json/json_functions), allowing for easier extraction and storage. The full metadata for any dataset can be obtained by making a request to the corresponding `/dataset/{dataset-key}` endpoint.

The service exposes a `/datasets/search` endpoint that accepts a bounding box, temporal range, and list of licenses as optional filter, and returns the identifiers of all datasets whose declared coverage intersects those parameters. For more details on the exact definition of these [API document](/docs/api.md).

Each dataset record stores its asset list, which are the URLs of its constituent Parquet files, alongside the EML content. This design was strongly influenced by the [asset objects](https://github.com/radiantearth/stac-spec/blob/master/commons/assets.md) in SpatioTemporal Asset Catalogs ([STAC](https://stacspec.org/en)).

### Business logic layer: fastaproxy-sdc

The central proxy for all SPARQL queries. Its responsibilities are:

- Accepting client SPARQL queries alongside optional dataset filters (spatial, temporal, license).
- Querying the metadata API to resolve the relevant dataset IDs.
- Delegating database construction to `db_builder`.
- Delegating container management to `ContainerRegistry`.
- Forwarding SPARQL to the appropriate Ontop container.
- Caching results in Valkey.

It is stateless with respect to data, but stateful with respect to the container registry (held in `app.state`).

#### db_builder

Constructs a materialised DuckDB database for a given list of dataset IDs. For each Darwin Core table (event, media, occurrence, etc...), it creates views over the Parquet assets from all datasets in the context. The [`union_by_name=True`](https://duckdb.org/docs/current/data/multiple_files/combining_schemas) option handles column set differences across datasets by filling absent columns with NULL and guaranteeing correct column matching.

The output is a `.duckdb` file containing views over Parquet files representing the tables in the Darwin Core Data Package schema, named after a 16-character SHA-256 prefix of the sorted, pipe-delimited dataset ID list. This hash serves as both the filename and the cache key, a database is built only once per unique dataset combination and reused on all subsequent requests.

The [blanks/](../blanks/) directory contains zero-row Parquet files for every table in the Darwin Core Data Package schema, obtained from the [GBIF schema repository](https://rs.gbif.org/sandbox/experimental/data-packages/dwc-dp/0.1/table-schemas/). These serve as schema anchors: they guarantee that every table exists in the database even when no dataset in the context contributes data to it, preventing Ontop from encountering missing tables or forcing the Parquet file to contains numerous empty columns.

#### container_manager

Manages the lifecycle of per-context Ontop containers. On the first request for a context, it generates a context-specific properties file (with the correct `jdbc.url`) and OBDA mapping file (with the database name replaced by the quoted context hash), then starts an Ontop container with those files and the shared `/db` and `/blanks` volumes. On subsequent requests for the same context, it checks the in-memory registry and reuses the running container if healthy.

Volume host paths are discovered automatically by inspecting the fastaproxy container's own mount table via the Docker socket, removing the need for explicit `HOST_*` environment variables.

#### Ontop containers

Short-lived containers running [Ontop](https://ontop-vkg.org/) (`ontop/ontop:5.5.0`) with the DuckDB JDBC driver (`duckdb_jdbc-1.5.2.1.jar`). Each container receives three files at startup: an OWL ontology (`.ttl`), an OBDA mapping (`.obda`), and a connection properties file (`.properties`). The OBDA mapping is generated per-context with the correct database catalog name. Ontop translates incoming SPARQL queries to SQL, executes them against the DuckDB database, and returns results in SPARQL JSON format.

### Caching layer: Valkey

A [Valkey](https://valkey.io/) instance used for in-memory result caching. As the number of datasets grows, query latency may increase, caching allows repeated queries to be served from RAM rather than re-executing against the database.

Cache keys are SHA-256 digests of the context hash concatenated with the SPARQL query bytes. Each key has a configurable time-to-live ([TTL](https://valkey.io/commands/ttl/)), defaulting to 70 seconds.

The instance uses at most 1 Gb or RAM and considers an [allkeys-lfu](https://valkey.io/topics/lru-cache/) eviction policy. This means that when memory is exhausted, the least frequently accessed keys will be removed to make place for the new data to be added.

---

## Data flow

The flow of data in the application can be summarized by the following sequence:

  1. Client POSTs `{ sparql, [bbox, temporal, licenses] }` request to fastaproxy `/sparql`

  2. fastaproxy calls metadata-api `/datasets/search`
    → returns list of dataset IDs whose coverage intersects the request

  3. fastaproxy computes `context_hash = SHA-256(sorted(dataset_ids))[:16]`
    → checks Valkey for `cache_key` corresponding to `"sparql:{context_hash}:{SHA-256(query)}"`
    → on hit: return cached result immediately

  4. fastaproxy calls `db_builder.build_db(dataset_ids)`
    → if `/db/{context_hash}.duckdb` exists: no-op (file already exists)
    → else: fetches Parquet assets from S3, creates DuckDB views, writes file

  5. fastaproxy calls `registry.get_or_create(dataset_ids)`
    → if `ontop-{context_hash}` is running and healthy: reuse
    → else: generate per-context `.properties` and `.obda` files,
            docker run `ontop-{context_hash}`,
            wait for `/actuator/health` → 200

  6. fastaproxy POSTs SPARQL to `http://ontop-{context_hash}:8080/sparql`
    → Ontop reformulates SPARQL to SQL
    → DuckDB executes SQL against views
    → results returned as SPARQL JSON

  7. fastaproxy caches result in Valkey, returns SPARQL JSON results to client
