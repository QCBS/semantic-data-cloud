# Semantic Data Cloud

An application that allows SPARQL-based queries over biodiversity datasets using Darwin Core semantics over Parquet-backed DuckDB views.

## Overview

Biodiversity data is commonly published as Darwin Core archives distributed across institutional repositories. The newly proposed [Darwin Core Data Package](https://www.gbif.org/composition/3Be8w9RzbjHtK2brXxTtun/introducing-the-darwin-core-data-package) format introduces additional semantics and flexibility, but also increased complexity in data integration and querying. Querying across multiple such datasets typically requires either centralising the data or negotiating heterogeneous APIs.

The [Darwin Core Conceptual Model](https://gbif.github.io/dwc-dp/cm/) is a highly interconnected data model. In this regard, it is well suited to graph representations. However, transforming tabular datasets into RDF represents a considerable Extract, Transform, Load (ETL) process and raises deduplication concerns, as the dataset must then exist in two different forms.

This project takes a different approach: data tables contained in the Data Package are hosted as Parquet files on object storage. Databases, consisting of views over the Parquet files, are used to construct a Virtual Knowledge Graph (VKG) and expose the data through a SPARQL interface. The datasets can then be queried using a lightweight OWL 2 QL compliant ontology based primarily on [Darwin Core](https://dwc.tdwg.org/list/) terms.

## Usage

To use the application locally, first clone the repository:

```bash
git clone <https://github.com/QCBS/semantic-data-cloud>
cd <semantic-data-cloud>
```

Start the application with Docker Compose:

```bash
docker compose up --build
```

The application will then expose a (modified) SPARQL endpoint at:

```text
http://localhost:8000/
```

For more details regarding the types of and example queries that can be run, please see the [SPARQL documentation](docs/sparql.md).