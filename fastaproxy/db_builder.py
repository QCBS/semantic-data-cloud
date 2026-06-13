import hashlib
import os
from pathlib import Path
from urllib.parse import urlparse
#
import duckdb
import httpx


DB_DIR = Path("/db")
BLANKS_DIR = Path("/blanks")
METADATA_API_BASE = os.getenv("METADATA_API_BASE", "http://metadata-api:8000")


# NOTE: Maybe later increase the number of characters if number of datasets increases.
#
def context_hash(dataset_ids: list[str]) -> str:
    key = "|".join(sorted(dataset_ids))
    return hashlib.sha256(key.encode()).hexdigest()[:16]


def _local_schema() -> dict[str, list[str]]:
    tables = {}
    for parquet_path in BLANKS_DIR.glob("*.parquet"):
        name = parquet_path.stem.replace("-", "_")
        tables[name] = [str(parquet_path)]
    return tables


def _fetch_dataset_json(dataset_id: str) -> dict:
    url = f"{METADATA_API_BASE}/dataset/{dataset_id}"
    resp = httpx.get(url, timeout=30)
    resp.raise_for_status()
    return resp.json()


def _merge_assets(tables: dict[str, list[str]], dataset_json: dict) -> None:
    for asset in dataset_json.get("assets", []):
        href = asset.get("href", "")
        if not href.endswith(".parquet"):
            continue
        name = Path(urlparse(href).path).stem.replace("-", "_")
        if name in tables:
            tables[name].append(href)

def _get_datasets_citations(dataset_ids: list[str], ctx_hash: str) -> str:
    citation_file = DB_DIR / f"{ctx_hash}-citations.txt"

    if not citation_file.exists():
        citation_resp = httpx.get(
            f"{METADATA_API_BASE}/datasets/citations",
            params=[("dataset_names", dataset) for dataset in dataset_ids]
        )

        citation_resp.raise_for_status()

        citations = citation_resp.json().get("citations", [])

        citation_file.write_text("\n".join(citations), encoding="utf-8")


def build_db(dataset_ids: list[str]) -> Path:
    datasets_hash = context_hash(dataset_ids)

    _get_datasets_citations(dataset_ids, datasets_hash)

    db_path = DB_DIR / f"{datasets_hash}.duckdb"

    if db_path.exists():
        return db_path

    tables = _local_schema()

    for dataset_id in dataset_ids:
        dataset_json = _fetch_dataset_json(dataset_id)
        _merge_assets(tables, dataset_json)

    # NOTE: Need to make sure the directory exists now
    #
    DB_DIR.mkdir(parents=True, exist_ok=True)

    con = duckdb.connect(str(db_path))

    for table_name, paths in tables.items():
        rel = con.read_parquet(paths, union_by_name=True)
        rel.create_view(table_name)

    # NOTE: Create views to handle the dwc:SurveyTarget definition
    #
    con.execute("""
    -- Views to expose survey_target data without computed expressions.
    CREATE VIEW v_survey_target AS
    SELECT DISTINCT survey_target_id, survey_id, is_survey_target_fully_reported
    FROM survey_target;

    CREATE VIEW v_survey_target_with_key AS
    SELECT *, LOWER(REPLACE(survey_target_type, ' ', '')) AS definition_key
    FROM survey_target;
    """)

    # NOTE: Create a view to separate dcterms:Location information from the event table
    #
    con.execute("""
    -- dcterms:Location entity separated from by event table.
    CREATE VIEW v_location AS
    SELECT * EXCLUDE (rn)
    FROM (
        SELECT *,
               ROW_NUMBER() OVER (PARTITION BY location_id ORDER BY event_id) AS rn
        FROM event
        WHERE location_id IS NOT NULL
    )
    WHERE rn = 1;
    """)

    # NOTE: Add transitive and transitive_reflexive tables
    #
    con.execute("""
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
    """)

    con.close()

    return db_path
