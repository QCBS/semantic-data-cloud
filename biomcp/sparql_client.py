import os
#
from httpx import AsyncClient, HTTPStatusError, TimeoutException
from dotenv import load_dotenv

load_dotenv()

SPARQL_ENDPOINT = "http://fastaproxy-sdc:8000/sparql"
TIMEOUT_VAL = float(os.getenv("TIMEOUT_VAL", 100))

async def run_sparql(query: str) -> tuple[list[dict[str, str]], str]:
    try:
        async with AsyncClient(timeout=TIMEOUT_VAL) as client:
            response = await client.post(
                SPARQL_ENDPOINT,
                headers={
                    "Accept": "application/sparql-results+json",
                    "Content-Type": "application/sparql-query",
                },
                content=query,
            )

        body = response.json()

    except TimeoutException:
        return [], (
            f"Ontop did not respond within {TIMEOUT_VAL}s."
            "The query may be too broad — try adding a LIMIT clause."
        )
    except HTTPStatusError as err:
        return [], f"HTTP error {err.response.status_code}: {err.response.text}"

    bindings = body.get("results", {}).get("bindings", [])
    rows = [
        {var: cell.get("value", "") for var, cell in binding.items()}
        for binding in bindings
    ]

    return rows, ""


def rows_to_markdown(rows: list[dict[str, str]]) -> str:
    if not rows:
        return "_No results found._"

    headers = list(rows[0].keys())
    sep = "| " + " | ".join("---" for _ in headers) + " |"
    header_row = "| " + " | ".join(headers) + " |"

    data_rows = [
        "| " + " | ".join(str(row.get(h, "")) for h in headers) + " |"
        for row in rows
    ]

    total_line = f"\n_{len(rows)} row(s) returned._"
    return "\n".join([header_row, sep] + data_rows) + total_line