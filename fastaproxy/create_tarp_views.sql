-- Define dwcdp:derivedFromTransitive for dwc:MaterialEntity
CREATE VIEW derived_from_transitive_material AS
WITH RECURSIVE closure(child, ancestor) AS (
    SELECT material_entity_id, derived_from_material_entity_id
    FROM material
    WHERE derived_from_material_entity_id IS NOT NULL

    UNION ALL

    SELECT clo.child, mat.derived_from_material_entity_id
    FROM closure clo
    JOIN material mat
    ON clo.ancestor = mat.material_entity_id
    WHERE mat.derived_from_material_entity_id IS NOT NULL
)

SELECT DISTINCT child, ancestor
FROM closure;

-- Define dwcdp:derivedFromTransitiveReflexive for dwc:MaterialEntity
CREATE VIEW derived_from_transitive_reflexive_material AS
WITH RECURSIVE closure(child, ancestor) AS (
    SELECT
        material_entity_id AS child,
        derived_from_material_entity_id AS ancestor
    FROM material
    WHERE derived_from_material_entity_id IS NOT NULL

    UNION

    SELECT
        material_entity_id AS child,
        material_entity_id AS ancestor
    FROM material

    UNION

    SELECT
        clo.child,
        mat.is_part_of_material_entity_id AS ancestor
    FROM closure clo
    JOIN material mat
        ON clo.ancestor = mat.material_entity_id
    WHERE mat.derived_from_material_entity_id IS NOT NULL
)

SELECT DISTINCT child, ancestor
FROM closure;

-- Define dwcdp:derivedFromTransitive for dwc:Media
CREATE VIEW derived_from_transitive_media AS
WITH RECURSIVE closure(child, ancestor) AS (
    SELECT media_id, derived_from_media_id
    FROM media
    WHERE derived_from_media_id IS NOT NULL

    UNION ALL

    SELECT clo.child, med.derived_from_media_id
    FROM closure clo
    JOIN media med
    ON clo.ancestor = med.media_id
    WHERE med.derived_from_media_id IS NOT NULL
)

SELECT DISTINCT child, ancestor
FROM closure;

-- Define dwcdp:derivedFromTransitiveReflexive for dwc:Media
CREATE VIEW derived_from_transitive_reflexive_media AS
WITH RECURSIVE closure(child, ancestor) AS (
    SELECT
        media_id AS child,
        derived_from_media_id AS ancestor
    FROM media
    WHERE derived_from_media_id IS NOT NULL

    UNION

    SELECT
        media_id AS child,
        media_id AS ancestor
    FROM media

    UNION

    SELECT
        clo.child,
        med.derived_from_media_id AS ancestor
    FROM closure clo
    JOIN media med
        ON clo.ancestor = med.media_id
    WHERE med.derived_from_media_id IS NOT NULL
)

SELECT DISTINCT child, ancestor
FROM closure;

-- Define dwcdp:happenedDuringTransitive for dwc:Event
CREATE VIEW happened_during_transitive_event AS
WITH RECURSIVE closure(child, ancestor, depth) AS (
    SELECT event_id, parent_event_id, 1
    FROM event
    WHERE parent_event_id IS NOT NULL

    UNION ALL

    SELECT clo.child, eve.parent_event_id, clo.depth + 1
    FROM closure clo
    JOIN event eve
    ON clo.ancestor = eve.event_id
    WHERE eve.parent_event_id IS NOT NULL
)

SELECT DISTINCT child, ancestor, depth
FROM closure;

-- Define dwcdp:happenedDuringTransitiveReflexive for dwc:Event
CREATE VIEW happened_during_transitive_reflexive_event AS
WITH RECURSIVE closure(child, ancestor) AS (
    SELECT
        event_id AS child,
        parent_event_id AS ancestor
    FROM event
    WHERE parent_event_id IS NOT NULL

    UNION

    SELECT
        event_id AS child,
        event_id AS ancestor
    FROM event

    UNION

    SELECT
        clo.child,
        eve.parent_event_id AS ancestor
    FROM closure clo
    JOIN event eve
        ON clo.ancestor = eve.event_id
    WHERE eve.parent_event_id IS NOT NULL
)

SELECT DISTINCT child, ancestor
FROM closure;

-- Define dwcdp:partOfTransitive for dcterms:BibliographicResource
CREATE VIEW part_of_transitive_bibliographic_resource AS
WITH RECURSIVE closure(child, ancestor) AS (
    SELECT reference_id, parent_reference_id
    FROM bibliographic_resource
    WHERE parent_reference_id IS NOT NULL

    UNION ALL

    SELECT clo.child, bib.parent_reference_id
    FROM closure clo
    JOIN bibliographic_resource bib
    ON clo.ancestor = bib.reference_id
    WHERE bib.parent_reference_id IS NOT NULL
)

SELECT DISTINCT child, ancestor
FROM closure;

-- Define dwcdp:partOfTransitiveReflexive for dcterms:BibliographicResource    
CREATE VIEW part_of_transitive_reflexive_bibliographic_resource AS
WITH RECURSIVE closure(child, ancestor) AS (
    SELECT
        reference_id AS child,
        parent_reference_id AS ancestor
    FROM bibliographic_resource
    WHERE parent_reference_id IS NOT NULL

    UNION

    SELECT
        reference_id AS child,
        reference_id AS ancestor
    FROM bibliographic_resource

    UNION

    SELECT
        clo.child,
        bib.parent_reference_id AS ancestor
    FROM closure clo
    JOIN bibliographic_resource bib
        ON clo.ancestor = bib.reference_id
    WHERE bib.parent_reference_id IS NOT NULL
)

SELECT DISTINCT child, ancestor
FROM closure;

-- Define dwcdp:partOfTransitive for dwc:MaterialEntity
CREATE VIEW part_of_transitive_material AS
WITH RECURSIVE closure(child, ancestor) AS (
    SELECT material_entity_id, is_part_of_material_entity_id
    FROM material
    WHERE is_part_of_material_entity_id IS NOT NULL

    UNION ALL

    SELECT clo.child, mat.is_part_of_material_entity_id
    FROM closure clo
    JOIN material mat
    ON clo.ancestor = mat.material_entity_id
    WHERE mat.is_part_of_material_entity_id IS NOT NULL
)

SELECT DISTINCT child, ancestor
FROM closure;

-- Define dwcdp:partOfTransitiveReflexive for dwc:MaterialEntity
CREATE VIEW part_of_transitive_reflexive_material AS
WITH RECURSIVE closure(child, ancestor) AS (
    SELECT
        material_entity_id AS child,
        is_part_of_material_entity_id AS ancestor
    FROM material
    WHERE is_part_of_material_entity_id IS NOT NULL

    UNION

    SELECT
        material_entity_id AS child,
        material_entity_id AS ancestor
    FROM material

    UNION

    SELECT
        clo.child,
        mat.is_part_of_material_entity_id AS ancestor
    FROM closure clo
    JOIN material mat
        ON clo.ancestor = mat.material_entity_id
    WHERE mat.is_part_of_material_entity_id IS NOT NULL
)

SELECT DISTINCT child, ancestor
FROM closure;

-- Define dwcdp:partOfTransitive for dwc:Media
CREATE VIEW part_of_transitive_media AS
WITH RECURSIVE closure(child, ancestor) AS (

    SELECT media_id, is_part_of_media_id
    FROM media
    WHERE is_part_of_media_id IS NOT NULL

    UNION ALL

    SELECT clo.child, med.is_part_of_media_id
    FROM closure clo
    JOIN media med
    ON clo.ancestor = med.media_id
    WHERE med.is_part_of_media_id IS NOT NULL
)

SELECT DISTINCT child, ancestor
FROM closure;

-- Define dwcdp:partOfTransitiveReflexive for dwc:Media
CREATE VIEW part_of_transitive_reflexive_media AS
WITH RECURSIVE closure(child, ancestor) AS (
    SELECT
        media_id AS child,
        is_part_of_media_id AS ancestor
    FROM media
    WHERE is_part_of_media_id IS NOT NULL

    UNION

    SELECT
        media_id AS child,
        media_id AS ancestor
    FROM media

    UNION

    SELECT
        clo.child,
        med.is_part_of_media_id AS ancestor
    FROM closure clo
    JOIN media med
        ON clo.ancestor = med.media_id
    WHERE med.is_part_of_media_id IS NOT NULL
)

SELECT DISTINCT child, ancestor
FROM closure;

-- Define dwcdp:partOfTransitive for dwc:Occurrence
CREATE VIEW part_of_transitive_occurrence AS
WITH RECURSIVE closure(child, ancestor) AS (
    SELECT occurrence_id, is_part_of_occurrence_id
    FROM occurrence
    WHERE is_part_of_occurrence_id IS NOT NULL

    UNION ALL

    SELECT clo.child, occ.is_part_of_occurrence_id
    FROM closure clo
    JOIN occurrence occ
    ON clo.ancestor = occ.occurrence_id
    WHERE occ.is_part_of_occurrence_id IS NOT NULL
)

SELECT DISTINCT child, ancestor
FROM closure;

-- Define dwcdp:partOfTransitiveReflexive for dwc:Occurrence
CREATE VIEW part_of_transitive_reflexive_occurrence AS
WITH RECURSIVE closure(child, ancestor) AS (
    SELECT
        occurrence_id AS child,
        is_part_of_occurrence_id AS ancestor
    FROM occurrence
    WHERE is_part_of_occurrence_id IS NOT NULL

    UNION

    SELECT
        occurrence_id AS child,
        occurrence_id AS ancestor
    FROM occurrence

    UNION

    SELECT
        clo.child,
        occ.is_part_of_occurrence_id AS ancestor
    FROM closure clo
    JOIN occurrence occ
        ON clo.ancestor = occ.occurrence_id
    WHERE occ.is_part_of_occurrence_id IS NOT NULL
)

SELECT DISTINCT child, ancestor
FROM closure;