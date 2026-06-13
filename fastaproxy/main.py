from asyncio import Lock, to_thread
from contextlib import asynccontextmanager
import hashlib
import os
#
from fastapi import FastAPI, HTTPException, Request, status, Depends
from glide import GlideClient, GlideClientConfiguration, NodeAddress
from httpx import AsyncClient, AsyncHTTPTransport, HTTPError
import orjson
#
from container_manager import ContainerRegistry
from db_builder import build_db, context_hash
from schemas.sparql import QueryRequest


TTL_VAL = int(os.getenv("TTL_VAL", 70))
TIMEOUT_VAL = float(os.getenv("TIMEOUT_VAL", 100))
METADATA_API_BASE = os.getenv("METADATA_API_BASE", "http://metadata-api:8000")


def make_cache_key(ctx_hash: str, sparql: bytes) -> str:
    digest = hashlib.sha256(sparql).hexdigest()
    return f"sparql:{ctx_hash}:{digest}"


@asynccontextmanager
async def lifespan(app: FastAPI):
    config = GlideClientConfiguration(addresses=[NodeAddress("valkey", 6379)])
    app.state.glide = await GlideClient.create(config)
    transport = AsyncHTTPTransport(retries=0)

    app.state.http = AsyncClient(timeout=TIMEOUT_VAL, transport=transport)

    app.state.registry = ContainerRegistry()

    app.state.lock = Lock()

    yield

    await app.state.http.aclose()
    if app.state.glide:
        await app.state.glide.close()


# NOTE: Dependency functions
#
def get_http_client(request: Request) -> AsyncClient:
    return request.app.state.http

def get_glide_client(request: Request) -> GlideClient:
    return request.app.state.glide

def get_registry(request: Request) -> ContainerRegistry:
    return request.app.state.registry

def get_lock(request: Request) -> Lock:
    return request.app.state.lock


app = FastAPI(title="sdc-fastapi-proxy", lifespan=lifespan)


@app.post("/sparql")
async def sparql_query(
    body: QueryRequest,
    client: AsyncClient = Depends(get_http_client),
    cache: GlideClient = Depends(get_glide_client),
    registry: ContainerRegistry = Depends(get_registry),
    lock: Lock = Depends(get_lock),
):
    print(body.bbox)
    print(body.temporal)
    print(body.licenses)

    min_lon, min_lat, max_lon, max_lat = body.bbox
    begin_date, end_date = body.temporal
    sparql_bytes = body.query.encode("utf-8")

    search_params = [
        ("min_lon", min_lon),
        ("min_lat", min_lat),
        ("max_lon", max_lon),
        ("max_lat", max_lat),
        ("begin_date", begin_date),
        ("end_date", end_date),
    ]

    if body.licenses:
        search_params.extend(("licenses", license) for license in body.licenses)

    search_resp = await client.get(
        f"{METADATA_API_BASE}/datasets/search",
        params=search_params,
    )

    dataset_ids: list[str] = search_resp.json().get("datasets", [])

    if not dataset_ids:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No datasets found for the given spatial and temporal filters.")

    ctx_hash = context_hash(dataset_ids)

    cache_key = make_cache_key(ctx_hash, sparql_bytes)

    cached = await cache.get(cache_key)
    if cached:
        return orjson.loads(cached)

    # NOTE: Changes to not block the event loop
    #
    async with lock:
        db_path = await to_thread(build_db, dataset_ids)
        info = await to_thread(registry.get_or_create, dataset_ids)

    try:
        response = await client.post(
            f"{info.ontop_url}/sparql",
            headers={
                "Accept": "application/sparql-results+json",
                "Content-Type": "application/sparql-query",
            },
            content=sparql_bytes,
        )
    except HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"SPARQL request failed: {e}",
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail={
                "error": response.text
            }
        )

    result = response.json()

    await cache.set(cache_key, orjson.dumps(result))
    await cache.expire(cache_key, TTL_VAL)

    return result