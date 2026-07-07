import asyncio
from contextlib import asynccontextmanager
from datetime import date
import json
import logging
import os
from threading import Lock
import time
#
from fastapi import Depends, FastAPI, HTTPException, Query, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
#
from s3io import s3_to_duckdb, duckdb_connect


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
    lock = Lock()

    app.state.ddb = ddb
    app.state.lock = lock

    after_init = time.perf_counter()

    loop = asyncio.get_running_loop()
    success = await loop.run_in_executor(None, lambda: s3_to_duckdb("eml", ".json", ddb))

    after_load = time.perf_counter()

    logger.info(f"DuckDB init: {after_init - start:.3f}s")
    logger.info(f"S3 load: {after_load - after_init:.3f}s")
    logger.info(f"Total startup: {after_load - start:.3f}s")

    yield

    ddb.close()


# NOTE: Dependency functions
#
def get_lock(request: Request) -> Lock:
    return request.app.state.lock

def get_ddb(request: Request):
    return request.app.state.ddb


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
    lock: Lock = Depends(get_lock),
):
    loop = asyncio.get_event_loop()
    datasets = await loop.run_in_executor(None, lambda: _list_datasets(1, 10, ddb, lock))
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
    lock: Lock = Depends(get_lock),
):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: _list_datasets(page, page_size, ddb, lock))


@app.get("/dataset/{dataset_id}")
async def get_dataset(
    dataset_id: str,
    ddb = Depends(get_ddb),
    lock: Lock = Depends(get_lock),
):
    loop = asyncio.get_event_loop()

    def _query():
        with lock:
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
    min_lon: float = Query(
        default=-180.0,
        description="West bound of query bbox (in WGS84)",
        ge=-180.0,
        le=180.0,
    ),
    min_lat: float = Query(
        default=-90.0,
        description="South bound of query bbox (in WGS84)",
        ge=-90.0,
        le=90.0,
    ),
    max_lon: float = Query(
        default=180.0,
        description="East bound of query bbox (in WGS84)",
        ge=-180.0,
        le=180.0,
    ),
    max_lat: float = Query(
        default=90.0,
        description="North bound of query bbox (in WGS84)",
        ge=-90.0,
        le=90.0,
    ),
    begin_date: date = Query(
        default=date(1, 1, 1),
        description="Start of temporal range (YYYY-MM-DD)",
    ),
    end_date: date = Query(
        default=date(2038, 1, 19),
        description="End of temporal range (YYYY-MM-DD)",
    ),
    licenses: list[str] | None = Query(
        default=None,
        description="SPDX IDs of the licenses requested",
    ),
    ddb = Depends(get_ddb),
    lock: Lock = Depends(get_lock),
):
    params = [min_lon, max_lon, min_lat, max_lat, begin_date, end_date]
    loop = asyncio.get_event_loop()

    def _query():
        with lock:
            if licenses:
                return ddb.execute("""
                    SELECT name
                    FROM datasets
                    WHERE
                        max_lon >= ?
                        AND min_lon <= ?
                        AND max_lat >= ?
                        AND min_lat <= ?
                        AND end_date >= ?
                        AND begin_date <= ?
                        AND license_id = ANY(?)
                    ;
                """, params + [licenses]).fetchall()
            else:
                return ddb.execute("""
                    SELECT name
                    FROM datasets
                    WHERE
                        max_lon >= ?
                        AND min_lon <= ?
                        AND max_lat >= ?
                        AND min_lat <= ?
                        AND end_date >= ?
                        AND begin_date <= ?
                    ;
                """, params).fetchall()

    rows = await loop.run_in_executor(None, _query)
    return {"datasets": [row[0] for row in rows]}


@app.post("/datasets/citations")
async def get_citations(
    body: CitationRequest,
    ddb = Depends(get_ddb),
    lock: Lock = Depends(get_lock),
):
    if not body.dataset_names:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="dataset_names cannot be empty",
        )

    loop = asyncio.get_event_loop()

    def _query():
        with lock:
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
        lock: Lock,
) -> dict:
    offset = (page - 1) * page_size

    with lock:
        total = ddb.execute("SELECT COUNT(*) FROM datasets;").fetchone()[0]
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