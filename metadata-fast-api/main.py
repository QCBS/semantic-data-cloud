from fastapi import FastAPI, Query, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json
from pydantic import BaseModel
from shapely.geometry import shape
from s3io import s3_to_duckdb, duckdb_connect
import os


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

@app.get("/")
def read_root():
    return {"title": "Welcome to the QCBS Semantic Data Cloud API!", 
            "links": {"datasets": f"{os.getenv('API_BASE_URL')}/datasets"},
            "datasets": list_datasets(1, 10)}


@app.get("/datasets")
def get_list_datasets(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
):
    return list_datasets(page, page_size)


@app.get("/dataset/{dataset_id}")
def get_dataset(dataset_id: str):
    row = ddb.execute(
        "SELECT eml_content FROM datasets WHERE name = ?;",
        [dataset_id],
    ).fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Dataset not found")

    eml = row[0]
    return Response(eml, media_type="application/ld+json") if isinstance(eml, str) else eml

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