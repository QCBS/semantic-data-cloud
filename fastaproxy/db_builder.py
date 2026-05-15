from glob import glob
from pathlib import Path
from urllib.parse import urlparse
#
import duckdb
import httpx


DB_DIR   = Path("/db")
BLANKS_DIR = Path("/blanks")


def _local_schema() -> dict[str, list[str]]:
    tables: dict[str, list[str]] = {}
    for parquet in glob(str(BLANKS_DIR / "*.parquet")):
        name = Path(parquet).stem.replace("-", "_")
        tables[name] = [str(parquet)]
    return tables


def _merge_api_assets(tables: dict[str, list[str]], dataset_json: dict) -> None:
    for asset in dataset_json.get("assets", []):
        href = asset.get("href", "")
        if not href.endswith(".parquet"):
            continue
        name = Path(urlparse(href).path).stem.replace("-", "_")
        if name in tables:
            tables[name].append(href)


def build_db(dataset_url: str) -> Path:
    res = httpx.get(dataset_url, timeout=30)
    res.raise_for_status()
    dataset_json = res.json()

    tables = _local_schema()
    _merge_api_assets(tables, dataset_json)

    DB_DIR.mkdir(parents=True, exist_ok=True)

    dbname = DB_DIR / f"{urlparse(dataset_url).path.split("/")[-1]}.duckdb"

    con = duckdb.connect(dbname)
    for table_name, paths in tables.items():
        rel = con.read_parquet(paths, union_by_name=True)
        rel.create_view(table_name, replace=True)
    con.close()

    return dbname
