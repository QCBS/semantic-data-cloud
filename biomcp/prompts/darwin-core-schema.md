# Darwin Core Data Package — Ontology Reference

> Injected into every SPARQL tool call.
> Describes the EXACT graph structure of this endpoint.
> Do NOT assume flat Darwin Core — this uses DWC-DP linked object properties.

---

## Instructions — read before writing any SPARQL

USE THE PATTERNS. Every query type has a worked example below.
Find the matching pattern, copy it, adapt filter values only.
Do not invent new graph traversals.

| User asks about... | Pattern |
|---|---|
| Species names, occurrences, lists | 1 |
| Coordinates, map positions | 2 |
| Country, locality, geographic filter | 3 |
| Dates, years, months | 4 |
| Counts, rankings, aggregations | 5 |
| Who recorded or collected | 6 |
| Measurements, body size, numeric values | 7 |
| Photos, images, audio, video | 8 |
| Taxonomic identification details | 9 |
| Ecological interactions between species | OrganismInteraction section |

---

## Prefix block — include relevant prefixes in every query

```sparql
PREFIX ac: <http://rs.tdwg.org/ac/terms/>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX dwc: <http://rs.tdwg.org/dwc/terms/>
PREFIX dwcdp: <http://rs.tdwg.org/dwcdp/terms/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
```

---

## Graph structure

There are NO coordinates or dates directly on dwc:Occurrence.
You MUST traverse the object property chain to reach them.

```
dwc:Occurrence
├─ dwcdp:happenedDuring  ──► dwc:Event
│                              ├─ dwcdp:spatialLocation ──► dcterms:Location
│                              │                              dwc:decimalLatitude
│                              │                              dwc:decimalLongitude
│                              │                              dwc:country, dwc:stateProvince
│                              ├─ dwc:eventDate, dwc:year, dwc:month
│                              └─ dwcdp:happenedDuring  ──► dwc:Event  (parent event)
├─ dwcdp:occurrenceOf    ──► dwc:Organism
├─ dwcdp:recordedBy      ──► dcterms:Agent
└─ dwcdp:identifiedBy    ──► dcterms:Agent

dwc:Assertion            — dwcdp:about ──► [any entity: Occurrence, MaterialEntity, ...]
dwc:OccurrenceMedia      — dwcdp:hasContent ──► [any entity: Occurrence, MaterialEntity, ...]
                         — dwcdp:thisMedia   ──► dwc:Media  (ac:accessURI)
dwc:Identification       — dwcdp:basedOn ──► [Occurrence, MaterialEntity, Media,
                                               NucleotideAnalysis, NucleotideSequence]
```

---

## Key properties per class

### dwc:Occurrence (direct — no traversal needed)
`dwc:scientificName` · `dwc:occurrenceID` · `dwc:occurrenceStatus`
`dwc:sex` · `dwc:lifeStage` · `dwc:vitality` · `dwc:behavior`
`dwc:recordedBy` · `dwc:identifiedBy` · `dwc:organismQuantity` · `dwc:organismQuantityType`

### dwc:Event (reached via dwcdp:happenedDuring)
`dwc:eventDate` · `dwc:year` · `dwc:month` · `dwc:day`
`dwc:eventType` · `dwc:habitat` · `dwc:datasetName`

### dcterms:Location (reached via dwc:Event → dwcdp:spatialLocation)
`dwc:decimalLatitude` · `dwc:decimalLongitude` · `dwc:coordinateUncertaintyInMeters`
`dwc:country` · `dwc:countryCode` · `dwc:stateProvince` · `dwc:locality`
`dwc:waterBody` · `dwc:minimumDepthInMeters` · `dwc:maximumDepthInMeters`

### dwc:Assertion (linked to its subject via dwcdp:about)
`dwc:assertionType` · `dwc:assertionValue` · `dwc:assertionValueNumeric`
`dwc:assertionUnit` · `dwc:assertionMadeDate`

### dwc:Identification (linked to its basis via dwcdp:basedOn)
`dwc:scientificName` · `dwc:identifiedBy` · `dwc:dateIdentified`
`dwc:taxonRank` · `dwc:identificationVerificationStatus`

### dwc:Media (reached via dwc:OccurrenceMedia → dwcdp:thisMedia)
`ac:accessURI` · `dcterms:title` · `dcterms:type` · `dc:format`

---

## Query patterns

### Pattern 1 — List occurrences by taxon name

```sparql
PREFIX dwc: <http://rs.tdwg.org/dwc/terms/>

SELECT ?occ ?name
WHERE {
  ?occ a dwc:Occurrence ;
       dwc:scientificName ?name .
  FILTER(CONTAINS(LCASE(?name), "abudefduf"))
}
ORDER BY ?name
LIMIT 100
```

### Pattern 2 — Occurrences with coordinates
Coordinates are on dcterms:Location, never on Occurrence. Always traverse.

```sparql
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX dwc: <http://rs.tdwg.org/dwc/terms/>
PREFIX dwcdp: <http://rs.tdwg.org/dwcdp/terms/>

SELECT ?name ?lat ?lon
WHERE {
  ?occ a dwc:Occurrence ;
       dwc:scientificName ?name ;
       dwcdp:happenedDuring ?evt .

  ?evt dwcdp:spatialLocation ?loc .

  ?loc dwc:decimalLatitude  ?lat ;
       dwc:decimalLongitude ?lon .
}
LIMIT 200
```

### Pattern 3 — Filter by country or species with full location

```sparql
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX dwc: <http://rs.tdwg.org/dwc/terms/>
PREFIX dwcdp: <http://rs.tdwg.org/dwcdp/terms/>

SELECT ?name ?lat ?lon ?country ?date
WHERE {
  ?occ a dwc:Occurrence ;
       dwc:scientificName ?name ;
       dwcdp:happenedDuring ?evt .

  ?evt dwcdp:spatialLocation ?loc .
  OPTIONAL { ?evt dwc:eventDate ?date }
  OPTIONAL { ?loc dwc:decimalLatitude  ?lat }
  OPTIONAL { ?loc dwc:decimalLongitude ?lon }
  OPTIONAL { ?loc dwc:country ?country }

  FILTER(?name = "Abudefduf vaigiensis")
}
LIMIT 500
```

### Pattern 4 — Filter by year range

```sparql
PREFIX dwc: <http://rs.tdwg.org/dwc/terms/>
PREFIX dwcdp: <http://rs.tdwg.org/dwcdp/terms/>

SELECT ?name ?year ?month
WHERE {
  ?occ a dwc:Occurrence ;
       dwc:scientificName ?name ;
       dwcdp:happenedDuring ?evt .

  ?evt dwc:year ?year .
  OPTIONAL { ?evt dwc:month ?month }
  FILTER(?year >= 2015 && ?year <= 2023)
}
ORDER BY ?year ?month
LIMIT 200
```

### Pattern 5 — Count or rank by species

```sparql
PREFIX dwc: <http://rs.tdwg.org/dwc/terms/>

SELECT ?name (COUNT(?occ) AS ?n)
WHERE {
  ?occ a dwc:Occurrence ;
       dwc:scientificName ?name .
}
GROUP BY ?name
ORDER BY DESC(?n)
LIMIT 50
```

### Pattern 6 — Who recorded an occurrence

```sparql
PREFIX dwc: <http://rs.tdwg.org/dwc/terms/>

SELECT ?name ?recorder
WHERE {
  ?occ a dwc:Occurrence ;
       dwc:scientificName ?name ;
       dwc:recordedBy ?recorder .
  FILTER(CONTAINS(LCASE(?name), "tremarctos"))
}
LIMIT 100
```

### Pattern 7 — Assertions (measurements about any entity)
dwc:Assertion records numeric or categorical measurements.
Link from assertion to its subject via dwcdp:about.
Subject can be Occurrence, MaterialEntity, Event, Organism, or Media.

```sparql
PREFIX dwc: <http://rs.tdwg.org/dwc/terms/>
PREFIX dwcdp: <http://rs.tdwg.org/dwcdp/terms/>

SELECT ?sciName (AVG(?val) AS ?avgVal) ?unit
WHERE {
  ?ass a dwc:Assertion ;
       dwc:assertionType 'body size' ;
       dwc:assertionValueNumeric ?val ;
       dwc:assertionUnit ?unit ;
       dwcdp:about ?occ .

  ?occ a dwc:Occurrence ;
       dwc:scientificName ?sciName .
}
GROUP BY ?sciName ?unit
ORDER BY DESC(?avgVal)
```

### Pattern 8 — Media linked to an occurrence (OccurrenceMedia)
dwc:OccurrenceMedia is an entity that represents a dwc:Occurrence as content
in a dwc:Media item. Variants: dwc:EventMedia, dwc:MaterialMedia, dwc:OrganismMedia.

```sparql
PREFIX ac: <http://rs.tdwg.org/ac/terms/>
PREFIX dwc: <http://rs.tdwg.org/dwc/terms/>
PREFIX dwcdp: <http://rs.tdwg.org/dwcdp/terms/>

SELECT ?accUri ?sciName
WHERE {
  ?occMed a dwc:OccurrenceMedia ;
          dwcdp:thisMedia ?med ;
          dwcdp:hasContent ?occ .

  ?med a dwc:Media ;
       ac:accessURI ?accUri .

  ?occ a dwc:Occurrence ;
       dwc:scientificName 'Trapezia rufopunctata' .
}
```

### Pattern 9 — Identification based on a specific entity type
dwc:Identification can be based on Occurrence, MaterialEntity, Media,
NucleotideAnalysis, or NucleotideSequence - all linked via dwcdp:basedOn.

```sparql
PREFIX dwc:   <http://rs.tdwg.org/dwc/terms/>
PREFIX dwcdp: <http://rs.tdwg.org/dwcdp/terms/>

SELECT ?iden ?mat ?rems
WHERE {
  ?iden a dwc:Identification ;
        dwc:scientificName 'Tremarctos ornatus' ;
        dwcdp:basedOn ?mat .

  ?mat a dwc:MaterialEntity .
  OPTIONAL { ?mat dwc:materialEntityRemarks ?rems }
}
```

---

## dwc:OrganismInteraction — ecological interactions between two occurrences

This class links two dwc:Occurrence nodes in asymmetric roles:
one is the actor (subject), one is the target (object).

### Graph structure

```
dwc:OrganismInteraction
├─ dwc:organismInteractionType  (string: "visited flower of", "parasite of", ...)
├─ dwcdp:interactionBy   ──► dwc:Occurrence   (the acting organism)
└─ dwcdp:interactionWith ──► dwc:Occurrence   (the target organism)
```

### Critical rules

1. Always use different variable names for each occurrence — `?subjOcc` and `?objOcc`.
   Reusing the same variable matches only self-interactions, returning 0 results.
2. Always declare `a dwc:Occurrence` for BOTH occurrences explicitly.
3. Filter `?objOcc` by scientificName to find what interacts with a specific species.
4. Filter `?subjOcc` by scientificName to find what a specific species interacts with.

### Standard pattern — what pollinates a specific plant?

```sparql
PREFIX dwc: <http://rs.tdwg.org/dwc/terms/>
PREFIX dwcdp: <http://rs.tdwg.org/dwcdp/terms/>

SELECT ?subjectName (COUNT(*) AS ?n)
WHERE {
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

### Variation A — all interactions a species participates in (as actor)

```sparql
PREFIX dwc: <http://rs.tdwg.org/dwc/terms/>
PREFIX dwcdp: <http://rs.tdwg.org/dwcdp/terms/>

SELECT ?type ?objectName (COUNT(*) AS ?n)
WHERE {
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

### Variation B — all interaction types in the dataset

```sparql
PREFIX dwc: <http://rs.tdwg.org/dwc/terms/>

SELECT ?type (COUNT(*) AS ?n)
WHERE {
  ?orgInt a dwc:OrganismInteraction ;
          dwc:organismInteractionType ?type .
}
GROUP BY ?type
ORDER BY DESC(?n)
```

### Variation C — all species pairs for a given interaction type

```sparql
PREFIX dwc: <http://rs.tdwg.org/dwc/terms/>
PREFIX dwcdp: <http://rs.tdwg.org/dwcdp/terms/>

SELECT ?subjectName ?objectName (COUNT(*) AS ?n)
WHERE {
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

## Rules

1. Declare all namespaces used in the query at the top
2. NEVER place coordinates on Occurrence — the path is always:
   `?occ dwcdp:happenedDuring ?evt . ?evt dwcdp:spatialLocation ?loc . ?loc dwc:decimalLatitude ?lat`
3. Dates and years are on dwc:Event, not on Occurrence
4. Use OPTIONAL for any property that may be absent on some records
5. Always add LIMIT — 100 for browsing, 500 for filtered queries; omit for aggregations
6. ALL SPARQL keywords UPPERCASE: AS, FILTER, OPTIONAL, ORDER BY, GROUP BY, WHERE
7. NEVER use REGEX() — DuckDB cannot execute it via Ontop. Use instead:
   - Partial match: `FILTER(CONTAINS(LCASE(?x), "term"))`
   - Exact match: `FILTER(?x = "Exact Value")`
   - Starts with: `FILTER(STRSTARTS(LCASE(?x), "prefix"))`
8. COUNT queries do not need LIMIT
9. dwcdp:happenedDuring on Occurrence links to the event it occurred during;
   dwcdp:happenedDuring on Event links to its parent event — different meanings, same property