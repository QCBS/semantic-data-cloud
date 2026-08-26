import asyncio
from contextlib import asynccontextmanager
import logging
import os
import time
from typing import Annotated
#
import duckdb
from fastapi import Depends, FastAPI, HTTPException, Query, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
import orjson
from pydantic import BaseModel
#
from s3io import s3_to_duckdb, duckdb_connect, METADATA_DB_PATH
from schemas.datasets import DatasetRequest


# WARN: Use uvicorn's error logger to output times. Probably remove along with timings after.
#
logger = logging.getLogger("uvicorn.error")


# NOTE: Tiny Pydantic model for dataset citations POST requests
#
class CitationRequest(BaseModel):
    dataset_names: list[str]


class SuppressHealthcheck(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return "/health" not in record.getMessage()


METADATA_API_PORT = os.getenv("METADATA_API_PORT")


@asynccontextmanager
async def lifespan(app: FastAPI):
    start = time.perf_counter()

    logging.getLogger("uvicorn.access").addFilter(SuppressHealthcheck())

    ddb = duckdb_connect()

    after_init = time.perf_counter()

    loop = asyncio.get_running_loop()
    success = await loop.run_in_executor(None, lambda: s3_to_duckdb("eml", ".json", ddb))

    after_load = time.perf_counter()

    logger.info(f"DuckDB init: {after_init - start:.3f}s")
    logger.info(f"S3 load: {after_load - after_init:.3f}s")
    logger.info(f"Total startup: {after_load - start:.3f}s")

    ddb.close()

    yield


def get_ddb(request: Request):
    conn = duckdb.connect(str(METADATA_DB_PATH), read_only=True)
    try:
        yield conn
    finally:
        conn.close()


app = FastAPI(title="sdc-metadata-fast-api", lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def read_root(
    ddb = Depends(get_ddb),
):
    loop = asyncio.get_running_loop()

    datasets = await loop.run_in_executor(None, lambda: _list_datasets(1, 10, ddb))

    return {
        "title": "Welcome to the QCBS Semantic Data Cloud API!",
        "description": "A metadata catalog of biodiversity and ecological datasets described using Ecological Metadata Language (EML), providing standardized, machine-readable metadata and access to associated data assets for discovery, integration, and analysis.",
        "links": {
            "datasets": f"http://localhost:{METADATA_API_PORT}/datasets",
        },
        "datasets": datasets,
    }


@app.get("/health")
async def get_health():
    return {"status": "ok"}


@app.get("/datasets")
async def get_list_datasets(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    ddb = Depends(get_ddb),
):
    loop = asyncio.get_running_loop()

    return await loop.run_in_executor(None, lambda: _list_datasets(page, page_size, ddb))


@app.get("/dataset/{dataset_id}")
async def get_dataset(
    dataset_id: str,
    ddb = Depends(get_ddb),
):
    loop = asyncio.get_running_loop()

    def _query():
        return ddb.execute(
            "SELECT eml_content FROM datasets WHERE name = ?;",
            [dataset_id],
        ).fetchone()

    row = await loop.run_in_executor(None, _query)

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found",
        )

    return Response(row[0], media_type="application/ld+json")


@app.get("/datasets/search")
async def search_datasets(
    request: Annotated[DatasetRequest, Query()],
    ddb=Depends(get_ddb),
):
    loop = asyncio.get_running_loop()

    def _query():
        params = [request.min_lon, request.max_lon, request.min_lat, request.max_lat, request.begin_date, request.end_date]

        conditions = [
            "max_lon >= ?",
            "min_lon <= ?",
            "max_lat >= ?",
            "min_lat <= ?",
            "end_date >= ?",
            "begin_date <= ?",
        ]

        if request.licenses:
            params.append(request.licenses)
            conditions.append("license_id = ANY(?)")

        if request.maintenance:
            params.append(request.maintenance)
            conditions.append("maintenance_update_frequency = ANY(?)")

        query = "SELECT name FROM datasets WHERE " + " AND ".join(conditions) + ";"

        return ddb.execute(query, params).fetchall()

    rows = await loop.run_in_executor(None, _query)

    return {"datasets": [row[0] for row in rows]}


@app.post("/datasets/citations")
async def get_citations(
    body: CitationRequest,
    ddb = Depends(get_ddb),
):
    if not body.dataset_names:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="dataset_names cannot be empty",
        )

    loop = asyncio.get_running_loop()

    def _query():
        return ddb.execute(
            "SELECT dataset_citation FROM datasets WHERE name = ANY(?);",
            (body.dataset_names,)
        ).fetchall()

    rows = await loop.run_in_executor(None, _query)

    return {"citations": [row[0] for row in rows]}


# NOTE: list_datasets() now renamed _list_datasets() for consistency with fastaproxy code
#
def _list_datasets(
        page: int,
        page_size: int,
        ddb,
) -> dict:
    offset = (page - 1) * page_size

    total = ddb.execute("SELECT COUNT(*) FROM datasets;").fetchone()[0]

    rows = ddb.execute(
        "SELECT name, eml_content FROM datasets ORDER BY name LIMIT ? OFFSET ?;",
        [page_size, offset],
    ).fetchall()

    datasets = {}
    for dataset_id, eml in rows:
        datasets[dataset_id] = orjson.loads(eml) if isinstance(eml, str) else eml

    return {
        "page": page,
        "page_size": page_size,
        "total": total,
        "datasets": datasets,
    }