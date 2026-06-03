from __future__ import annotations
from pathlib import Path
import sys
#
from fastmcp import FastMCP
from sparql_client import run_sparql, rows_to_markdown

PROMPTS_PATH = Path(__file__).parent / "prompts"
DWC_SCHEMA = (PROMPTS_PATH / "darwin-core-schema.md").read_text(encoding="utf-8")
QUERY_GUIDE = (PROMPTS_PATH / "query-guidance.md").read_text(encoding="utf-8")

_TOOL_DESCRIPTION = f"""
Translate a natural language biodiversity question into a SPARQL SELECT query
and execute it against the Darwin Core linked-data endpoint.

Your primary job is writing correct SPARQL. Focus on that.

OPTIONAL geographic, temporal and lincense scoping:
  bbox     — [min_lon, min_lat, max_lon, max_lat] in WGS84.
             Only supply this when the user explicitly asks to restrict results
             to a geographic area AND that restriction is meant to filter which
             datasets are loaded, not just to filter rows in the query.
             Note: a dataset with global coverage will still be included even
             when a bbox is given — the bbox selects datasets whose declared
             coverage intersects the box, not datasets that contain only that area.
  temporal — ["YYYY-MM-DD", "YYYY-MM-DD"].
             Only supply this when the user explicitly asks to restrict by
             data collection period at the dataset level.
  licenses — ["CC-BY-4.0", "CC0-1.0", ...].
             List of SPDX license identifiers used to restrict which datasets
             are loaded. Only supply this when the user explicitly requests
             licensing constraints (for example: "CC-BY data only",
             "public-domain records", or "exclude non-commercial licenses").
             This filters datasets by their declared license and is not a
             SPARQL filter on individual records.

When in doubt, omit bbox, temporal and licenses entirely. Most questions do not need them.
If a query returns 0 results, check the SPARQL before adjusting the bbox.

---

{DWC_SCHEMA}

---

{QUERY_GUIDE}
""".strip()

mcp = FastMCP(
    name="Biodiversity-DwC-DP",
    instructions="""
You have one tool: sparql_query.

Your job is to translate natural language biodiversity questions into correct
SPARQL queries using the Darwin Core ontology, then execute them.

bbox and temporal are optional. Omit them unless the user explicitly asks
to scope the query to a specific geographic region or time period at the
dataset level. Do not fill them in "helpfully" — leave them empty by default.
""".strip()
)


@mcp.tool(description=_TOOL_DESCRIPTION)
async def sparql_query(
    query: str,
    bbox: list[float] | None = None,
    temporal: list[str]   | None = None,
) -> str:
    """Execute a SPARQL query against the biodiversity endpoint."""
    print(f"[sparql_query] bbox={bbox} temporal={temporal}", file=sys.stderr)
    print(f"[sparql_query] query={query}", file=sys.stderr)

    rows, error = await run_sparql(query, bbox, temporal)

    if error:
        return (
            f"API error:\n\n{error}\n\n"
            "Common causes:\n"
            "- Missing PREFIX declarations\n"
            "- Wrong property name or traversal path — re-read the ontology reference\n"
            "- LIMIT missing on a large result set"
        )

    if not rows:
        return (
            "_No results returned._\n\n"
            "1. Check traversal chains — coordinates are on Location, dates on Event\n"
            "2. Wrap optional properties in OPTIONAL { }\n"
            "3. Remove FILTER clauses one at a time to isolate the problem\n"
            "4. Run SELECT * with no filters and a small LIMIT to see what is actually there"
        )

    table = rows_to_markdown(rows[:500])
    note  = (
        "\n\n_Capped at 500 rows. Add a more specific FILTER to narrow results._"
        if len(rows) >= 500 else ""
    )
    return table + note


if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=9000)