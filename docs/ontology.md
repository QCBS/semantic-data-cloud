# Ontology and mappings

## Overview

The semantic layer of this system is built on three files that work together: an OWL ontology, an OBDA mapping file, and a JDBC properties file. These are static across all dataset contexts, only the database name in the mapping and properties files changes per-context, and that substitution is performed automatically by the container manager.

---

## OWL Ontology (`dwcowl.ttl`)

The ontology defines the vocabulary used in SPARQL queries, which consists of the classes and properties over which Ontop reasons. It is written in [Turtle](https://www.w3.org/TR/turtle/) format and is based primarily around terms published by TDWG, including [Darwin Core](https://dwc.tdwg.org/list/), the [Humboldt Extension Vocabulary](https://eco.tdwg.org/list/), [Audiovisual Core](https://ac.tdwg.org/termlist), and the [Chronometric Age Vocabulary](https://chrono.tdwg.org/list/). Additional terms from the Minimum Information about any (x) Sequence ([MIxS](https://genomicsstandardsconsortium.github.io/mixs/)) and Global Genome Biodiversity Network ([GGBN](https://www.ggbn.org/ggbn_portal/site/wf?p=GGBN_Data_Standard)), as well as other other vocabularies for genomic data.

Vocabularies can borrow terms from other namespaces, for example, Darwin Core includes terms from both the Dublin Core legacy (`dc:`) and Dublin Core terms (`dcterms:`) namespaces. At its most expressive, the ontology spans up to 30 namespaces. For most queries, the relevant ones are:

```sparql
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX ac: <http://rs.tdwg.org/ac/terms/>
PREFIX dwc: <http://rs.tdwg.org/dwc/terms/>
PREFIX eco: <http://rs.tdwg.org/eco/terms/>
PREFIX dwcdp: <http://rs.tdwg.org/dwcdp/terms/>
```

The ontology declares three types of entities:

- **Classes** corresponding to Darwin Core record types: `dwc:Occurrence`, `dwc:Event`, `dwc:Organism`, `dwc:MaterialEntity`, and others.
- **Data properties** for literal Darwin Core terms (e.g. `dwc:scientificName`, `dwc:decimalLatitude`).
- **Object properties** linking records (e.g. a `dwc:Occurrence` instance is related to a `dwc:Event` instance via `dwcdp:happenedDuring`).

The ontology is validated as conformant with the OWL 2 QL profile using [ROBOT's ontology profile validation](https://robot.obolibrary.org/validate-profile), which checks the ontology against the W3C OWL 2 profile specification.

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

## Connection Properties (`dwcowl.properties`)

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

Only the `jdbc.url` line is modified, all other settings are preserved from the template. However, users can modify them if they wish. For other configuration options, consult the [Ontop configuration keys](https://ontop-vkg.org/guide/advanced/configuration.html) page.

As the application is oriented towards open-access to biodiversity data, no authentication is enabled by default. Should the user wish to enable it, credentials can be passed through the `jdbc.user` and `jdbc.password` settings.

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


https://robot.obolibrary.org/validate-profile