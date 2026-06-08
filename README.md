# Semantic Data Cloud

An application that allows SPARQL-based queries over biodiversity datasets using Darwin Core semantics over Parquet-backed DuckDB views.

## Overview

Biodiversity data is commonly published as Darwin Core archives distributed across institutional repositories. The newly proposed [Darwin Core Data Package](https://www.gbif.org/composition/3Be8w9RzbjHtK2brXxTtun/introducing-the-darwin-core-data-package) format introduces additional semantics and flexibility, but also increased complexity in data integration and querying. Querying across multiple such datasets typically requires either centralising the data or negotiating heterogeneous APIs.

The [Darwin Core Conceptual Model](https://gbif.github.io/dwc-dp/cm/) is a highly interconnected data model. In this regard, it is well suited to graph representations. However, transforming tabular datasets into RDF represents a considerable Extract, Transform, Load (ETL) process and raises deduplication concerns, as the dataset must then exist in two different forms.

This project takes a different approach: data tables contained in each Data Package are hosted as Parquet files on object storage. On demand, a materialised DuckDB database is assembled from the relevant files and exposed through a SPARQL interface via a Virtual Knowledge Graph (VKG). Datasets can then be queried using a lightweight OWL 2 QL compliant ontology based primarily on [Darwin Core](https://dwc.tdwg.org/list/) terms, without any ETL step or permanent data duplication.

## Usage

The application accepts SPARQL queries over HTTP, following the structure of the [SPARQL 1.1 Protocol](https://www.w3.org/TR/sparql11-protocol/). Queries are submitted as JSON to the `/sparql` endpoint:

```json
{
  "query": "PREFIX dwc: <http://rs.tdwg.org/dwc/terms/> SELECT ?sciName (COUNT(?occ) AS ?nOcc) WHERE { ?occ a dwc:Occurrence ; dwc:scientificName ?sciName . } GROUP BY ?sciName ORDER BY DESC(?nOcc) LIMIT 5"
}
```

Any tool capable of making HTTP requests can interact with the endpoint, including:

- Python: [Requests](https://requests.readthedocs.io/), [HTTPX](https://www.python-httpx.org/), or the standard library [urllib](https://docs.python.org/3/library/urllib.request.html).
- Ruby: [Faraday](https://lostisland.github.io/faraday/), [HTTParty](https://github.com/jnunemaker/httparty), or the standard gem [HTTP](https://ruby-doc.org/stdlib-2.7.0/libdoc/net/http/rdoc/Net/HTTP.html).
- JavaScript: [Axios](https://axios-http.com/), [ky](https://github.com/sindresorhus/ky), or the standard [Fetch](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch).
- R: [httr2](https://httr2.r-lib.org/).
- Command line: [curl](https://curl.se/) or [wget](https://www.gnu.org/software/wget/)

## Additional functionality

In addition to creating complete collection of datasets, the application can generate filtered dataset subsets based on user-defined criteria. The following filters are currently supported:

- **Spatial filtering**: Provide a bounding box of coordinates to include only datasets whose spatial coverage intersects the specified area.
- **Temporal filtering**: Provide a date range to include only datasets whose temporal coverage intersects the specified period.
- **License filtering**: Provide one or more license identifiers to include only datasets published under the selected licenses.

Optional filters can narrow which datasets are loaded before the query runs, which means that the application accepts the following JSON objects:

```json
{
  "query": "...",
  "bbox":     [min_lon, min_lat, max_lon, max_lat],
  "temporal": ["YYYY-MM-DD", "YYYY-MM-DD"],
  "licenses": ["CC-BY-4.0", "CC0-1.0"]
}
```

When generating a subset, the application reads only the data required from the source Parquet files stored in object storage. It then creates an isolated, context-specific Docker container that enables efficient querying and processing of the selected data.

### Data provenance and attribution

Each generated container includes a `{ctx_hash}-citations.txt` file containing the citations associated with the datasets used to build that context. This ensures, traceability of the source datasets, proper attribution of data providers cand ompliance with GBIF data usage requirements. This is in line with [the GBIF data user agreement](https://www.gbif.org/terms/data-user) and [GBIF citation guidelines](https://www.gbif.org/citation-guidelines).

## Local deployment

Clone the repository and start the stack with Docker Compose:

```bash
git clone https://github.com/QCBS/semantic-data-cloud
cd semantic-data-cloud
docker compose up --build
```

The SPARQL endpoint will be available at:

```
http://localhost:8000/sparql
```

### Storage layout

Datasets are stored in object storage as directory-like prefixes, where each dataset is represented as a self-contained Darwin Core Data Package in exploded Parquet form. An example structure layout is as shown below:

```
datasets/
├── dataset_a/
│   ├── eml.jsonld
│   ├── event.parquet
│   ├── identification.parquet
│   ├── occurrence.parquet
│   └── occurrence-assertion.parquet
├── dataset_b/
│   ├── eml.jsonld
│   ├── event.parquet
│   └── material.parquet
└── dataset_c/
    ├── eml.jsonld
    ├── event.parquet
    ├── event-assertion.parquet
    └── occurrence.parquet
```

Each top-level directory under `datasets/` represents a single dataset (i.e., a Darwin Core Data Package). The presence of an `eml.jsonld` file provides the required metadata for discovery and attribution.

All tables are stored as Parquet files, corresponding to Darwin Core tables (e.g., `event`, `identification`, `occurrence`) in the `.csv` (though they are technically `.tsv`) files contained in the Darwin Core Data Package. This layout is corresponds to an "exploded" representation of a Darwin Core Data Package, designed for columnar access and efficient partial loading in DuckDB without requiring transformation into RDF or a centralized warehouse.

### Environment Configuration

To access the object storage instance and API services, you must define a `.env` file in the root of the project with the following variables:

```env
S3_ACCESS_ID=your_access_key_id
S3_ACCESS_SECRET=your_secret_access_key
S3_ENDPOINT_URL=https://your-object-storage-endpoint
S3_BUCKET_NAME=your_bucket_name
OBJECT_STORE_BASE_URL=https://your-public-object-url-base
API_BASE_URL=https://your-api-base-url
```

Where the following parameters are required:

- **S3_ACCESS_ID**: Access key ID used to authenticate with the object storage service.
- **S3_ACCESS_SECRET**: Secret key paired with the access ID for authentication.
- **S3_ENDPOINT_URL**: Endpoint URL of the S3-compatible storage service.
- **S3_BUCKET_NAME**: Name of the bucket where objects are stored.
- **OBJECT_STORE_BASE_URL**: Public base URL used to access stored objects.
- **API_BASE_URL**: Base URL of the backend API service.

## Documentation

Additional detailed documentation can be found in the [`docs/`](docs/) directory:
  - [Architecture](docs/architecture.md) describing the overall architecture and design of the application.
  - [API reference](docs/api.md), describing the endpoint specification and request/response formats.
  - [Ontology and mappings](docs/ontology.md), describing the Darwin Core OWL ontology and OBDA mapping conventions.
  - [MCP server](docs/mcp.md), describing a natural language interface via the Model Context Protocol.
