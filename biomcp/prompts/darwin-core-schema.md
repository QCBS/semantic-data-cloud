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
| Who did what surrounding the event of an occurrence | 6 |
| Measurements, body size, numeric values | 7 |
| Photos, images, audio, video | 8 |
| Taxonomic identification details | 9 |
| Information about a survey | 10 |
| Information about a molecular protocol | 11 |
| Information about the chronometric age surrounding the event of an occurrence | 12 |
| Information about the geological context surrounding a material entity | 13 |
| Information about the provenance of an event, material entity or occurrence | 14 |
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
There are NO coordinates or dates directly on dwc:Occurrence.
You MUST traverse the object property chain to reach them.

```
dwc:Occurrence
├─ dwcdp:happenedDuring ──► dwc:Event
│                              ├─ dwcdp:spatialLocation ──► dcterms:Location
│                              │                            └─ dwcdp:georeferencedBy ──► dcterms:Agent
│                              ├─ dwcdp:conductedBy ──► dcterms:Agent
│                              ├─ dwcdp:happenedDuring ──► dwc:Event (parent event)
│                              └─ dwcdp:hasProvenance ──► dwc:Provenance
├─ dwcdp:occurrenceOf ──► dwc:Organism
├─ dwcdp:recordedBy ──► dcterms:Agent
└─ dwcdp:identifiedBy ──► dcterms:Agent

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

dwc:OrganismInteraction
├─ dwcdp:happenedDuring ──► dwc:Event
├─ dwcdp:interactionBy ──► dwc:Occurrence
└─ dwcdp:interactionWith ──► dwc:Occurrence

dwc:Survey — dwcdp:happenedDuring ──► dwc:Event

dwc:Media — dwcdp:hasProvenance ──► dwc:Provenance

dwc:GeologicalContext — dwcdp:contextFor ──► dwc:MaterialEntity

dwc:Assertion — dwcdp:about ──► [any entity: Occurrence, MaterialEntity, ...]

dwc:OccurrenceMedia — dwcdp:hasContent ──► dwc:Occurrence
└─ dwcdp:thisMedia ──► dwc:Media (ac:accessURI)

dwc:Identification — dwcdp:basedOn ──► [Occurrence, MaterialEntity, Media,
├─                                      NucleotideAnalysis, NucleotideSequence]
└─ dwcdp:identifiedBy ──► dcterms:Agent

chrono:ChronometricAge — dwcdp:ageFor ──► dwc:Event
```

---


## Key properties per class

### dwc:Occurrence
`dwc:occurrenceID` · `dwc:scientificName` · `dwc:occurrenceStatus`
`dwc:sex` · `dwc:lifeStage` · `dwc:vitality` · `dwc:behavior`
`dwc:recordedBy` · `dwc:identifiedBy` · `dwc:organismQuantity` · `dwc:organismQuantityType` · `dwc:occurrenceRemarks`

### dwc:Event (reached via dwcdp:happenedDuring)
`dwc:eventID` · `dwc:eventDate` · `dwc:year` · `dwc:month` · `dwc:day`
`dwc:eventType` · `dwc:habitat` · `dwc:datasetName` · `dwc:eventRemarks`

### dcterms:Location (reached via dwc:Event → dwcdp:spatialLocation)
`dwc:locationID` · `dwc:decimalLatitude` · `dwc:decimalLongitude` · `dwc:coordinateUncertaintyInMeters`
`dwc:country` · `dwc:countryCode` · `dwc:stateProvince` · `dwc:locality`
`dwc:waterBody` · `dwc:minimumDepthInMeters` · `dwc:maximumDepthInMeters` · `dwc:locationRemarks`

### dwc:Assertion (linked to its subject via dwcdp:about)
`dwc:assertionID` · `dwc:assertionType` · `dwc:assertionValue` · `dwc:assertionValueNumeric`
`dwc:assertionUnit` · `dwc:assertionMadeDate`

### dwc:Identification (linked to its basis via dwcdp:basedOn)
`dwc:identificationID` · `dwc:scientificName` · `dwc:identifiedBy` · `dwc:dateIdentified`
`dwc:taxonRank` · `dwc:identificationVerificationStatus` · `dwc:identificationRemarks`

### dwc:Media (reached via dwc:OccurrenceMedia → dwcdp:thisMedia)
`dwc:mediaID` · `ac:accessURI` · `dcterms:title` · `dcterms:type` · `dc:format`

### dwc:Survey (linked to a dwc:Event via dwcdp:happenedDuring)
`dwc:surveyID` · `dwc:sampleSizeUnit` · `dwc:sampleSizeValue` · `eco:areNonTargetTaxaFullyReported`
`eco:isAbsenceReported` · `eco:isLeastSpecificTargetCategoryQuantityInclusive` · `eco:samplingEffortProtocol`
`eco:samplingEffortUnit` · `eco:samplingEffortValue` · `eco:samplingPerformedBy`

### dwc:GeologicalContext (linked to a dwc:MaterialEntity via dwcdp:contextFor)
`dwc:geologicalContextID` · `dwc:bed` · `dwc:earliestAgeOrLowestStage` · `dwc:earliestEpochOrLowestSeries`
`dwc:earliestEraOrLowestErathem` · `dwc:earliestPeriodOrLowestSystem` · `dwc:formation` · `dwc:group`
`dwc:latestAgeOrHighestStage` · `dwc:latestEpochOrHighestSeries` · `dwc:latestEraOrHighestErathem`
`dwc:latestPeriodOrHighestSystem` · `dwc:member`

### dwc:MolecularProtocol
`dwc:molecularProtocolID` · `mixs:0000041` · `mixs:0000044`
`mixs:0000045` · `mixs:0000050` · `mixs:0000086` · `mixs:0000087`
`gbif:pcr_primer_forward` · `gbif:pcr_primer_reverse` · `gbif:pcr_primer_name_forward` · `gbif:pcr_primer_name_reverse`

### dwc:Provenance
`dwc:provenanceID` · `ac:fundingAttribution` · `ac:metadataCreatorLiteral` · `ac:providerLiteral`
`dc:creator` · `dcterms:bibliographicCitation` · `dcterms:references`
`dwc:datasetID` · `dwc:projectID` · `dwc:projectTitle`

### dwc:OrganismInteraction
`dwc:organismInteractionID` · `dwc:organismInteractionDescription` · `dwc:subjectOrganismPart`
`dwc:organismInteractionType` · `dwc:relatedOrganismPart`

### chrono:ChronometricAge
`dwc:chronometricAgeID` · `chrono:chronometricAgeConversionProtocol` · `chrono:chronometricAgeConversionRemarks`
`chrono:materialDated` · `chrono:materialDatedRelationship` · `chrono:earliestChronometricAge`
`chrono:earliestChronometricAgeReferenceSystem` · `chrono:latestChronometricAge`
`chrono:latestChronometricAgeReferenceSystem` · `chrono:verbatimChronometricAge`

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
Coordinates are on dcterms:Location, never on Occurrence. Always traverse.

```sparql
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX dwc: <http://rs.tdwg.org/dwc/terms/>
PREFIX dwcdp: <http://rs.tdwg.org/dwcdp/terms/>

SELECT ?lat ?lon
WHERE {
  ?occ a dwc:Occurrence ;
       dwc:scientificName "Coccyzus americanus" ;
       dwcdp:happenedDuring ?evt .

  ?evt dwcdp:spatialLocation ?loc .

  ?loc dwc:decimalLatitude ?lat ;
       dwc:decimalLongitude ?lon .
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
       dwcdp:happenedDuring ?evt .

  ?evt dwcdp:spatialLocation ?loc .
  OPTIONAL { ?evt dwc:eventDate ?date }
  OPTIONAL { ?loc dwc:decimalLatitude ?lat }
  OPTIONAL { ?loc dwc:decimalLongitude ?lon }
  OPTIONAL { ?loc dwc:country ?country }
}
LIMIT 500
```

### Pattern 4 — Filter by year range

```sparql
PREFIX dwc: <http://rs.tdwg.org/dwc/terms/>
PREFIX dwcdp: <http://rs.tdwg.org/dwcdp/terms/>

SELECT ?occ ?year ?month
WHERE {
  ?occ a dwc:Occurrence ;
       dwc:scientificName "Lutjanus viridis" ;
       dwcdp:happenedDuring ?evt .

  ?evt dwc:year ?year .

  OPTIONAL { ?evt dwc:month ?month }
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
dcterms:Agent represents actors in various roles. They can be the recorders of a dwc:Occurrence
via dwcdp:recordedBy, the identifiers of an occurrence via dwcdp:identifiedBy, or the conductors
of a dwc:Event via dwcdp:conductedBy. The literal string properties dwc:recordedBy and
dwc:identifiedBy on dwc:Occurrence are also available for simpler lookups.

```sparql
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX dwc: <http://rs.tdwg.org/dwc/terms/>
PREFIX dwcdp: <http://rs.tdwg.org/dwcdp/terms/>

SELECT ?identifierName ?identifierType ?conductorName ?conductorType
       ?identificationRemarks ?recorderName ?recorderType ?recordedBy ?identifiedBy
WHERE {
  ?occ a dwc:Occurrence ;
       dwc:scientificName "Actias luna" ;
       dwcdp:happenedDuring ?evt .

  ?evt a dwc:Event .

  OPTIONAL { ?occ dwc:identificationRemarks ?identificationRemarks }
  OPTIONAL { ?occ dwc:identifiedBy ?identifiedBy }
  OPTIONAL { ?occ dwc:recordedBy ?recordedBy }

  OPTIONAL {
    ?evt dwcdp:recordedBy ?recorder .
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
    ?evt dwcdp:conductedBy ?conductor .
    ?conductor a dcterms:Agent ;
               dcterms:title ?conductorName ;
               dwc:agentType ?conductorType .
  }
}
LIMIT 100
```

### Pattern 7 — Assertions (measurements about any entity)
dwc:Assertion records numeric or categorical measurements.
Link from assertion to its subject via dwcdp:about.
Subject can be any other entity, such as dwc:Occurrence, dwc:MaterialEntity, dwc:Event, or dwc:Media.

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
dwc:OccurrenceMedia is an entity that represents a dwc:Occurrence as content in a dwc:Media item.
Variants include dwc:EventMedia, dwc:MaterialMedia, dwc:OrganismMedia.

```sparql
PREFIX ac: <http://rs.tdwg.org/ac/terms/>
PREFIX dwc: <http://rs.tdwg.org/dwc/terms/>
PREFIX dwcdp: <http://rs.tdwg.org/dwcdp/terms/>

SELECT ?accUri ?sciName ?subjectOrientationLiteral ?subjectPartLiteral
WHERE {
  ?occMed a dwc:OccurrenceMedia ;
          dwcdp:thisMedia ?med ;
          dwcdp:hasContent ?occ .

  ?med a dwc:Media ;
       ac:accessURI ?accUri .

  ?occ a dwc:Occurrence ;
       dwc:scientificName "Trapezia rufopunctata" .

  OPTIONAL { ?occMed ac:subjectOrientationLiteral ?subjectOrientationLiteral }
  OPTIONAL { ?occMed ac:subjectPartLiteral ?subjectPartLiteral }
}
```

### Pattern 9 — Identification based on a specific entity type
dwc:Identification can be based on Occurrence, MaterialEntity, Media,
NucleotideAnalysis, or NucleotideSequence — all linked via dwcdp:basedOn.

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

### Pattern 10 — Information about a survey that happened during an event
dwc:Survey contains information about biodiversity inventories, checklists and surveys.
These are related to an event using the dwcdp:happenedDuring property.

```sparql
PREFIX dwc: <http://rs.tdwg.org/dwc/terms/>
PREFIX dwcdp: <http://rs.tdwg.org/dwcdp/terms/>
PREFIX eco: <http://rs.tdwg.org/eco/terms/>

SELECT ?sampleSizeUnit ?sampleSizeValue ?samplingEffortProtocol ?samplingEffortUnit
       ?samplingEffortValue ?isAbsenceReported ?areNonTargetTaxaFullyReported
       ?isLeastSpecificTargetCategoryQuantityInclusive ?samplingPerformedBy
WHERE {
  ?surv a dwc:Survey ;
        dwcdp:happenedDuring ?evt .

  OPTIONAL { ?surv dwc:sampleSizeUnit ?sampleSizeUnit }
  OPTIONAL { ?surv dwc:sampleSizeValue ?sampleSizeValue  }

  OPTIONAL { ?surv eco:areNonTargetTaxaFullyReported ?areNonTargetTaxaFullyReported }
  OPTIONAL { ?surv eco:isAbsenceReported ?isAbsenceReported }
  OPTIONAL { ?surv eco:isLeastSpecificTargetCategoryQuantityInclusive ?isLeastSpecificTargetCategoryQuantityInclusive }
  OPTIONAL { ?surv eco:samplingEffortProtocol ?samplingEffortProtocol }
  OPTIONAL { ?surv eco:samplingEffortUnit ?samplingEffortUnit }
  OPTIONAL { ?surv eco:samplingEffortValue ?samplingEffortValue }
  OPTIONAL { ?surv eco:samplingPerformedBy ?samplingPerformedBy }

  # Replace the event ID below with that of the event you want to query
  ?evt a dwc:Event ;
       dwc:eventID "BROKE_WEST_RMT_004_RMT1" .
}
LIMIT 5
```

### Pattern 11 — Information about genomic data
Genomic data information is contained within dwc:NucleotideAnalysis. It links a
dwc:NucleotideSequence to a dwc:Event and a dwc:MaterialEntity via a dwc:MolecularProtocol.

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

### Pattern 12 — Information about the chronometric age surrounding an event
chrono:ChronometricAge contains information about the chronometric age of a dwc:Event.
It is related to its corresponding dwc:Event through the dwcdp:ageFor property.

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
       dwc:scientificName "Odocoileus virginianus" ;
       dwcdp:happenedDuring ?evt .

  ?mat a dwc:MaterialEntity ;
       dwcdp:evidenceFor ?occ .

  ?evt a dwc:Event ;
       dwc:eventDate ?eventDate .

  ?chro a chrono:ChronometricAge ;
        dwcdp:ageFor ?evt .

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
dwc:GeologicalContext contains information about the geological context of a dwc:MaterialEntity.
It is related to its corresponding dwc:MaterialEntity through the dwcdp:contextFor property.

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
dwc:Provenance contains information about an entity's origin. This entity can be of various kinds, such as dwc:Event, dwc:MaterialEntity or dwc:Media.
If considering the provenance of a dwc:Occurrence, then this must be done through the dwc:Event.

```sparql
PREFIX ac: <http://rs.tdwg.org/ac/terms/>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX dwc: <http://rs.tdwg.org/dwc/terms/>
PREFIX dwcdp: <http://rs.tdwg.org/dwcdp/terms/>

SELECT DISTINCT ?prov ?fundingAttribution ?metadataCreatorLiteral ?providerLiteral
       ?creatorLiteral ?references ?datasetID ?projectID ?projectTitle
WHERE {
  ?occ a dwc:Occurrence ;
       dwc:scientificName "Notolepis coatsi" ;
       dwcdp:happenedDuring ?evt .

  ?evt a dwc:Event ;
       dwcdp:hasProvenance ?prov .

  ?prov a dwc:Provenance .

  OPTIONAL { ?prov ac:fundingAttribution ?fundingAttribution }
  OPTIONAL { ?prov ac:metadataCreatorLiteral ?metadataCreatorLiteral }
  OPTIONAL { ?prov ac:providerLiteral ?providerLiteral }
  OPTIONAL { ?prov dc:creator ?creatorLiteral }
  OPTIONAL { ?prov dcterms:references ?references }
  OPTIONAL { ?prov dwc:datasetID ?datasetID }
  OPTIONAL { ?prov dwc:projectID ?projectID }
  OPTIONAL { ?prov dwc:projectTitle ?projectTitle }
}
LIMIT 100
```

---

## dwc:OrganismInteraction — ecological interactions between two occurrences

This class links two dwc:Occurrence nodes in asymmetric roles:
one is the actor (subject), one is the target (object).

### Graph structure

```
dwc:OrganismInteraction
├─ dwc:organismInteractionType (string: "visited flower of", "parasite of", ...)
├─ dwcdp:interactionBy ──► dwc:Occurrence (the acting organism)
└─ dwcdp:interactionWith ──► dwc:Occurrence (the target organism)
```

### Critical rules

1. Always use different variable names for each occurrence — `?subjOcc` and `?objOcc`.
   Reusing the same variable matches only self-interactions, returning 0 results.
2. Always declare `a dwc:Occurrence` for BOTH occurrences explicitly.
3. Filter `?objOcc` by scientificName to find what interacts with a specific species.
4. Filter `?subjOcc` by scientificName to find what a specific species interacts with.

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

### Variation A — All interactions a species participates in (as actor)

```sparql
PREFIX dwc: <http://rs.tdwg.org/dwc/terms/>
PREFIX dwcdp: <http://rs.tdwg.org/dwcdp/terms/>

SELECT ?type ?objectName (COUNT(*) AS ?n)
WHERE {
  ?orgInt a dwc:OrganismInteraction ;
          dwc:organismInteractionType ?type ;
          dwcdp:interactionBy ?subjOcc ;
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
2. NEVER place coordinates on Occurrence — the path is always:
   `?occ dwcdp:happenedDuring ?evt . ?evt dwcdp:spatialLocation ?loc . ?loc dwc:decimalLatitude ?lat`
3. Dates and years are on dwc:Event, not on Occurrence
4. Use OPTIONAL for any property that may be absent on some records
5. Always add LIMIT — 100 for browsing, 500 for filtered queries; omit for aggregations
6. ALL SPARQL keywords UPPERCASE: AS, FILTER, OPTIONAL, ORDER BY, GROUP BY, WHERE
7. NEVER use REGEX() — DuckDB cannot execute it via Ontop. Use instead:
   - Exact match: `FILTER(?x = "Exact Value")`
   - Partial match: `FILTER(CONTAINS(LCASE(?x), "term"))`
   - Starts with: `FILTER(STRSTARTS(LCASE(?x), "prefix"))`
8. COUNT queries do not need LIMIT
9. dwcdp:happenedDuring on Occurrence links to the event it occurred during;
   dwcdp:happenedDuring on Event links to its parent event — different meanings, same property

---

## When a query returns 0 results

Try in this order:
1. Run `SELECT * WHERE { ?s ?p ?o } LIMIT 10` to confirm the endpoint has data at all
2. Remove FILTER clauses one by one — identify which one eliminates all results
3. Check every traversal chain — coordinates must go through Location, dates through Event
4. Wrap non-essential triples in `OPTIONAL { }` and add them back one at a time