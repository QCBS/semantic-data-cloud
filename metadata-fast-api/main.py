from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import json
from pydantic import BaseModel
from shapely.geometry import shape
from s3io import s3_to_duckdb, duckdb_connect


ddb = duckdb_connect()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

success = s3_to_duckdb('eml', '.json', ddb)
if success: 
    print("Successfully loaded S3 data into DuckDB.")
else:
    print("Failed to load S3 data into DuckDB.")

@app.get("/datasets")
def list_datasets(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
):
    offset = (page - 1) * page_size

    total = ddb.execute("SELECT COUNT(*) FROM datasets;").fetchone()[0]
    print(total)
    rows = ddb.execute(
        "SELECT name, eml_content FROM datasets ORDER BY name LIMIT ? OFFSET ?;",
        [page_size, offset],
    ).fetchall()

    datasets = {}
    for dataset_id, eml in rows:
        datasets[dataset_id] = json.loads(eml) if isinstance(eml, str) else eml

    return {
        "page": page,
        "page_size": page_size,
        "total": total,
        "datasets": datasets,
    }


