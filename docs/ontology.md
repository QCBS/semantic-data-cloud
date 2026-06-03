# Ontology and mappings

## Overview

The semantic layer of this system is built on three files that work together: an OWL ontology, an OBDA mapping file, and a JDBC properties file. These are static across all dataset contexts, only the database name in the mapping and properties files changes per context, and that substitution is performed automatically by the container manager.

---

## OWL Ontology (`dwcowl.ttl`)

The ontology defines the vocabulary used in SPARQL queries and the class/property hierarchy over which Ontop reasons. It is written in [Turtle](https://www.w3.org/TR/turtle/) format and is mainly based around terms published by TDWG, including [Darwin Core](https://dwc.tdwg.org/list/), [Audiovisual Core](https://ac.tdwg.org/termlist) and the [Chronometric Age Vocabulary](https://chrono.tdwg.org/list/#chrono_ChronometricAge). In addition, terms from  Minimum Information about any (x) Sequence (MIxS) ([MIxS](https://genomicsstandardsconsortium.github.io/mixs/)) and Global Genome Biodiversity Network ([GGBN](https://www.ggbn.org/ggbn_portal/site/wf?p=GGBN_Data_Standard)) standards, as well as other other vocabularies for genomic data.

Note that, vocabularies can sometimes borrow terms from other names, for example Darwin Core considers terms from Dublin Core legacy and Dublin Core terms namespace (e.g `dc:title` or `dcterms:rights`). Therefore, at its most expressive, the ontology can consider up to 30 namespaces. However, for most queries, the considered namespaces usually are:

```
PREFIX ac:  <http://rs.tdwg.org/ac/terms/>
PREFIX dwc:  <http://rs.tdwg.org/dwc/terms/>
PREFIX dwcdp:  <http://rs.tdwg.org/dwcdp/terms/>
```

The ontology declares three types of entities:

- **Classes** corresponding to Darwin Core record types: `dwc:Occurrence`, `dwc:Event`, `dwc:Organism`, `dwc:MaterialSample`, and others.
- **Object properties** linking records (e.g. an Occurrence is related to an Event via `dwc:eventID`).
- **Data properties** for literal Darwin Core terms (e.g. `dwc:scientificName`, `dwc:decimalLatitude`).

Ontop uses this ontology during query reformulation. It supports OWL 2 QL reasoning, which means subclass and subproperty hierarchies declared in the ontology are respected during query answering, though these features are kept to a minimum for now. For a better view of the ontology, we recommend loading the `.ttl` file into a ontology editor such as [Protégé](https://protege.stanford.edu/).

---

## OBDA mapping (`dwcowl.obda`)

The OBDA mapping file connects ontology terms to SQL queries over the DuckDB tables. It is written in Ontop's native [OBDA](https://ontop-vkg.org/guide/advanced/mapping-language.html#source-query) mapping language, but can be converted into the standard [R2RML](https://www.w3.org/TR/r2rml/) mapping language.

Each mapping assertion has the form:

```
mappingId  <id>
target     <ontology term pattern>
source     <SQL SELECT statement>
```

For example, a minimal mapping of the `dwc:Occurrence` class and `dwc:scientificName` to the content in a relational database can be obtained as:

```
mappingId  occurrence-minimal-class
target     :occurrence/{occurrence_id} a dwc:Occurrence ; dwc:scientific_name {scientific_name}^^xsd:string .
source     SELECT occurrence_id, scientific_name FROM FROM "dwcowl".main.occurrence
```

The string `dwcowl` in the SQL `FROM` clause is the DuckDB catalog name. It is replaced at runtime by the container manager with the quoted context hash (e.g. `"95cb752fb61d60a2"`) for each per-context database file. The quoting is necessary because the hash begins with a digit, making it an invalid bare SQL identifier.

Note that, in order to maximize portability and the possibility of considering other database management systems and operating systems, we consider a strict `snake_case` naming for all terms in the database.

---

## Connection Properties (`dwcowl.properties`)

The JDBC connection properties file is read by Ontop at startup. A template is stored in `ontop/mappings/`; the container manager generates a context-specific copy with the correct `jdbc.url` before starting each Ontop container.

Template:

```properties
jdbc.driver=org.duckdb.DuckDBDriver
jdbc.url=jdbc\:duckdb\:/db/dwcowl.duckdb
jdbc.user=
jdbc.password=
ontop.query.defaultTimeout=3600
ontop.queryLogging=true
ontop.queryLogging.includeReformulatedQuery=true
```

This properties file is generated on a per context basis and passed on to the container running Ontop. Only the `jdbc.url` line is modified, all other settings are preserved from the template.

As the application is oriented towards open-access to biodiversity data, no authentification is enabled. Should the used desire to enable it, the appropriate credentials can be passed on to the application throuhgh the `jdbc.user` and `jdbc.password` settings.

If other parameters need to be changed, please consult the [Ontop configuration keys](https://ontop-vkg.org/guide/advanced/configuration.html) page.

---

## Ontop version and JDBC driver

The application considers the Ontop `ontop/ontop:5.5.0` image. The DuckDB JDBC driver (`duckdb_jdbc-1.5.2.1.jar`) is obtained from the [Maven repository](https://repo1.maven.org/maven2/org/duckdb/duckdb_jdbc/) and added to `/opt/ontop/jdbc/` at image build time:

```dockerfile
FROM ontop/ontop:5.5.0
USER root
ADD https://repo1.maven.org/maven2/org/duckdb/duckdb_jdbc/1.5.2.1/duckdb_jdbc-1.5.2.1.jar \
    /opt/ontop/jdbc/
ENV CLASSPATH="/opt/ontop/jdbc/duckdb_jdbc-1.5.2.1.jar:${CLASSPATH}"
```

If the DuckDB JDBC driver version is updated, the `duckdb` Python package version in `fastaproxy/requirements.txt` should be kept in alignment, as DuckDB file format compatibility is version-sensitive.
