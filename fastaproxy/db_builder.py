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
CREATE_TARP_VIEWS_SQL = (Path(__file__).parent / "create_tarp_views.sql").read_text(encoding="utf-8")


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


def _get_datasets_citations(dataset_ids: list[str], ctx_hash: str) -> None:
    citation_file = DB_DIR / f"{ctx_hash}.txt"

    if not citation_file.exists():
        citation_resp = httpx.post(
            f"{METADATA_API_BASE}/datasets/citations",
            json={"dataset_names": dataset_ids},
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

    # NOTE: Add transitive and transitive_reflexive views
    #
    con.execute(CREATE_TARP_VIEWS_SQL)

    con.close()

    # WARN: Change ownership of the duckdb database
    #
    os.chown(db_path, uid=999, gid=999)

    return db_path