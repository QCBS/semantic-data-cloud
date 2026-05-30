from datetime import date
import json
import os
#
from fastapi import FastAPI, Query, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from s3io import s3_to_duckdb, duckdb_connect
from shapely.geometry import shape


ddb = duckdb_connect()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

success = s3_to_duckdb("eml", ".json", ddb)
if success: 
    print("Successfully loaded S3 data into DuckDB.")
else:
    print("Failed to load S3 data into DuckDB.")

@app.get("/")
def read_root():
    return {"title": "Welcome to the QCBS Semantic Data Cloud API!", 
            "links": {"datasets": f"{os.getenv("API_BASE_URL")}/datasets"},
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


@app.get("/datasets/search")
def search_datasets(
    min_lon: float = Query(-180.0, description="West bound of query bbox (in WGS84)"),
    min_lat: float = Query(-90.0, description="South bound of query bbox (in WGS84)"),
    max_lon: float = Query(180.0, description="East bound of query bbox (in WGS84)"),
    max_lat: float = Query(90.0, description="North bound of query bbox (in WGS84)"),
    begin_date: date = Query(date(1900, 1, 1), description="Start of temporal range (YYYY-MM-DD)"),
    end_date: date = Query(date.today(), description="End of temporal range (YYYY-MM-DD)"),
):
    rows = ddb.execute("""
            SELECT name, min_lon, min_lat, max_lon, max_lat
            FROM datasets
            WHERE
            -- Geographical intersection filtering
            max_lon >= ?
            AND min_lon <= ?
            AND max_lat >= ?
            AND min_lat <= ?

            -- Temporal overlap filtering
            AND end_date >= ?
            AND begin_date <= ?

            -- Taxonomic coverage filtering (coming soon)
            ;
    """,
    [min_lon, max_lon, min_lat, max_lat, begin_date, end_date]
    ).fetchall()

    return {"datasets": [row[0] for row in rows]}
