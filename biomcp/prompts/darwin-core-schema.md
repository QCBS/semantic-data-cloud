# Darwin Core Data Package — Ontology Reference

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
| Who did what surrounding an occurrence (recorder, identifier, conductor) | 6 |
| Measurements, body size, numeric values | 7 |
| Photos, images, audio, video | 8 |
| Taxonomic identification details | 9 |
| Information about a survey | 10 |
| Information about a molecular protocol | 11 |
| Information about the chronometric age of an occurrence | 12 |
| Information about the geological context surrounding a material entity | 13 |
| Information about the provenance of an event, material entity, media or occurrence | 14 |
| Ecological interactions between species | OrganismInteraction section |

---

## Prefix block — include relevant prefixes in every query

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

---

## Graph structure

Here are the object properties connecting the main classes in the ontology.

**`dwc:Occurrence`, `eco:Survey`, and `dwc:OrganismInteraction` are `rdfs:subClassOf dwc:Event`.**
Each of them is an event, so every `dwc:Event` property below (coordinates via location, dates, conducting agent, provenance) is available directly on the subject — no traversal to a separate event node is required.
`dwcdp:happenedDuring` keeps a single, consistent meaning everywhere: it links a `dwc:event` to its hierarchical parent `dwc:Event` (e.g. an occurrence that happened during a larger expedition or sampling event).

```
dwc:Event  (superclass — properties below are inherited by dwc:Occurrence, dwc:OrganismInteraction and eco:Survey)
├─ dwcdp:spatialLocation ──► dcterms:Location
│                            └─ dwcdp:georeferencedBy ──► dcterms:Agent
├─ dwcdp:conductedBy ──► dcterms:Agent
├─ dwcdp:happenedDuring ──► dwc:Event (parent event)
└─ dwcdp:hasProvenance ──► dwc:Provenance

dwc:Occurrence (subClassOf dwc:Event — inherits all properties above)
├─ dwcdp:occurrenceOf ──► dwc:Organism
├─ dwcdp:recordedBy ──► dcterms:Agent
└─ dwcdp:identifiedBy ──► dcterms:Agent

dwc:OrganismInteraction  (subClassOf dwc:Event — inherits all properties above)
├─ dwcdp:interactionBy ──► dwc:Occurrence (the acting organism)
└─ dwcdp:interactionWith ──► dwc:Occurrence (the target organism)

eco:Survey  (subClassOf dwc:Event — inherits all properties above)

dwc:MaterialEntity
├─ dwcdp:collectedDuring ──► dwc:Event
├─ dwcdp:evidenceFor ──► dwc:Occurrence
├─ dwcdp:hasProvenance ──► dwc:Provenance
└─ dwcdp:identifiedBy ──► dcterms:Agent

dwc:NucleotideAnalysis
├─ dwcdp:analysisOf ──► dwc:MaterialEntity
├─ dwcdp:materialCollectedDuring ──► dwc:Event
├─ dwcdp:followed ──► dwc:MolecularProtocol
└─ dwcdp:produced ──► dwc:NucleotideSequence

ac:Media — dwcdp:hasProvenance ──► dwc:Provenance

dwc:GeologicalContext — dwcdp:contextFor ──► dwc:MaterialEntity

dwc:Assertion — dwcdp:about ──► [any entity: Occurrence, MaterialEntity, ...]

dwc:OccurrenceMedia — dwcdp:hasContent ──► dwc:Occurrence
└─ dwcdp:thisMedia ──► ac:Media (ac:accessURI)

dwc:Identification — dwcdp:basedOn ──► [ac:Media, dwc:Occurrence, dwc:MaterialEntity, dwc:NucleotideAnalysis, dwc:NucleotideSequence]
└─ dwcdp:identifiedBy ──► dcterms:Agent

chrono:ChronometricAge — dwcdp:ageFor ──► dwc:Event (which can be a plain dwc:Event or any of its subclasses, dwc:Occurrence, dwc:OrganismInteraction or eco:Survey)
```

---

## Key properties per class

### dwc:Event

`dwc:eventID` · `dwc:datasetName` · `dwc:day` · `dwc:eventDate` · `dwc:eventRemarks` · `dwc:eventType` · `dwc:habitat` · `dwc:month` · `dwc:year`

These properties are available on any event resources: a plain `dwc:Event`, or its subclasses, `dwc:Occurrence`, `dwc:OrganismInteraction` or `eco:Survey`.

### dcterms:Location (reached via `dwcdp:spatialLocation` from any dwc:Event resource, including its subclasses)

`dwc:locationID` · `dwc:coordinateUncertaintyInMeters` · `dwc:country` · `dwc:countryCode` · `dwc:decimalLatitude` · `dwc:decimalLongitude` · `dwc:locality` · `dwc:locationRemarks` · `dwc:maximumDepthInMeters` · `dwc:minimumDepthInMeters` · `dwc:stateProvince` · `dwc:waterBody`

### dwc:Occurrence

Also inherits all `dwc:Event` properties directly (`dwc:day`, `dwc:eventDate`, `dwc:month`, `dwc:year`, `dwcdp:conductedBy`, `dwcdp:hasProvenance`, `dwcdp:spatialLocation` and `dwcdp:happenedDuring` to a parent event) — see Graph structure above.

`dwc:occurrenceID` · `dwc:behavior` · `dwc:identifiedBy` · `dwc:lifeStage` · `dwc:occurrenceRemarks` · `dwc:occurrenceStatus` · `dwc:organismQuantity` · `dwc:organismQuantityType` · `dwc:recordedBy` · `dwc:scientificName` · `dwc:sex` · `dwc:vitality`

### dwc:OrganismInteraction

Also inherits all `dwc:Event` properties directly (it is a `dwc:Event`) — see Graph structure above.

`dwc:organismInteractionID` · `dwc:organismInteractionDescription` · `dwc:organismInteractionType` · `dwc:relatedOrganismPart` · `dwc:subjectOrganismPart`

### eco:Survey

Also inherits all `dwc:Event` properties directly (it is a `dwc:Event`) — see Graph structure above.

`eco:surveyID` · `dwc:sampleSizeUnit` · `dwc:sampleSizeValue` · `eco:areNonTargetTaxaFullyReported` · `eco:isAbsenceReported` · `eco:isLeastSpecificTargetCategoryQuantityInclusive` · `eco:samplingEffortProtocol` · `eco:samplingEffortUnit` · `eco:samplingEffortValue` · `eco:samplingPerformedBy`

### dwc:Assertion (linked to its subject via dwcdp:about)

`dwc:assertionID` · `dwc:assertionMadeDate` · `dwc:assertionType` · `dwc:assertionUnit` · `dwc:assertionValue` · `dwc:assertionValueNumeric`

### dwc:GeologicalContext (linked to a dwc:MaterialEntity via dwcdp:contextFor)

`dwc:geologicalContextID` · `dwc:bed` · `dwc:earliestAgeOrLowestStage` · `dwc:earliestEpochOrLowestSeries` · `dwc:earliestEraOrLowestErathem` · `dwc:earliestPeriodOrLowestSystem` · `dwc:formation` · `dwc:group` · `dwc:latestAgeOrHighestStage` · `dwc:latestEpochOrHighestSeries` · `dwc:latestEraOrHighestErathem` · `dwc:latestPeriodOrHighestSystem` · `dwc:member`

### dwc:Identification (linked to its basis via dwcdp:basedOn)

`dwc:identificationID` · `dwc:dateIdentified` · `dwc:identificationRemarks` · `dwc:identificationVerificationStatus` · `dwc:identifiedBy` · `dwc:scientificName` · `dwc:taxonRank`

### dwc:MolecularProtocol

`dwc:molecularProtocolID` · `gbif:pcr_primer_name_forward` · `gbif:pcr_primer_name_reverse` · `mixs:0000041` · `mixs:0000044` · `mixs:0000045` · `mixs:0000050` · `mixs:0000086` · `mixs:0000087` · `gbif:pcr_primer_forward` · `gbif:pcr_primer_reverse`

### dwc:Provenance

`dwc:provenanceID` · `ac:fundingAttribution` · `ac:metadataCreatorLiteral` · `ac:providerLiteral` · `dc:creator` · `dcterms:bibliographicCitation` · `dcterms:references` · `dwc:datasetID` · `dwc:projectID` · `dwc:projectTitle`

### ac:Media (reached via dwc:OccurrenceMedia → dwcdp:thisMedia)

`dwc:mediaID` · `ac:accessURI` · `dc:format` · `dcterms:title` · `dcterms:type`

### chrono:ChronometricAge

`dwc:chronometricAgeID` · `chrono:chronometricAgeConversionProtocol` · `chrono:chronometricAgeConversionRemarks` · `chrono:earliestChronometricAge` `chrono:earliestChronometricAgeReferenceSystem` · `chrono:latestChronometricAge` `chrono:latestChronometricAgeReferenceSystem` · `chrono:materialDated` · `chrono:materialDatedRelationship` · `chrono:verbatimChronometricAge`

---

## Query patterns

### Pattern 1 — List occurrences by taxon name

```sparql
PREFIX dwc: <http://rs.tdwg.org/dwc/terms/>

SELECT ?occ

WHERE {
  ?occ a dwc:Occurrence ;
       dwc:scientificName "Chaetodon baronessa" .
}
LIMIT 100
```

### Pattern 2 — Occurrences with coordinates

`dwc:Occurrence` is a `dwc:Event`, so `dwcdp:spatialLocation` is available directly on it.
A `dcterms:Location` node is still required as an intermediate, as coordinates never sit directly on the occurrence's own properties.

```sparql
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX dwc: <http://rs.tdwg.org/dwc/terms/>
PREFIX dwcdp: <http://rs.tdwg.org/dwcdp/terms/>

SELECT ?lat ?lon ?country ?county ?locality ?locationRemarks ?stateProvince

WHERE {
  ?occ a dwc:Occurrence ;
       dwc:scientificName "Coccyzus americanus" ;
       dwcdp:spatialLocation ?loc .

  ?loc a dcterms:Location ;
       dwc:decimalLatitude ?lat ;
       dwc:decimalLongitude ?lon .

  OPTIONAL { ?loc dwc:country ?country }
  OPTIONAL { ?loc dwc:county ?county }
  OPTIONAL { ?loc dwc:locality ?locality }
  OPTIONAL { ?loc dwc:locationRemarks ?locationRemarks }
  OPTIONAL { ?loc dwc:stateProvince ?stateProvince }
}
LIMIT 200
```

### Pattern 3 — Filter by country or species with full location

```sparql
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX dwc: <http://rs.tdwg.org/dwc/terms/>
PREFIX dwcdp: <http://rs.tdwg.org/dwcdp/terms/>

SELECT ?lat ?lon ?country ?date

WHERE {
  ?occ a dwc:Occurrence ;
       dwc:scientificName "Abudefduf vaigiensis" ;
       dwcdp:spatialLocation ?loc .

  ?loc a dcterms:Location .

  OPTIONAL { ?occ dwc:eventDate ?date }
  OPTIONAL { ?loc dwc:decimalLatitude ?lat }
  OPTIONAL { ?loc dwc:decimalLongitude ?lon }
  OPTIONAL { ?loc dwc:country ?country }
}
LIMIT 500
```

### Pattern 4 — Filter by year range

`dwc:year` and `dwc:month` are inherited Event properties and sit directly on the occurrence — no traversal to a separate event is needed.

```sparql
PREFIX dwc: <http://rs.tdwg.org/dwc/terms/>

SELECT ?occ ?year ?month

WHERE {
  ?occ a dwc:Occurrence ;
       dwc:scientificName "Lutjanus viridis" ;
       dwc:year ?year .

  OPTIONAL { ?occ dwc:month ?month }
  FILTER(?year >= 1980 && ?year <= 2000)
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

### Pattern 6 — Who did what surrounding an occurrence

`dcterms:Agent` represents actors in various roles. They can be the recorders of a `dwc:Occurrence` via `dwcdp:recordedBy`, the identifiers of an occurrence via `dwcdp:identifiedBy`, or the conductor of an event via `dwcdp:conductedBy` — all directly on the occurrence.
The literal string properties `dwc:recordedBy` and `dwc:identifiedBy` on `dwc:Occurrence` are also available for simpler lookups.

```sparql
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX dwc: <http://rs.tdwg.org/dwc/terms/>
PREFIX dwcdp: <http://rs.tdwg.org/dwcdp/terms/>

SELECT ?identifierName ?identifierType ?conductorName ?conductorType
       ?identificationRemarks ?recorderName ?recorderType ?recordedBy ?identifiedBy

WHERE {
  ?occ a dwc:Occurrence ;
       dwc:scientificName "Actias luna" .

  OPTIONAL { ?occ dwc:identificationRemarks ?identificationRemarks }
  OPTIONAL { ?occ dwc:identifiedBy ?identifiedBy }
  OPTIONAL { ?occ dwc:recordedBy ?recordedBy }

  OPTIONAL {
    ?occ dwcdp:recordedBy ?recorder .

    ?recorder a dcterms:Agent ;
              dcterms:title ?recorderName ;
              dwc:agentType ?recorderType .
  }

  OPTIONAL {
    ?occ dwcdp:identifiedBy ?identifier .

    ?identifier a dcterms:Agent ;
                dcterms:title ?identifierName ;
                dwc:agentType ?identifierType .
  }

  OPTIONAL {
    ?occ dwcdp:conductedBy ?conductor .

    ?conductor a dcterms:Agent ;
               dcterms:title ?conductorName ;
               dwc:agentType ?conductorType .
  }
}
LIMIT 100
```

### Pattern 7 — Assertions (measurements or facts about any entity)

`dwc:Assertion` records a statement, be it numerical or categorical, about another resource.
You can link the assertion to its subject via `dwcdp:about`.
The subject can be any other entity, such as `dwc:Occurrence`, `dwc:MaterialEntity`, `dwc:Event`, or `ac:Media`.

```sparql
PREFIX dwc: <http://rs.tdwg.org/dwc/terms/>
PREFIX dwcdp: <http://rs.tdwg.org/dwcdp/terms/>

SELECT ?sciName (AVG(?val) AS ?avgVal) ?unit

WHERE {
  ?ass a dwc:Assertion ;
       dwc:assertionType "body size" ;
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

`dwc:OccurrenceMedia` is an entity that represents a `dwc:Occurrence` as content in a `ac:Media` item.
Variants include `dwc:EventMedia`, `dwc:MaterialMedia` and `dwc:OrganismMedia`.

```sparql
PREFIX ac: <http://rs.tdwg.org/ac/terms/>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX dwc: <http://rs.tdwg.org/dwc/terms/>
PREFIX dwcdp: <http://rs.tdwg.org/dwcdp/terms/>

SELECT ?accUri ?sciName ?subjectOrientationLiteral ?subjectPartLiteral ?title ?type ?format

WHERE {
  ?occMed a dwc:OccurrenceMedia ;
          dwcdp:thisMedia ?med ;
          dwcdp:hasContent ?occ .

  ?med a ac:Media ;
       ac:accessURI ?accUri .

  ?occ a dwc:Occurrence ;
       dwc:scientificName "Trapezia rufopunctata" .

  OPTIONAL { ?occMed ac:subjectOrientationLiteral ?subjectOrientationLiteral }
  OPTIONAL { ?occMed ac:subjectPartLiteral ?subjectPartLiteral }

  OPTIONAL { ?med dcterms:title ?title }
  OPTIONAL { ?med dcterms:type ?type }
  OPTIONAL { ?med dc:format ?format }
}
```

### Pattern 9 — Identification based on a specific entity type

`dwc:Identification` can be based on `dwc:Occurrence`, `dwc:MaterialEntity`, `dwc:NucleotideAnalysis`, `dwc:NucleotideSequence` or `ac:Media` — all linked via `dwcdp:basedOn`.

```sparql
PREFIX dwc: <http://rs.tdwg.org/dwc/terms/>
PREFIX dwcdp: <http://rs.tdwg.org/dwcdp/terms/>

SELECT ?iden ?mat ?materialEntityRemarks ?materialEntityType

WHERE {
  ?iden a dwc:Identification ;
        dwc:scientificName "Tremarctos ornatus" ;
        dwcdp:basedOn ?mat .

  ?mat a dwc:MaterialEntity .
  OPTIONAL { ?mat dwc:materialEntityRemarks ?materialEntityRemarks }
  OPTIONAL { ?mat dwc:materialEntityType ?materialEntityType }
}
```

### Pattern 10 — Information about a survey

`eco:Survey` is itself a `dwc:Event`, so its own date, location, and conducting agent sit directly on it.
Use its `eco:surveyID` to identify it directly.

```sparql
PREFIX dwc: <http://rs.tdwg.org/dwc/terms/>
PREFIX eco: <http://rs.tdwg.org/eco/terms/>

SELECT ?sampleSizeUnit ?sampleSizeValue ?samplingEffortProtocol ?samplingEffortUnit
       ?samplingEffortValue ?isAbsenceReported ?areNonTargetTaxaFullyReported
       ?isLeastSpecificTargetCategoryQuantityInclusive ?samplingPerformedBy

WHERE {
  ?surv a eco:Survey ;
        eco:surveyID "BROKE_WEST_RMT_004_RMT1" .

  OPTIONAL { ?surv dwc:sampleSizeUnit ?sampleSizeUnit }
  OPTIONAL { ?surv dwc:sampleSizeValue ?sampleSizeValue }

  OPTIONAL { ?surv eco:areNonTargetTaxaFullyReported ?areNonTargetTaxaFullyReported }
  OPTIONAL { ?surv eco:isAbsenceReported ?isAbsenceReported }
  OPTIONAL { ?surv eco:isLeastSpecificTargetCategoryQuantityInclusive ?isLeastSpecificTargetCategoryQuantityInclusive }
  OPTIONAL { ?surv eco:samplingEffortProtocol ?samplingEffortProtocol }
  OPTIONAL { ?surv eco:samplingEffortUnit ?samplingEffortUnit }
  OPTIONAL { ?surv eco:samplingEffortValue ?samplingEffortValue }
  OPTIONAL { ?surv eco:samplingPerformedBy ?samplingPerformedBy }
}
LIMIT 5
```

### Pattern 11 — Information about genomic data

Genomic data information is contained within `dwc:NucleotideAnalysis`. It links a `dwc:NucleotideSequence` to a `dwc:Event` and a `dwc:MaterialEntity` via a `dwc:MolecularProtocol`.

```sparql
PREFIX dwc: <http://rs.tdwg.org/dwc/terms/>
PREFIX dwcdp: <http://rs.tdwg.org/dwcdp/terms/>
PREFIX gbif: <http://rs.gbif.org/terms/>
PREFIX mixs: <https://w3id.org/mixs/>

SELECT ?molPro ?evtId ?libLayout ?targetGene ?targetSubfragment ?seqMeth
       ?otuSeqCompAppr ?otuDb ?pcrPrimerForward ?pcrPrimerReverse
       ?pcrPrimerNameForward ?pcrPrimerNameReverse

WHERE {
  ?nucAna a dwc:NucleotideAnalysis ;
          dwcdp:followed ?molPro ;
          dwcdp:materialCollectedDuring ?evt ;
          dwcdp:produced ?nucSeq .

  ?evt a dwc:Event ;
       dwc:eventID ?evtId .

  ?molPro a dwc:MolecularProtocol .

  OPTIONAL { ?molPro mixs:0000041 ?libLayout }
  OPTIONAL { ?molPro mixs:0000044 ?targetGene }
  OPTIONAL { ?molPro mixs:0000045 ?targetSubfragment }
  OPTIONAL { ?molPro mixs:0000050 ?seqMeth }
  OPTIONAL { ?molPro mixs:0000086 ?otuSeqCompAppr }
  OPTIONAL { ?molPro mixs:0000087 ?otuDb }

  OPTIONAL { ?molPro gbif:pcr_primer_forward ?pcrPrimerForward }
  OPTIONAL { ?molPro gbif:pcr_primer_reverse ?pcrPrimerReverse }
  OPTIONAL { ?molPro gbif:pcr_primer_name_forward ?pcrPrimerNameForward }
  OPTIONAL { ?molPro gbif:pcr_primer_name_reverse ?pcrPrimerNameReverse }

  ?nucSeq a dwc:NucleotideSequence .

  ?iden a dwc:Identification ;
        dwc:scientificName "Thysanoessa" ;
        dwcdp:basedOn ?nucSeq .
}
LIMIT 100
```

### Pattern 12 — Information about the chronometric age of an occurrence

`chrono:ChronometricAge` contains information about the chronometric age of an event resource. Since `dwc:Occurrence` is itself a `dwc:Event`, the occurrence can be dated directly via `dwcdp:ageFor`.

```sparql
PREFIX chrono: <http://rs.tdwg.org/chrono/terms/>
PREFIX dwc: <http://rs.tdwg.org/dwc/terms/>
PREFIX dwcdp: <http://rs.tdwg.org/dwcdp/terms/>

SELECT ?occ
       ?materialEntityRemarks ?preparations
       ?eventDate
       ?chronometricAgeConversionProtocol ?chronometricAgeConversionRemarks
       ?earliestChronometricAge ?earliestChronometricAgeReferenceSystem
       ?latestChronometricAge ?latestChronometricAgeReferenceSystem
       ?materialDated ?materialDatedRelationship ?verbatimChronometricAge

WHERE {
  ?occ a dwc:Occurrence ;
       dwc:scientificName "Odocoileus virginianus" .

  OPTIONAL { ?occ dwc:eventDate ?eventDate }

  ?mat a dwc:MaterialEntity ;
       dwcdp:evidenceFor ?occ .

  ?chro a chrono:ChronometricAge ;
        dwcdp:ageFor ?occ .

  OPTIONAL { ?mat dwc:materialEntityRemarks ?materialEntityRemarks }
  OPTIONAL { ?mat dwc:preparations ?preparations }

  OPTIONAL { ?chro chrono:chronometricAgeConversionProtocol ?chronometricAgeConversionProtocol }
  OPTIONAL { ?chro chrono:chronometricAgeConversionRemarks ?chronometricAgeConversionRemarks }
  OPTIONAL { ?chro chrono:materialDated ?materialDated }
  OPTIONAL { ?chro chrono:materialDatedRelationship ?materialDatedRelationship }
  OPTIONAL { ?chro chrono:earliestChronometricAge ?earliestChronometricAge }
  OPTIONAL { ?chro chrono:earliestChronometricAgeReferenceSystem ?earliestChronometricAgeReferenceSystem }
  OPTIONAL { ?chro chrono:latestChronometricAge ?latestChronometricAge }
  OPTIONAL { ?chro chrono:latestChronometricAgeReferenceSystem ?latestChronometricAgeReferenceSystem }
  OPTIONAL { ?chro chrono:verbatimChronometricAge ?verbatimChronometricAge }
}
LIMIT 100
```

### Pattern 13 — Information about the geological context surrounding a material entity

`dwc:GeologicalContext` contains information about the geological context of a `dwc:MaterialEntity`.
It is related to its corresponding `dwc:MaterialEntity` through the `dwcdp:contextFor` property.

```sparql
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX dwc: <http://rs.tdwg.org/dwc/terms/>
PREFIX dwcdp: <http://rs.tdwg.org/dwcdp/terms/>

SELECT ?mat ?geoCtx
       ?country ?county ?decimalLatitude ?decimalLongitude ?locality ?locationRemarks ?stateProvince
       ?bed ?earliestAgeOrLowestStage ?earliestEpochOrLowestSeries ?earliestEraOrLowestErathem
       ?earliestPeriodOrLowestSystem ?formation ?group ?latestAgeOrHighestStage
       ?latestEpochOrHighestSeries ?latestEraOrHighestErathem ?latestPeriodOrHighestSystem ?member

WHERE {
  ?mat a dwc:MaterialEntity ;
       dwc:scientificName "Carcharodon megalodon" ;
       dwcdp:collectedDuring ?evt .

  ?evt a dwc:Event ;
       dwcdp:spatialLocation ?loc .

  ?loc a dcterms:Location .

  ?geoCtx a dwc:GeologicalContext ;
          dwcdp:contextFor ?mat .

  OPTIONAL { ?loc dwc:country ?country }
  OPTIONAL { ?loc dwc:county ?county }
  OPTIONAL { ?loc dwc:decimalLatitude ?decimalLatitude }
  OPTIONAL { ?loc dwc:decimalLongitude ?decimalLongitude }
  OPTIONAL { ?loc dwc:locality ?locality }
  OPTIONAL { ?loc dwc:locationRemarks ?locationRemarks }
  OPTIONAL { ?loc dwc:stateProvince ?stateProvince }

  OPTIONAL { ?geoCtx dwc:bed ?bed }
  OPTIONAL { ?geoCtx dwc:earliestAgeOrLowestStage ?earliestAgeOrLowestStage }
  OPTIONAL { ?geoCtx dwc:earliestEpochOrLowestSeries ?earliestEpochOrLowestSeries }
  OPTIONAL { ?geoCtx dwc:earliestEraOrLowestErathem ?earliestEraOrLowestErathem }
  OPTIONAL { ?geoCtx dwc:earliestPeriodOrLowestSystem ?earliestPeriodOrLowestSystem }
  OPTIONAL { ?geoCtx dwc:formation ?formation }
  OPTIONAL { ?geoCtx dwc:group ?group }
  OPTIONAL { ?geoCtx dwc:latestAgeOrHighestStage ?latestAgeOrHighestStage }
  OPTIONAL { ?geoCtx dwc:latestEpochOrHighestSeries ?latestEpochOrHighestSeries }
  OPTIONAL { ?geoCtx dwc:latestEraOrHighestErathem ?latestEraOrHighestErathem }
  OPTIONAL { ?geoCtx dwc:latestPeriodOrHighestSystem ?latestPeriodOrHighestSystem }
  OPTIONAL { ?geoCtx dwc:member ?member }
}
LIMIT 100
```

### Pattern 14 — Information about the provenance of an occurrence

`dwc:Provenance` contains information about an entity's origin. This entity can be of various kinds, such as `dwc:Event`, `dwc:MaterialEntity` or `ac:Media`.
Since `dwc:Occurrence` is itself a `dwc:Event`, `dwcdp:hasProvenance` is available directly on the occurrence.

```sparql
PREFIX ac: <http://rs.tdwg.org/ac/terms/>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX dwc: <http://rs.tdwg.org/dwc/terms/>
PREFIX dwcdp: <http://rs.tdwg.org/dwcdp/terms/>

SELECT DISTINCT ?prov ?fundingAttribution ?metadataCreatorLiteral ?providerLiteral
       ?creatorLiteral ?bibliographicCitation ?references ?datasetID ?projectID ?projectTitle
WHERE {
  ?occ a dwc:Occurrence ;
       dwc:scientificName "Notolepis coatsi" ;
       dwcdp:hasProvenance ?prov .

  ?prov a dwc:Provenance .

  OPTIONAL { ?prov ac:fundingAttribution ?fundingAttribution }
  OPTIONAL { ?prov ac:metadataCreatorLiteral ?metadataCreatorLiteral }
  OPTIONAL { ?prov ac:providerLiteral ?providerLiteral }
  OPTIONAL { ?prov dc:creator ?creatorLiteral }
  OPTIONAL { ?prov dcterms:bibliographicCitation ?bibliographicCitation }
  OPTIONAL { ?prov dcterms:references ?references }
  OPTIONAL { ?prov dwc:datasetID ?datasetID }
  OPTIONAL { ?prov dwc:projectID ?projectID }
  OPTIONAL { ?prov dwc:projectTitle ?projectTitle }
}
LIMIT 100
```

---

## dwc:OrganismInteraction — ecological interactions between two occurrences

This class links two `dwc:Occurrence` nodes in asymmetric roles: one is the actor (subject), one is the target (object).

`dwc:OrganismInteraction` is also `rdfs:subClassOf dwc:Event`. It inherits `dwcdp:spatialLocation`, `dwc:eventDate`, `dwcdp:conductedBy`, and `dwcdp:hasProvenance` directly.

### Graph structure

```
dwc:OrganismInteraction (subClassOf dwc:Event)
├─ dwc:organismInteractionType (string: "visited flower of", "parasitized", ...)
├─ dwcdp:interactionBy ──► dwc:Occurrence (the acting organism)
├─ dwcdp:interactionWith ──► dwc:Occurrence (the target organism)
├─ dwcdp:spatialLocation ──► dcterms:Location (inherited from Event)
├─ dwc:eventDate / dwc:year / dwc:month / dwc:day  (inherited from Event)
└─ dwcdp:happenedDuring ──► dwc:Event (parent event, if any)
```

### Critical rules

1. Always use different variable names for each occurrence — `?subjOcc` and `?objOcc`.
2. Always declare `a dwc:Occurrence` for BOTH occurrences explicitly.
3. Filter `?objOcc` by scientificName to find what interacts with a specific species.
4. Filter `?subjOcc` by scientificName to find what a specific species interacts with.
5. To get the location or date of the interaction itself, query the properties directly on `?orgInt`.

### Standard pattern — What pollinates a specific plant?

```sparql
PREFIX dwc: <http://rs.tdwg.org/dwc/terms/>
PREFIX dwcdp: <http://rs.tdwg.org/dwcdp/terms/>

SELECT ?subjectName (COUNT(*) AS ?n)

WHERE {
  ?orgInt a dwc:OrganismInteraction ;
          dwc:organismInteractionType "visited flower of" ;
          dwcdp:interactionBy ?subjOcc ;
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

### Variation A — All interactions a species participates in (as actor), with location and date

```sparql
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX dwc: <http://rs.tdwg.org/dwc/terms/>
PREFIX dwcdp: <http://rs.tdwg.org/dwcdp/terms/>

SELECT ?type ?objectName ?eventDate ?country (COUNT(*) AS ?n)

WHERE {
  ?orgInt a dwc:OrganismInteraction ;
          dwc:organismInteractionType ?type ;
          dwcdp:interactionBy ?subjOcc ;
          dwcdp:interactionWith ?objOcc .

  ?subjOcc a dwc:Occurrence ;
           dwc:scientificName "Apis mellifera" .

  ?objOcc a dwc:Occurrence ;
          dwc:scientificName ?objectName .

  OPTIONAL { ?orgInt dwc:eventDate ?eventDate }
  OPTIONAL {
    ?orgInt dwcdp:spatialLocation ?loc .

    ?loc a dcterms:Location ;
         dwc:country ?country .
  }
}
GROUP BY ?type ?objectName ?eventDate ?country
ORDER BY DESC(?n)
LIMIT 20
```

### Variation B — All interaction types in the dataset

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

### Variation C — All species pairs for a given interaction type

```sparql
PREFIX dwc: <http://rs.tdwg.org/dwc/terms/>
PREFIX dwcdp: <http://rs.tdwg.org/dwcdp/terms/>

SELECT ?subjectName ?objectName (COUNT(*) AS ?n)

WHERE {
  ?orgInt a dwc:OrganismInteraction ;
          dwc:organismInteractionType "visited flower of" ;
          dwcdp:interactionBy ?subjOcc ;
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
2. `dwc:Occurrence`, `eco:Survey`, and `dwc:OrganismInteraction` are `rdfs:subClassOf dwc:Event`, so coordinates CAN be reached directly from any of them: `?occ dwcdp:spatialLocation ?loc . ?loc dwc:decimalLatitude ?lat`. A `dcterms:Location` intermediate node is still always required — coordinates are never literal properties of the occurrence/survey/interaction itself.
3. Dates and years are inherited `dwc:Event` properties, so they sit directly on `dwc:Occurrence`, `dwc:OrganismInteraction` and `eco:Survey` — no traversal needed to reach them on these classes.
4. Use OPTIONAL for any property that may be absent on some records
5. Always add LIMIT — 100 for browsing, 500 for filtered queries; omit for aggregations
6. ALL SPARQL keywords UPPERCASE: AS, FILTER, OPTIONAL, ORDER BY, GROUP BY, WHERE
7. NEVER use REGEX() — DuckDB cannot execute it via Ontop. Use instead:
  - Exact match: `FILTER(?x = "Exact Value")`
  - Partial match: `FILTER(CONTAINS(LCASE(?x), "term"))`
  - Starts with: `FILTER(STRSTARTS(LCASE(?x), "prefix"))`
8. COUNT queries do not need LIMIT
9. `dwcdp:happenedDuring` has ONE consistent meaning everywhere: it links a `dwc:Event` resource (a plain `dwc:Event`, or a subclass like `dwc:Occurrence`, `dwc:OrganismInteraction` or `eco:Survey` acting as one) to its containing parent `dwc:Event`. It is never needed to reach an entity's own date, location, or conducting agent — only to reach a broader event that contains it.
10. Because `dwc:Occurrence`, `dwc:OrganismInteraction` and `eco:Survey` are subclasses of `dwc:Event`, `?x a dwc:Event` may also match instances only ever asserted as one of these subclasses. If a pattern specifically needs a "plain" event that is not any of these, and this matters for the question being asked, scope it with `FILTER NOT EXISTS { ?evt a dwc:Occurrence }` (and similarly for the other subclasses) rather than assuming `a dwc:Event` excludes them.

---

## When a query returns 0 results

Try in this order:

1. Run `SELECT * WHERE { ?s ?p ?o } LIMIT 10` to confirm the endpoint has data at all
2. Remove FILTER clauses one by one — identify which one eliminates all results
3. Check every traversal chain — coordinates always go through a `dcterms:Location` node (whether reached from a plain `dwc:Event` or directly from its subclasses of `dwc:Occurrence`, `dwc:OrganismInteraction` or `eco:Survey`); dates are either directly on the resource or on a related `dwc:Event` reached via `dwcdp:happenedDuring`
4. Wrap non-essential triples in `OPTIONAL { }` and add them back one at a time