# MCP Server

## Overview

The application exposes a natural language interface through the [Model Context Protocol](https://modelcontextprotocol.io/docs/getting-started/intro) (MCP). An MCP server runs on port 9000, built with [FastMCP](https://gofastmcp.com/servers/server), and provides a single tool (`sparql_query`) that translates natural language biodiversity questions into SPARQL queries and executes them against the endpoint.

A live instance is available at [https://chat.qcbs.ca/data](https://chat.qcbs.ca/data) with approximately 50 pre-loaded datasets.

---

## Connecting from VS Code

Create a `.vscode/mcp.json` file in your workspace:

```json
{
  "servers": {
    "biomcp": {
      "url": "https://chat.qcbs.ca/mcp",
      "type": "http"
    }
  },
  "inputs": []
}
```

Reload your VS Code window after saving the file. The server will appear in the MCP tools panel and can be invoked from any AI chat interface that supports MCP.

Note that if you are running the application locally, the URL of the biomcp server should be `http://localhost:9000/mcp` instead.

---

## Tool: `sparql_query`

The tool accepts a SPARQL query string and three optional dataset-level filters:

| Parameter | Type | Description |
|---|---|---|
| `sparql` | `string` | A complete SPARQL SELECT query with all PREFIX declarations |
| `bbox` | `[float, float, float, float]` | Geographic bounding box `[min_lon, min_lat, max_lon, max_lat]`. Only supply when the user explicitly requests a geographic scope |
| `temporal` | `[string, string]` | Date range `["YYYY-MM-DD", "YYYY-MM-DD"]`. Only supply when the user explicitly requests a temporal scope |
| `licenses` | `[string, ...]` | SPDX license identifiers. Only supply when the user explicitly requests license-based filtering |

The `bbox`, `temporal`, and `licenses` parameters filter which datasets are loaded before the query runs, they are not SPARQL filters on individual records. For most questions, the tool should omit them entirely and focus on writing correct SPARQL.

In this regard the tool is almost identical to the `/sparql` endpoint definition of the fastaproxy service. The only notable difference is the consideration of `sparql` instead of `query`, as smaller models had difficulty distinguishing between the natural language query from the user and the SPARQL query they had to rewrite.

In addition to a prompt, the LLM also receives Python [typing](https://docs.python.org/3/library/typing.html) and [Pydantic](https://pydantic.dev/docs/validation/latest/get-started/) annotations to facilitate tool understanding.

---

## Example interaction

The primary use case is data retrieval through natural language. A secondary benefit is cross-language accessibility: datasets published in other languages become queryable in English (or any language the underlying model supports).

For example, one dataset covers [occurrences of Andean bears (*Tremarctos ornatus*) in Chingaza National Park, Colombia](https://www.gbif.org/dataset/d35934a1-41fc-4628-a919-44d17867adeb) and is written entirely in Spanish. Asking the question `Can you tell me what was the basis of identifications of Tremarctos ornatus?` will produce a response such as:

```
All identifications of Tremarctos ornatus (Spectacled Bear) were based on dwc:MaterialEntity — physical field evidence, not direct sightings.

The breakdown by material type (translated from Spanish):

| Material type        | Count | Translation                         |
|----------------------|-------|-------------------------------------|
| Heces                | 303   | Feces/scat                          |
| Comedero-Puya        | 214   | Feeding site (Puya plant)           |
| Comedero-Gregia      | 158   | Feeding site (Gregia plant)         |
| Comedero             | 71    | Feeding site (general)              |
| Comedero-Frailejón   | 59    | Feeding site (Frailejón plant)      |
| Marcas de Garras     | 33    | Claw marks                          |
| Sendero              | 22    | Tracks/trail                        |
| Pasadero             | 18    | Passage marks                       |
| Rascadero            | 16    | Scratching site                     |
| Huellas              | 7     | Footprints                          |
| Letrina              | 4     | Latrine site                        |
| Encame               | 3     | Rest/den site                       |
| Pelos                | 1     | Hair                                |
| Esqueleto Adulto     | 1     | Adult skeleton                      |

This is a camera-trap-free, sign-based wildlife survey — identifications were made from physical traces rather than visual encounters.
```

This illustrates how the interface can make datasets from other countries and languages accessible to a broader audience.