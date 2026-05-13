from fastmcp import FastMCP

mcp = FastMCP(
    name="Biodiversity-DwC-DP",
    instructions= "SPARQL access biodiversity data using Darwin Core Data Package (DWC-DP) linked-data ontology. Call describe_schema first, then sparql_query."
)

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=9000)