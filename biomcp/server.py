from pathlib import Path
import sys
#
from fastmcp import FastMCP
from sparql_client import run_sparql, rows_to_markdown

mcp = FastMCP(
    name="Biodiversity-DwC-DP",
    instructions= "SPARQL access biodiversity data using Darwin Core Data Package (DWC-DP) linked-data ontology."
)

PROMPTS_PATH = Path(__file__).parent / "prompts"

DWC_SCHEMA  = (PROMPTS_PATH / "darwin-core-schema.md").read_text(encoding="utf-8")
QUERY_GUIDE = (PROMPTS_PATH / "query-guidance.md").read_text(encoding="utf-8")

# Build a sparql query docstring template
# NOTE: Later try to integrate .obda file.
#
_SPARQL_TOOL_DOCSTRING = f"""
Execute a SPARQL SELECT query against the SPARQL endpoint using terms from the
Darwin Core OWL (DWC-OWL) ontology.

BEFORE writing any query:
1. Read the ontology reference below — especially the graph structure section.
2. Use one of the provided query patterns as a starting point.

Results are returned as a Markdown table (max 500 rows shown).
If a query returns 0 results, re-read the traversal rules.

---

{DWC_SCHEMA}

---

{QUERY_GUIDE}
"""


@mcp.tool()
async def sparql_query(query: str) -> str:
    # Enable logging of the query.
    #
    print(f"Supplied query: {query}", file=sys.stderr)

    rows, error = await run_sparql(query)

    # NOTE: LLMs tend to overreact if there is an error returned as an exception.
    # Return it as readable text so the LLM can diagnose and retry again.
    #
    if error:
        return (
            f"Query error:\n\n{error}\n\n"
            f"Re-read the ontology reference in your tool description and retry. "
            f"Common causes: missing prefix declarations, or wrong graph traversal method."
        )

    if not rows:
        return (
            "_No results returned._\n\n"
            "If you expected results:\n"
            "1. Check that all traversal chains are complete (Occurrence → Event → Location for coordinates)\n"
            "2. Wrap optional properties in OPTIONAL { }\n"
            "3. Try removing FILTER clauses one at a time to find which one is excluding all results"
        )

    n = len(rows)
    table = rows_to_markdown(rows)

    # Tell the LLM how many rows came back and whether there may be more.
    if n >= 500:
        note = "\n\n_Result capped at 500 rows. Add a more specific FILTER to narrow results._"
    else:
        note = ""

    return table + note


# Replace the placeholder docstring with the full injected version.
#
sparql_query.__doc__ = _SPARQL_TOOL_DOCSTRING

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=9000)