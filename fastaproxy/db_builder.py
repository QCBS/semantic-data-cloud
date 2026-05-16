from glob import glob
import hashlib
from pathlib import Path
from urllib.parse import urlparse
#
import duckdb
import httpx


DB_DIR = Path("/db")
BLANKS_DIR = Path("/blanks")
METADATA_API_BASE = "http://metadata-api:8000"


# NOTE: Maybe later increase the number of characters if number of datasets increases.
#
def context_hash(dataset_ids: list[str]) -> str:
    key = "|".join(sorted(dataset_ids))
    return hashlib.sha256(key.encode()).hexdigest()[:16]


def _local_schema() -> dict[str, list[str]]:
    tables = {}
    for parquet in glob(str(BLANKS_DIR / "*.parquet")):
        name = Path(parquet).stem.replace("-", "_")
        tables[name] = [str(parquet)]
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


def build_db(dataset_ids: list[str]) -> Path:
    db_path = DB_DIR / f"{context_hash(dataset_ids)}.duckdb"

    tables = _local_schema()

    for dataset_id in dataset_ids:
        dataset_json = _fetch_dataset_json(dataset_id)
        _merge_assets(tables, dataset_json)

    con = duckdb.connect(str(db_path))

    for table_name, paths in tables.items():
        rel = con.read_parquet(paths, union_by_name=True)
        rel.create_view(table_name, replace=True)

    con.close()
    return db_path