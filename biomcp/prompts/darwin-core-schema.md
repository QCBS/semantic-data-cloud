# Darwin Core Data Package — Ontology Reference

> This file is injected at runtime into every SPARQL tool call.
> It describes the EXACT graph structure of THIS endpoint.
> Do NOT assume flat Darwin Core — this uses DWC-DP linked object properties.

---

## ⚠️ MANDATORY INSTRUCTIONS — READ BEFORE DOING ANYTHING

**DO NOT write exploratory queries.** Do not query `?interaction ?predicate ?value`
to "understand the structure". The structure is fully documented below.
Writing exploratory queries wastes time and often returns misleading results
due to OPTIONAL properties.

**USE THE PATTERNS.** Every query type you will ever need has a worked example
in this document. Find the pattern that matches the user's question, copy it,
and adapt the filter values only. Do not invent new query structures.

**Decision tree — pick your pattern before writing a single line of SPARQL:**

| User asks about... | Action |
|---|---|
| Species occurrences, counts, names | Use Pattern 1 or 5 |
| Coordinates, locations, countries | Use Pattern 2, 3, or 4 |
| Dates, years, months | Use Pattern 6 |
| Who recorded something | Use Pattern 7 |
| Interactions between species | Go to OrganismInteraction section — use standard pattern there |
| Unsure what properties exist | Call `inspect_ontology` tool — do NOT write exploratory SPARQL |

---

## Namespace prefixes
Declare ALL of these at the top of every query, even if you only use some.

```sparql
PREFIX rdf:     <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs:    <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl:     <http://www.w3.org/2002/07/owl#>
PREFIX xsd:     <http://www.w3.org/2001/XMLSchema#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX dce:     <http://purl.org/dc/elements/1.1/>
PREFIX dwc:     <http://rs.tdwg.org/dwc/terms/>
PREFIX dwciri:  <http://rs.tdwg.org/dwc/iri/>
PREFIX dwcdp:   <http://rs.tdwg.org/dwcdp/terms/>
PREFIX eco:     <http://rs.tdwg.org/eco/terms/>
PREFIX ac:      <http://rs.tdwg.org/ac/terms/>
```

---

## Graph structure — how classes connect via object properties

**This is not flat DWC.** To reach location data you must traverse a chain.
There are NO coordinates directly on dwc:Occurrence.

```
dwc:Occurrence
├─ dwcdp:happenedDuring  ──► dwc:Event
│                              ├─ dwcdp:spatialLocation ──► dcterms:Location
│                              │                              (coordinates, country, locality)
│                              ├─ dwcdp:conductedBy     ──► dcterms:Agent
│                              ├─ dwcdp:hasProvenance   ──► dwcdp:Provenance
│                              └─ dwcdp:happenedDuring  ──► dwc:Event  (parent event)
│
├─ dwcdp:occurrenceOf    ──► dwc:Organism
├─ dwcdp:recordedBy      ──► dcterms:Agent
├─ dwcdp:identifiedBy    ──► dcterms:Agent
├─ dwcdp:mentionedIn     ──► dcterms:BibliographicResource
├─ dwcdp:happenedWithin  ──► dwc:GeologicalContext
└─ dwcdp:satisfied       ──► eco:SurveyTarget
```

---

## Properties per class

### dwc:Occurrence — data properties (no traversal needed)

| Property | Description | Example |
|---|---|---|
| `dwc:scientificName` | Full scientific name | "Abudefduf vaigiensis" |
| `dwc:scientificNameID` | Taxon name identifier | |
| `dwc:taxonID` | Taxon identifier | |
| `dwc:taxonRank` | Rank of the taxon | "species", "genus" |
| `dwc:kingdom` | Kingdom | "Animalia", "Plantae" |
| `dwc:verbatimIdentification` | Original identification string | |
| `dwc:vernacularName` | Common name | |
| `dwc:basisOfRecord` | Nature of the record | "HumanObservation", "PreservedSpecimen" |
| `dwc:occurrenceID` | Unique occurrence identifier | |
| `dwc:occurrenceStatus` | Presence/absence | "present", "absent" |
| `dwc:occurrenceRemarks` | Free-text notes | |
| `dwc:individualCount` | Number of individuals | 3 |
| `dwc:organismQuantity` | Quantity value | |
| `dwc:organismQuantityType` | Quantity unit | "individuals", "% cover" |
| `dwc:sex` | Sex of organism | "male", "female" |
| `dwc:lifeStage` | Life stage | "adult", "juvenile", "larva" |
| `dwc:vitality` | Living status | "alive", "dead" |
| `dwc:recordedBy` | Recorder name (literal string) | "Jane Smith" |
| `dwc:identifiedBy` | Identifier name (literal string) | |
| `dwc:catalogNumber` | Catalog number | |
| `dwc:collectionCode` | Collection code | |
| `dwc:institutionCode` | Institution code | "MNHN", "JAMSTEC" |
| `dwc:eventID` | Event identifier (literal) | |
| `dwc:surveyTargetID` | Survey target identifier | |
| `dcterms:identifier` | Record identifier | |

### dwc:Event — data properties

| Property | Description |
|---|---|
| `dwc:eventDate` | ISO 8601 date: "2023-06-15" or "2023-06" or "2023" |
| `dwc:eventTime` | Time of event |
| `dwc:year` | Integer year |
| `dwc:month` | Integer month (1–12) |
| `dwc:day` | Integer day |
| `dwc:eventType` | Type of event |
| `dwc:eventCategory` | Category |
| `dwc:eventID` | Identifier |
| `dwc:datasetName` | Name of the source dataset |
| `dwc:samplingProtocol` | Protocol name |
| `dwc:samplingEffort` | Effort description |
| `dwc:habitat` | Habitat description |
| `dwc:eventRemarks` | Free-text notes |
| `dwc:parentEventID` | Parent event identifier (literal) |
| `dcterms:title` | Event title |
| `dcterms:identifier` | Identifier |

### dcterms:Location — data properties (all geographic data lives here)

| Property | Description |
|---|---|
| `dwc:decimalLatitude` | Decimal degrees WGS84 — **coordinates are HERE** |
| `dwc:decimalLongitude` | Decimal degrees WGS84 — **coordinates are HERE** |
| `dwc:coordinateUncertaintyInMeters` | Positional uncertainty |
| `dwc:coordinatePrecision` | Precision |
| `dwc:geodeticDatum` | "WGS84" |
| `dwc:country` | Country name |
| `dwc:countryCode` | ISO 3166-1 alpha-2: "FR", "PH", "JP" |
| `dwc:stateProvince` | State or province |
| `dwc:county` | County |
| `dwc:municipality` | Municipality |
| `dwc:locality` | Locality description |
| `dwc:verbatimLocality` | Original locality string |
| `dwc:continent` | "Europe", "Asia", "North America", etc. |
| `dwc:waterBody` | Water body name |
| `dwc:island` | Island name |
| `dwc:islandGroup` | Island group |
| `dwc:higherGeography` | Broader geographic name |
| `dwc:minimumDepthInMeters` | Min depth (for aquatic) |
| `dwc:maximumDepthInMeters` | Max depth (for aquatic) |
| `dwc:minimumElevationInMeters` | Min elevation |
| `dwc:maximumElevationInMeters` | Max elevation |
| `dwc:footprintWKT` | WKT geometry string |
| `dwc:footprintSRS` | SRS for WKT |
| `dcterms:identifier` | Location identifier |

---

## Query patterns — copy and adapt these exactly

> Copy the entire pattern including all PREFIX lines.
> Change only the filter values (species names, country codes, years).
> Do not restructure the pattern.

### Pattern 1: List occurrences by taxon name (no location needed)
```sparql
PREFIX rdf:     <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs:    <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl:     <http://www.w3.org/2002/07/owl#>
PREFIX xsd:     <http://www.w3.org/2001/XMLSchema#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX dce:     <http://purl.org/dc/elements/1.1/>
PREFIX dwc:     <http://rs.tdwg.org/dwc/terms/>
PREFIX dwciri:  <http://rs.tdwg.org/dwc/iri/>
PREFIX dwcdp:   <http://rs.tdwg.org/dwcdp/terms/>
PREFIX eco:     <http://rs.tdwg.org/eco/terms/>
PREFIX ac:      <http://rs.tdwg.org/ac/terms/>

SELECT ?occ ?name ?basisOfRecord ?institutionCode WHERE {
  ?occ a dwc:Occurrence ;
       dwc:scientificName ?name .
  OPTIONAL { ?occ dwc:basisOfRecord   ?basisOfRecord }
  OPTIONAL { ?occ dwc:institutionCode ?institutionCode }
}
ORDER BY ?name
LIMIT 100
```

### Pattern 2: Coordinates — ALWAYS traverse Occurrence → Event → Location
```sparql
PREFIX rdf:     <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs:    <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl:     <http://www.w3.org/2002/07/owl#>
PREFIX xsd:     <http://www.w3.org/2001/XMLSchema#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX dce:     <http://purl.org/dc/elements/1.1/>
PREFIX dwc:     <http://rs.tdwg.org/dwc/terms/>
PREFIX dwciri:  <http://rs.tdwg.org/dwc/iri/>
PREFIX dwcdp:   <http://rs.tdwg.org/dwcdp/terms/>
PREFIX eco:     <http://rs.tdwg.org/eco/terms/>
PREFIX ac:      <http://rs.tdwg.org/ac/terms/>

SELECT ?name ?lat ?lon WHERE {
  ?occ a dwc:Occurrence ;
       dwc:scientificName ?name ;
       dwcdp:happenedDuring ?event .
  ?event dwcdp:spatialLocation ?loc .
  ?loc dwc:decimalLatitude  ?lat ;
       dwc:decimalLongitude ?lon .
}
LIMIT 100
```

### Pattern 3: Filter by species name + get full location
```sparql
PREFIX rdf:     <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs:    <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl:     <http://www.w3.org/2002/07/owl#>
PREFIX xsd:     <http://www.w3.org/2001/XMLSchema#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX dce:     <http://purl.org/dc/elements/1.1/>
PREFIX dwc:     <http://rs.tdwg.org/dwc/terms/>
PREFIX dwciri:  <http://rs.tdwg.org/dwc/iri/>
PREFIX dwcdp:   <http://rs.tdwg.org/dwcdp/terms/>
PREFIX eco:     <http://rs.tdwg.org/eco/terms/>
PREFIX ac:      <http://rs.tdwg.org/ac/terms/>

SELECT ?name ?lat ?lon ?country ?date WHERE {
  ?occ a dwc:Occurrence ;
       dwc:scientificName ?name ;
       dwcdp:happenedDuring ?event .
  ?event dwcdp:spatialLocation ?loc .
  OPTIONAL { ?loc   dwc:decimalLatitude  ?lat }
  OPTIONAL { ?loc   dwc:decimalLongitude ?lon }
  OPTIONAL { ?loc   dwc:country          ?country }
  OPTIONAL { ?event dwc:eventDate        ?date }
  FILTER(?name = "Abudefduf vaigiensis")
}
LIMIT 500
```

### Pattern 4: Filter by country code
```sparql
PREFIX rdf:     <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs:    <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl:     <http://www.w3.org/2002/07/owl#>
PREFIX xsd:     <http://www.w3.org/2001/XMLSchema#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX dce:     <http://purl.org/dc/elements/1.1/>
PREFIX dwc:     <http://rs.tdwg.org/dwc/terms/>
PREFIX dwciri:  <http://rs.tdwg.org/dwc/iri/>
PREFIX dwcdp:   <http://rs.tdwg.org/dwcdp/terms/>
PREFIX eco:     <http://rs.tdwg.org/eco/terms/>
PREFIX ac:      <http://rs.tdwg.org/ac/terms/>

SELECT ?name ?lat ?lon ?date WHERE {
  ?occ a dwc:Occurrence ;
       dwc:scientificName ?name ;
       dwcdp:happenedDuring ?event .
  ?event dwcdp:spatialLocation ?loc .
  ?loc dwc:countryCode         ?cc ;
       dwc:decimalLatitude     ?lat ;
       dwc:decimalLongitude    ?lon .
  OPTIONAL { ?event dwc:eventDate ?date }
  FILTER(?cc IN ("FR", "PH", "JP"))
}
LIMIT 500
```

### Pattern 5: Count occurrences per species
```sparql
PREFIX rdf:     <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs:    <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl:     <http://www.w3.org/2002/07/owl#>
PREFIX xsd:     <http://www.w3.org/2001/XMLSchema#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX dce:     <http://purl.org/dc/elements/1.1/>
PREFIX dwc:     <http://rs.tdwg.org/dwc/terms/>
PREFIX dwciri:  <http://rs.tdwg.org/dwc/iri/>
PREFIX dwcdp:   <http://rs.tdwg.org/dwcdp/terms/>
PREFIX eco:     <http://rs.tdwg.org/eco/terms/>
PREFIX ac:      <http://rs.tdwg.org/ac/terms/>

SELECT ?name (COUNT(?occ) AS ?n) WHERE {
  ?occ a dwc:Occurrence ;
       dwc:scientificName ?name .
}
GROUP BY ?name
ORDER BY DESC(?n)
LIMIT 50
```

### Pattern 6: Filter by year range (through Event)
```sparql
PREFIX rdf:     <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs:    <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl:     <http://www.w3.org/2002/07/owl#>
PREFIX xsd:     <http://www.w3.org/2001/XMLSchema#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX dce:     <http://purl.org/dc/elements/1.1/>
PREFIX dwc:     <http://rs.tdwg.org/dwc/terms/>
PREFIX dwciri:  <http://rs.tdwg.org/dwc/iri/>
PREFIX dwcdp:   <http://rs.tdwg.org/dwcdp/terms/>
PREFIX eco:     <http://rs.tdwg.org/eco/terms/>
PREFIX ac:      <http://rs.tdwg.org/ac/terms/>

SELECT ?name ?year ?month WHERE {
  ?occ a dwc:Occurrence ;
       dwc:scientificName ?name ;
       dwcdp:happenedDuring ?event .
  ?event dwc:year ?year .
  OPTIONAL { ?event dwc:month ?month }
  FILTER(?year >= 2015 && ?year <= 2023)
}
ORDER BY ?year ?month
LIMIT 200
```

### Pattern 7: Full record with recorder identity (Agent traversal)
```sparql
PREFIX rdf:     <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs:    <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl:     <http://www.w3.org/2002/07/owl#>
PREFIX xsd:     <http://www.w3.org/2001/XMLSchema#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX dce:     <http://purl.org/dc/elements/1.1/>
PREFIX dwc:     <http://rs.tdwg.org/dwc/terms/>
PREFIX dwciri:  <http://rs.tdwg.org/dwc/iri/>
PREFIX dwcdp:   <http://rs.tdwg.org/dwcdp/terms/>
PREFIX eco:     <http://rs.tdwg.org/eco/terms/>
PREFIX ac:      <http://rs.tdwg.org/ac/terms/>

SELECT ?name ?lat ?lon ?date ?recorder WHERE {
  ?occ a dwc:Occurrence ;
       dwc:scientificName ?name ;
       dwcdp:happenedDuring ?event .
  OPTIONAL {
    ?event dwcdp:spatialLocation ?loc .
    ?loc dwc:decimalLatitude  ?lat ;
         dwc:decimalLongitude ?lon .
  }
  OPTIONAL { ?event dwc:eventDate  ?date }
  OPTIONAL { ?occ   dwc:recordedBy ?recorder }
}
LIMIT 100
```

---

## dwc:OrganismInteraction — ecological interactions between two occurrences

This class is structurally unique in the ontology. Unlike every other class,
an OrganismInteraction links TWO dwc:Occurrence nodes in asymmetric roles:
one is the actor (subject), one is the target (object). Both are full
dwc:Occurrence instances with their own scientificName and properties.

### Graph structure

```
dwc:OrganismInteraction
├─ dwc:organismInteractionType   (string literal)
│    e.g. "visited flower of", "parasite of", "predator of"
├─ dwcdp:interactionBy   ──► dwc:Occurrence   (SUBJECT: the acting organism)
└─ dwcdp:interactionWith ──► dwc:Occurrence   (OBJECT: the target organism)
```

### Critical rules for interaction queries

1. **Always bind both occurrences with different variable names.**
   Use `?subjOcc` and `?objOcc` (or similar) — never reuse `?occ` for both.
   Reusing the same variable name will make the query match only
   self-interactions, returning 0 results.

2. **Always declare the rdf:type of both occurrences explicitly.**
   Write `?subjOcc a dwc:Occurrence` AND `?objOcc a dwc:Occurrence` —
   do not omit either, even if it seems redundant.

3. **Filter the object by scientificName to find interactions with a
   specific target species.** Filter the subject to find what interacts
   with something specific.

4. **Use COUNT + GROUP BY to find the most frequent interactor.**

5. **All variation patterns below require the same PREFIX declarations
   as the standard pattern.** Always copy the full PREFIX block.

### Standard query pattern — copy and adapt this exactly

```sparql
PREFIX rdf:     <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs:    <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl:     <http://www.w3.org/2002/07/owl#>
PREFIX xsd:     <http://www.w3.org/2001/XMLSchema#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX dce:     <http://purl.org/dc/elements/1.1/>
PREFIX dwc:     <http://rs.tdwg.org/dwc/terms/>
PREFIX dwciri:  <http://rs.tdwg.org/dwc/iri/>
PREFIX dwcdp:   <http://rs.tdwg.org/dwcdp/terms/>
PREFIX eco:     <http://rs.tdwg.org/eco/terms/>
PREFIX ac:      <http://rs.tdwg.org/ac/terms/>

SELECT ?subjectName (COUNT(*) AS ?n) WHERE {

  ?orgInt a dwc:OrganismInteraction ;
          dwc:organismInteractionType "visited flower of" ;
          dwcdp:interactionBy   ?subjOcc ;
          dwcdp:interactionWith ?objOcc .

  ?subjOcc a dwc:Occurrence ;
           dwc:scientificName ?subjectName .

  ?objOcc a dwc:Occurrence ;
          dwc:scientificName "Malus pumila" .
}
GROUP BY ?subjectName
ORDER BY DESC(?n)
LIMIT 20
```

### Variation A — Find all interactions a species participates in (as subject)

```sparql
PREFIX rdf:     <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs:    <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl:     <http://www.w3.org/2002/07/owl#>
PREFIX xsd:     <http://www.w3.org/2001/XMLSchema#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX dce:     <http://purl.org/dc/elements/1.1/>
PREFIX dwc:     <http://rs.tdwg.org/dwc/terms/>
PREFIX dwciri:  <http://rs.tdwg.org/dwc/iri/>
PREFIX dwcdp:   <http://rs.tdwg.org/dwcdp/terms/>
PREFIX eco:     <http://rs.tdwg.org/eco/terms/>
PREFIX ac:      <http://rs.tdwg.org/ac/terms/>

SELECT ?type ?objectName (COUNT(*) AS ?n) WHERE {
  ?orgInt a dwc:OrganismInteraction ;
          dwc:organismInteractionType ?type ;
          dwcdp:interactionBy   ?subjOcc ;
          dwcdp:interactionWith ?objOcc .

  ?subjOcc a dwc:Occurrence ;
           dwc:scientificName "Apis mellifera" .

  ?objOcc a dwc:Occurrence ;
          dwc:scientificName ?objectName .
}
GROUP BY ?type ?objectName
ORDER BY DESC(?n)
LIMIT 20
```

### Variation B — Find all interaction types in the dataset

```sparql
PREFIX rdf:     <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs:    <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl:     <http://www.w3.org/2002/07/owl#>
PREFIX xsd:     <http://www.w3.org/2001/XMLSchema#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX dce:     <http://purl.org/dc/elements/1.1/>
PREFIX dwc:     <http://rs.tdwg.org/dwc/terms/>
PREFIX dwciri:  <http://rs.tdwg.org/dwc/iri/>
PREFIX dwcdp:   <http://rs.tdwg.org/dwcdp/terms/>
PREFIX eco:     <http://rs.tdwg.org/eco/terms/>
PREFIX ac:      <http://rs.tdwg.org/ac/terms/>

SELECT ?type (COUNT(*) AS ?n) WHERE {
  ?orgInt a dwc:OrganismInteraction ;
          dwc:organismInteractionType ?type .
}
GROUP BY ?type
ORDER BY DESC(?n)
```

### Variation C — Find all species pairs for a given interaction type

```sparql
PREFIX rdf:     <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs:    <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl:     <http://www.w3.org/2002/07/owl#>
PREFIX xsd:     <http://www.w3.org/2001/XMLSchema#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX dce:     <http://purl.org/dc/elements/1.1/>
PREFIX dwc:     <http://rs.tdwg.org/dwc/terms/>
PREFIX dwciri:  <http://rs.tdwg.org/dwc/iri/>
PREFIX dwcdp:   <http://rs.tdwg.org/dwcdp/terms/>
PREFIX eco:     <http://rs.tdwg.org/eco/terms/>
PREFIX ac:      <http://rs.tdwg.org/ac/terms/>

SELECT ?subjectName ?objectName (COUNT(*) AS ?n) WHERE {
  ?orgInt a dwc:OrganismInteraction ;
          dwc:organismInteractionType "visited flower of" ;
          dwcdp:interactionBy   ?subjOcc ;
          dwcdp:interactionWith ?objOcc .

  ?subjOcc a dwc:Occurrence ;
           dwc:scientificName ?subjectName .

  ?objOcc a dwc:Occurrence ;
          dwc:scientificName ?objectName .
}
GROUP BY ?subjectName ?objectName
ORDER BY DESC(?n)
LIMIT 50
```

---

## Rules — read before every query

1. **Always declare all namespaces** — copy the full PREFIX block from the pattern
2. **Never put coordinates on Occurrence** — they do not exist there
3. **The coordinate path is always**: `?occ dwcdp:happenedDuring ?event . ?event dwcdp:spatialLocation ?loc . ?loc dwc:decimalLatitude ?lat`
4. **Use OPTIONAL** for any property that may not be present on all records
5. **Always add LIMIT** — use 100 for browsing, 500 for filtered queries, 5000 max
6. **For partial name matching**: `FILTER(CONTAINS(LCASE(?name), "search term"))`
7. **For exact name matching**: `FILTER(?name = "Exact Name")` — faster
8. **COUNT queries do not need LIMIT**
9. **dwcdp:happenedDuring on Event** means parent event (nested event hierarchy)
10. **dwcdp:happenedDuring on Occurrence** means the event this occurrence happened during — these are different uses of the same property on different subjects
11. **All SPARQL keywords MUST be UPPERCASE** — Ontop rejects lowercase `as`, `filter`, `optional`, `order by`, etc. Always write `AS`, `FILTER`, `OPTIONAL`, `ORDER BY`
12. **Never use REGEX()** — DuckDB cannot execute it via Ontop. Use instead:
    - Partial match: `FILTER(CONTAINS(LCASE(?name), "search term"))`
    - Exact match:   `FILTER(?name = "Exact Name")`
    - Starts with:   `FILTER(STRSTARTS(LCASE(?name), "prefix"))`