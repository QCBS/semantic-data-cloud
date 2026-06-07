import os
from httpx import AsyncClient, HTTPStatusError, TimeoutException
from dotenv import load_dotenv

load_dotenv()

SPARQL_ENDPOINT = os.getenv("SPARQL_ENDPOINT", "http://fastaproxy-sdc:8000/sparql")
TIMEOUT_VAL = float(os.getenv("TIMEOUT_VAL", 100))

async def run_sparql(
    sparql: str,
    bbox: list[float] | None = None,
    temporal: list[str] | None = None,
    licenses: list[str] | None = None,
) -> tuple[list[dict[str, str]], str]:
    payload: dict = {
        "query": sparql,
    }

    if bbox is not None:
        payload["bbox"] = bbox
    if temporal is not None:
        payload["temporal"] = temporal
    if licenses is not None:
        payload["licenses"] = licenses

    try:
        async with AsyncClient(timeout=TIMEOUT_VAL) as client:
            response = await client.post(
                SPARQL_ENDPOINT,
                json=payload,
            )
            response.raise_for_status()

    except TimeoutException:
        return [], (
            f"The endpoint did not respond within {TIMEOUT_VAL}s. "
            "Try adding a LIMIT clause or narrowing the query."
        )
    except HTTPStatusError as err:
        return [], f"HTTP {err.response.status_code}: {err.response.text}"

    bindings = response.json().get("results", {}).get("bindings", [])
    rows = [
        {var: cell.get("value", "") for var, cell in binding.items()}
        for binding in bindings
    ]
    return rows, ""


def rows_to_markdown(rows: list[dict[str, str]]) -> str:
    if not rows:
        return "_No results found._"

    headers = list(rows[0].keys())
    header_row = "| " + " | ".join(headers) + " |"
    sep = "| " + " | ".join("---" for _ in headers) + " |"
    data_rows = [
        "| " + " | ".join(str(row.get(h, "")) for h in headers) + " |"
        for row in rows
    ]
    return "\n".join([header_row, sep] + data_rows) + f"\n\n_{len(rows)} row(s) returned._"