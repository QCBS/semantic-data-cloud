import os
import sys
#
from httpx import AsyncClient, HTTPStatusError, TimeoutException
#
from enums.maintenance_frequency import MaintenanceFrequency


SPARQL_ENDPOINT = os.getenv("SPARQL_ENDPOINT", "http://fastaproxy-sdc:8000/sparql")
TIMEOUT_VAL = float(os.getenv("TIMEOUT_VAL", 100))


async def run_sparql(
    sparql: str,
    bbox: list[float] | None = None,
    temporal: list[str] | None = None,
    licenses: list[str] | None = None,
    maintenance: list[MaintenanceFrequency] | None = None,
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
    if maintenance is not None:
        payload["maintenance"] = maintenance

    try:
        print(payload, file=sys.stderr)

        async with AsyncClient(timeout=TIMEOUT_VAL) as client:
            response = await client.post(
                url=SPARQL_ENDPOINT,
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
        "| " + " | ".join(str(row.get(head, "")) for head in headers) + " |"
        for row in rows
    ]
    final_row = f"\n\n_{len(rows)} row(s) returned._"

    return "\n".join([header_row, sep] + data_rows) + final_row