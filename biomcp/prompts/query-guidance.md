# Query Strategy Guide

> Injected into the tool description at runtime.

---

## Step-by-step protocol for every query

### Step 1 — Identify what the user wants and choose a pattern

- Count or ranking → Pattern 5 with GROUP BY / ORDER BY DESC
- Locations or coordinates → Pattern 2 or 3 (coordinates live on Location, never on Occurrence)
- Dates or time range → Pattern 6 (dates live on Event, never on Occurrence)
- Species interactions → OrganismInteraction section
- Basic occurrence data → Pattern 1

Copy the pattern exactly. Adapt filter values only. Never write SPARQL from scratch.

### Step 2 — Build the query

- Declare all PREFIX namespaces at the top of every query
- Wrap optional fields in `OPTIONAL { }` — not all records have all properties
- Add a LIMIT clause on browsing queries (not needed for COUNT/aggregation)
- Do not add geographic or country filters in SPARQL unless the user is asking
  to filter individual rows by location — that is different from dataset-level scoping

### Step 3 — Validate before sending

- Are all used prefixes declared?
- Is `dwc:decimalLatitude` on `?loc`, not `?occ`?
- Is `dwc:eventDate` on `?event`, not `?occ`?
- Are all SPARQL keywords UPPERCASE?

---

## Common mistakes

| Wrong | Right |
|---|---|
| `?occ dwc:decimalLatitude ?lat` | Traverse to Location via Event first |
| `?occ dwc:eventDate ?date` | `?event dwc:eventDate ?date` |
| Missing PREFIX declarations | Always declare all namespaces used |
| No LIMIT on browsing queries | Always add LIMIT |
| `FILTER(?name = "branta")` | `FILTER(LCASE(?name) = LCASE("Branta canadensis"))` |
| `FILTER(REGEX(?name, "Abu", "i"))` | `FILTER(CONTAINS(LCASE(?name), "abudefduf"))` |
| Using same variable for both roles in an interaction | Use `?subjOcc` and `?objOcc` |
| Lowercase keywords: `as`, `order by` | Always UPPERCASE: `AS`, `ORDER BY` |

---

## When a query returns 0 results

Try in this order:
1. Run `SELECT * WHERE { ?s ?p ?o } LIMIT 20` to confirm the endpoint has data
2. Remove FILTER clauses one by one to find which excludes all results
3. Check traversal chains — is the correct intermediate node being used?
4. Wrap non-essential triples in OPTIONAL and add them back one at a time

---

## Geographic and temporal scoping (optional)

The endpoint can restrict which datasets are loaded by supplying a bounding box
and/or temporal range alongside the query. Only do this when the user explicitly
asks to scope at the dataset level.

Important: a dataset with global coverage is included whenever its declared
extent overlaps the requested box — it is not excluded because it covers more
than the requested area. Filtering individual rows by coordinates or country
should be done with SPARQL FILTER, not with the bbox parameter.

| Parameter | Format | When to use |
|-----------|--------|-------------|
| bbox | [min_lon, min_lat, max_lon, max_lat] | User asks to limit to a specific region |
| temporal | ["YYYY-MM-DD", "YYYY-MM-DD"] | User asks to limit to a collection period |

---

## Result size guidance

| Query type | Suggested LIMIT |
|---|---|
| Exploring / browsing | 20–100 |
| Filtered by species | 500 |
| Filtered by species + location | 1000 |
| Aggregations (COUNT, GROUP BY) | No LIMIT needed |