from pathlib import Path
#
from fastmcp import FastMCP

PROMPTS_PATH = Path(__file__).parent / "prompts"

DWC_SCHEMA  = (PROMPTS_PATH / "darwin-core-schema.md").read_text(encoding="utf-8")
QUERY_GUIDE = (PROMPTS_PATH / "query-guidance.md").read_text(encoding="utf-8")

mcp = FastMCP(
    name="Biodiversity-DwC-DP",
    instructions= "SPARQL access biodiversity data using Darwin Core Data Package (DWC-DP) linked-data ontology."
)

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=9000)