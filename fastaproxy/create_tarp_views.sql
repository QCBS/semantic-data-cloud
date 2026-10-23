-- Define dwcdp:derivedFromTransitive for dwc:MaterialEntity
CREATE VIEW derived_from_transitive_material AS
WITH RECURSIVE closure(child, ancestor) AS (
    SELECT material_entity_pk, derived_from_material_entity_fk
    FROM material
    WHERE derived_from_material_entity_fk IS NOT NULL

    UNION ALL

    SELECT clo.child, mat.derived_from_material_entity_fk
    FROM closure clo
    JOIN material mat
    ON clo.ancestor = mat.material_entity_pk
    WHERE mat.derived_from_material_entity_fk IS NOT NULL
)

SELECT DISTINCT child, ancestor
FROM closure;

-- Define dwcdp:derivedFromTransitiveReflexive for dwc:MaterialEntity
CREATE VIEW derived_from_transitive_reflexive_material AS
WITH RECURSIVE closure(child, ancestor) AS (
    SELECT
        material_entity_pk AS child,
        derived_from_material_entity_fk AS ancestor
    FROM material
    WHERE derived_from_material_entity_fk IS NOT NULL

    UNION

    SELECT
        material_entity_pk AS child,
        material_entity_pk AS ancestor
    FROM material

    UNION

    SELECT
        clo.child,
        mat.is_part_of_material_entity_fk AS ancestor
    FROM closure clo
    JOIN material mat
        ON clo.ancestor = mat.material_entity_pk
    WHERE mat.derived_from_material_entity_fk IS NOT NULL
)

SELECT DISTINCT child, ancestor
FROM closure;

-- Define dwcdp:derivedFromTransitive for dwc:Media
CREATE VIEW derived_from_transitive_media AS
WITH RECURSIVE closure(child, ancestor) AS (
    SELECT media_pk, derived_from_media_fk
    FROM media
    WHERE derived_from_media_fk IS NOT NULL

    UNION ALL

    SELECT clo.child, med.derived_from_media_fk
    FROM closure clo
    JOIN media med
    ON clo.ancestor = med.media_pk
    WHERE med.derived_from_media_fk IS NOT NULL
)

SELECT DISTINCT child, ancestor
FROM closure;

-- Define dwcdp:derivedFromTransitiveReflexive for dwc:Media
CREATE VIEW derived_from_transitive_reflexive_media AS
WITH RECURSIVE closure(child, ancestor) AS (
    SELECT
        media_pk AS child,
        derived_from_media_fk AS ancestor
    FROM media
    WHERE derived_from_media_fk IS NOT NULL

    UNION

    SELECT
        media_pk AS child,
        media_pk AS ancestor
    FROM media

    UNION

    SELECT
        clo.child,
        med.derived_from_media_fk AS ancestor
    FROM closure clo
    JOIN media med
        ON clo.ancestor = med.media_pk
    WHERE med.derived_from_media_fk IS NOT NULL
)

SELECT DISTINCT child, ancestor
FROM closure;

-- Define dwcdp:happenedDuringTransitive for dwc:Event
CREATE VIEW happened_during_transitive_event AS
WITH RECURSIVE closure(child, ancestor) AS (
    SELECT event_pk, parent_event_fk
    FROM event
    WHERE parent_event_fk IS NOT NULL

    UNION ALL

    SELECT clo.child, eve.parent_event_fk
    FROM closure clo
    JOIN event eve
    ON clo.ancestor = eve.event_pk
    WHERE eve.parent_event_fk IS NOT NULL
)

SELECT DISTINCT child, ancestor
FROM closure;

-- Define dwcdp:happenedDuringTransitiveReflexive for dwc:Event
CREATE VIEW happened_during_transitive_reflexive_event AS
WITH RECURSIVE closure(child, ancestor) AS (
    SELECT
        event_pk AS child,
        parent_event_fk AS ancestor
    FROM event
    WHERE parent_event_fk IS NOT NULL

    UNION

    SELECT
        event_pk AS child,
        event_pk AS ancestor
    FROM event

    UNION

    SELECT
        clo.child,
        eve.parent_event_fk AS ancestor
    FROM closure clo
    JOIN event eve
        ON clo.ancestor = eve.event_pk
    WHERE eve.parent_event_fk IS NOT NULL
)

SELECT DISTINCT child, ancestor
FROM closure;

-- Define dwcdp:partOfTransitive for dcterms:BibliographicResource
CREATE VIEW part_of_transitive_bibliographic_resource AS
WITH RECURSIVE closure(child, ancestor) AS (
    SELECT reference_pk, parent_reference_pk
    FROM bibliographic_resource
    WHERE parent_reference_fk IS NOT NULL

    UNION ALL

    SELECT clo.child, bib.parent_reference_fk
    FROM closure clo
    JOIN bibliographic_resource bib
    ON clo.ancestor = bib.reference_pk
    WHERE bib.parent_reference_pk IS NOT NULL
)

SELECT DISTINCT child, ancestor
FROM closure;

-- Define dwcdp:partOfTransitiveReflexive for dcterms:BibliographicResource    
CREATE VIEW part_of_transitive_reflexive_bibliographic_resource AS
WITH RECURSIVE closure(child, ancestor) AS (
    SELECT
        reference_pk AS child,
        parent_reference_fk AS ancestor
    FROM bibliographic_resource
    WHERE parent_reference_fk IS NOT NULL

    UNION

    SELECT
        reference_pk AS child,
        reference_pk AS ancestor
    FROM bibliographic_resource

    UNION

    SELECT
        clo.child,
        bib.parent_reference_fk AS ancestor
    FROM closure clo
    JOIN bibliographic_resource bib
        ON clo.ancestor = bib.reference_pk
    WHERE bib.parent_reference_fk IS NOT NULL
)

SELECT DISTINCT child, ancestor
FROM closure;

-- Define dwcdp:partOfTransitive for dwc:MaterialEntity
CREATE VIEW part_of_transitive_material AS
WITH RECURSIVE closure(child, ancestor) AS (
    SELECT material_entity_pk, is_part_of_material_entity_fk
    FROM material
    WHERE is_part_of_material_entity_fk IS NOT NULL

    UNION ALL

    SELECT clo.child, mat.is_part_of_material_entity_fk
    FROM closure clo
    JOIN material mat
    ON clo.ancestor = mat.material_entity_pk
    WHERE mat.is_part_of_material_entity_fk IS NOT NULL
)

SELECT DISTINCT child, ancestor
FROM closure;

-- Define dwcdp:partOfTransitiveReflexive for dwc:MaterialEntity
CREATE VIEW part_of_transitive_reflexive_material AS
WITH RECURSIVE closure(child, ancestor) AS (
    SELECT
        material_entity_pk AS child,
        is_part_of_material_entity_fk AS ancestor
    FROM material
    WHERE is_part_of_material_entity_pk IS NOT NULL

    UNION

    SELECT
        material_entity_pk AS child,
        material_entity_pk AS ancestor
    FROM material

    UNION

    SELECT
        clo.child,
        mat.is_part_of_material_entity_fk AS ancestor
    FROM closure clo
    JOIN material mat
        ON clo.ancestor = mat.material_entity_pk
    WHERE mat.is_part_of_material_entity_fk IS NOT NULL
)

SELECT DISTINCT child, ancestor
FROM closure;

-- Define dwcdp:partOfTransitive for dwc:Media
CREATE VIEW part_of_transitive_media AS
WITH RECURSIVE closure(child, ancestor) AS (

    SELECT media_pk, is_part_of_media_fk
    FROM media
    WHERE is_part_of_media_fk IS NOT NULL

    UNION ALL

    SELECT clo.child, med.is_part_of_media_fk
    FROM closure clo
    JOIN media med
    ON clo.ancestor = med.media_pk
    WHERE med.is_part_of_media_fk IS NOT NULL
)

SELECT DISTINCT child, ancestor
FROM closure;

-- Define dwcdp:partOfTransitiveReflexive for dwc:Media
CREATE VIEW part_of_transitive_reflexive_media AS
WITH RECURSIVE closure(child, ancestor) AS (
    SELECT
        media_pk AS child,
        is_part_of_media_fk AS ancestor
    FROM media
    WHERE is_part_of_media_fk IS NOT NULL

    UNION

    SELECT
        media_pk AS child,
        media_pk AS ancestor
    FROM media

    UNION

    SELECT
        clo.child,
        med.is_part_of_media_fk AS ancestor
    FROM closure clo
    JOIN media med
        ON clo.ancestor = med.media_pk
    WHERE med.is_part_of_media_fk IS NOT NULL
)

SELECT DISTINCT child, ancestor
FROM closure;

-- Define dwcdp:partOfTransitive for dwc:Occurrence
CREATE VIEW part_of_transitive_occurrence AS
WITH RECURSIVE closure(child, ancestor) AS (
    SELECT occurrence_pk, is_part_of_occurrence_fk
    FROM occurrence
    WHERE is_part_of_occurrence_fk IS NOT NULL

    UNION ALL

    SELECT clo.child, occ.is_part_of_occurrence_fk
    FROM closure clo
    JOIN occurrence occ
    ON clo.ancestor = occ.occurrence_pk
    WHERE occ.is_part_of_occurrence_fk IS NOT NULL
)

SELECT DISTINCT child, ancestor
FROM closure;

-- Define dwcdp:partOfTransitiveReflexive for dwc:Occurrence
CREATE VIEW part_of_transitive_reflexive_occurrence AS
WITH RECURSIVE closure(child, ancestor) AS (
    SELECT
        occurrence_pk AS child,
        is_part_of_occurrence_fk AS ancestor
    FROM occurrence
    WHERE is_part_of_occurrence_fk IS NOT NULL

    UNION

    SELECT
        occurrence_pk AS child,
        occurrence_pk AS ancestor
    FROM occurrence

    UNION

    SELECT
        clo.child,
        occ.is_part_of_occurrence_fk AS ancestor
    FROM closure clo
    JOIN occurrence occ
        ON clo.ancestor = occ.occurrence_pk
    WHERE occ.is_part_of_occurrence_fk IS NOT NULL
)

SELECT DISTINCT child, ancestor
FROM closure;