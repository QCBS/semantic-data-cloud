# Ontology and Mappings

## Overview

The semantic layer of this system is built on four files that work together: an OWL ontology, an OBDA mapping file, a JDBC properties file, and a database metadata JSON file. These are static across all dataset contexts, only the database name in the mapping, properties, and metadata files changes per context, and that substitution is performed automatically by the container manager.

---

## OWL ontology (`dwcowl.ttl`)

The ontology defines the vocabulary used in SPARQL queries and the class/property hierarchy over which Ontop reasons. It is written in [Turtle](https://www.w3.org/TR/turtle/) format and is based primarily around terms published by TDWG, including [Darwin Core](https://dwc.tdwg.org/list/), the [Humboldt Extension Vocabulary](https://eco.tdwg.org/list/), [Audiovisual Core](https://ac.tdwg.org/termlist), and the [Chronometric Age Vocabulary](https://chrono.tdwg.org/list/). Additional terms from the Minimum Information about any (x) Sequence ([MIxS](https://genomicsstandardsconsortium.github.io/mixs/)) and Global Genome Biodiversity Network ([GGBN](https://www.ggbn.org/ggbn_portal/site/wf?p=GGBN_Data_Standard)) standards cover genomic data.

Vocabularies can borrow terms from other namespaces, for example, Darwin Core includes terms from both the Dublin Core legacy (`dc:`) and Dublin Core terms (`dcterms:`) namespaces. At its most expressive, the ontology spans up to 30 namespaces. For most queries, the relevant ones are:

```sparql
PREFIX ac: <http://rs.tdwg.org/ac/terms/>
PREFIX chrono: <http://rs.tdwg.org/chrono/terms/>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX dwc: <http://rs.tdwg.org/dwc/terms/>
PREFIX dwcdp: <http://rs.tdwg.org/dwcdp/terms/>
PREFIX eco: <http://rs.tdwg.org/eco/terms/>
PREFIX gbif: <http://rs.gbif.org/terms/>
PREFIX mixs: <https://w3id.org/mixs/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
```

The ontology declares three types of entities:

- **Classes**, which represent categories or types of entities in the domain (for example, `dwc:Event`, `dwc:Occurrence`, or `dwc:MaterialEntity`).
- **Data properties**, which describe attributes of those entities using literal values such as text or numbers (for example, `dwc:decimalLatitude`, `dwc:organismQuantity`, or `dwc:scientificName`).
- **Object properties**, which define relationships between entities, linking one instance to another (for example, relating a `dwc:Occurrence` instance to a `dwc:Event` instance via `dwcdp:happenedDuring`).

The ontology is compliant to a specific OWL 2 profile, namely, the [OWL 2 QL](https://www.w3.org/2007/OWL/wiki/Profiles-v2.html#OWL_2_QL) profile. This is a requirement for Ontop to be able to translate the SPARQL queries to SQL (see [this paper](https://link.springer.com/article/10.1007/s10817-007-9078-x) for more details). The ontology is validated as conformant with the OWL 2 QL profile using [ROBOT's ontology profile validation](https://robot.obolibrary.org/validate-profile), which checks it against the W3C OWL 2 profile specification.

Ontop uses this ontology during query reformulation. It supports OWL 2 QL reasoning, which means subclass and subproperty hierarchies declared in the ontology are respected during query answering, though these features are kept minimal in the current version. For a full view of the ontology, consider loading the `.ttl` file into an ontology editor such as [Protégé](https://protege.stanford.edu/).

---

## OBDA mapping (`dwcowl.obda`)

The OBDA mapping file connects ontology terms to SQL queries over the DuckDB tables. It is written in Ontop's native [OBDA](https://ontop-vkg.org/guide/advanced/mapping-language.html) mapping language, which can be converted to the standard [R2RML](https://www.w3.org/TR/r2rml/) format.

Each mapping assertion has the form:

```
mappingId  <id>
target     <ontology term pattern>
source     <SQL SELECT statement>
```

For example, a minimal mapping of the `dwc:Occurrence` class and `dwc:scientificName` to relational content looks like:

```
mappingId  occurrence-minimal-class
target     :occurrence/{occurrence_id} a dwc:Occurrence ; dwc:scientific_name {scientific_name}^^xsd:string .
source     SELECT occurrence_id, scientific_name FROM FROM dwcowl.main.occurrence
```

The string `dwcowl` in the SQL `FROM` clause is the DuckDB catalog name. It is replaced at runtime by the container manager with the quoted context hash (e.g. `"95cb752fb61d60a2"`) for each per-context database file. The quoting is necessary because the hash begins with a digit, making it an invalid bare SQL identifier.

A strict `snake_case` naming convention is used for all column names in the database and Parquet files, to maximise portability across operating systems and database systems.

---

## Connection properties (`dwcowl.properties`)

The JDBC connection properties file is read by Ontop at startup. A template is stored in `ontop/mappings/`, from which the container manager generates a context-specific copy with the correct `jdbc.url` before starting each Ontop container.

The template is as follows:

```properties
jdbc.driver=org.duckdb.DuckDBDriver
jdbc.url=jdbc\:duckdb\:/db/dwcowl.duckdb
jdbc.user=
jdbc.password=
ontop.query.defaultTimeout=3600
ontop.queryLogging=true
ontop.queryLogging.includeReformulatedQuery=true
```

Only the `jdbc.url` line is modified by the application, all other settings are preserved from the template. Users can modify them if they wish. For other configuration options, consult the [Ontop configuration keys](https://ontop-vkg.org/guide/advanced/configuration.html) page.

As the application is oriented towards open-access to biodiversity data, no authentication is enabled by default. Should the user wish to enable it, credentials can be passed through the `jdbc.user` and `jdbc.password` settings.

---

## Database metadata (`dwcowl.json`)

The database metadata file provides Ontop with a complete description of the DWC DP table schema: column names, data types, nullability, primary key declarations, and foreign key relationships.

By taking database keys and other integrity constraints into account, Ontop can infer when multiple query atoms necessarily refer to the same database tuple. This allows it to eliminate redundant self-joins during SPARQL-to-SQL translation, producing simpler and more efficient SQL queries.

See the pages on the role [of primary keys](https://ontop-vkg.org/tutorial/mapping/primary-keys.html) and [of foreign keys](https://ontop-vkg.org/tutorial/mapping/foreign-keys.html) for a quick overview, as well as [this paper](https://www.sciencedirect.com/science/article/pii/S1570826815000153) for a more thorough explanation on the matter.

The metadata file was produced by running the [Ontop CLI](https://ontop-vkg.org/guide/cli.html) against a DuckDB instance populated with a modified DWC DP schema. This schema was based on the JSON files available at the [GBIF repository of schemas](https://rs.gbif.org/sandbox/experimental/data-packages/dwc-dp/0.1/table-schemas/), but also includes additional tables used by the application.

**Note:** The Ontop CLI's `extract-db-metadata` command produces a blank output with DuckDB JDBC driver 1.5.2 (the version considered by the application). Consequently, for database metadata extraction, version 1.5.1 of the driver was used (this fact can be seen at the bottom of the [metadata.json](/ontop/mappings/dwcowl.json) file). This does not affect the application, as Ontop only relies on the extracted metadata contained in the file.

---

## Ontop version and JDBC driver

The application uses the `ontop/ontop:5.5.0` Docker image. The DuckDB JDBC driver (`duckdb_jdbc-1.5.2.1.jar`) is downloaded from the [Maven repository](https://repo1.maven.org/maven2/org/duckdb/duckdb_jdbc/) and added to `/opt/ontop/jdbc/` at image build time:

```dockerfile
FROM ontop/ontop:5.5.0
USER root
ADD https://repo1.maven.org/maven2/org/duckdb/duckdb_jdbc/1.5.2.1/duckdb_jdbc-1.5.2.1.jar \
    /opt/ontop/jdbc/
ENV CLASSPATH="/opt/ontop/jdbc/duckdb_jdbc-1.5.2.1.jar:${CLASSPATH}"
```

If the DuckDB JDBC driver version is updated, the `duckdb` Python package version in `fastaproxy/requirements.txt` should be kept in alignment, as DuckDB file format compatibility is version-sensitive.
