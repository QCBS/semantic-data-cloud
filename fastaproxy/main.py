from contextlib import asynccontextmanager
import hashlib
import os
#
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, Depends
from glide import GlideClient, GlideClientConfiguration, NodeAddress
from httpx import AsyncClient, AsyncHTTPTransport, HTTPError
import orjson

load_dotenv()

TTL_VAL = int(os.getenv("TTL_VAL", 70))
TIMEOUT_VAL = float(os.getenv("TIMEOUT_VAL", 100))

def make_cache_key(prefix: str, query: bytes) -> str:
    digest = hashlib.sha256(query).hexdigest()

    return f"{prefix}:{digest}"



@asynccontextmanager
async def lifespan(app: FastAPI):
    config = GlideClientConfiguration(addresses=[NodeAddress("valkey", 6379)])
    app.state.glide = await GlideClient.create(config)
    transport = AsyncHTTPTransport(retries=0)
    app.state.http = AsyncClient(timeout=TIMEOUT_VAL, transport=transport)

    yield

    await app.state.http.aclose()
    if app.state.glide:
        await app.state.glide.close()


# Dependency function that provides the shared HTTP client
#
def get_http_client(request: Request):
    return request.app.state.http

# Dependency function that provides the shared GLIDE client
#
def get_glide_client(request: Request) -> GlideClient:
    return request.app.state.glide


app = FastAPI(title="sdc-fastapi-proxy", lifespan=lifespan)


@app.post("/sparql")
async def sparql_query(
    request: Request,
    client: AsyncClient = Depends(get_http_client),
    cache: GlideClient = Depends(get_glide_client)
):
    # Read raw body as SPARQL query (application/sparql-query)
    #
    body = await request.body()
    query = body.decode("utf-8")

    cache_key = make_cache_key("sparql", body)

    cached = await cache.get(cache_key)

    if cached:
        print("Found in cache!")
        cached_json = orjson.loads(cached)
        return cached_json

    try:

        response = await client.post(
                "http://ontop-sdc:8080/sparql",
                headers={
                    "Accept": "application/sparql-results+json",
                    "Content-Type": "application/sparql-query"
                },
                content=body
        )

    except HTTPError as e:

        raise HTTPException(status_code=500, detail=f"SPARQL request failed: {str(e)}")

    response_json = response.json()

    # Set in Valkey
    #
    await cache.set(cache_key, orjson.dumps(response_json))
    await cache.expire(cache_key, TTL_VAL)

    return response_json
