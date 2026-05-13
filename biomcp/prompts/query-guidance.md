# Query Strategy Guide

> This file is injected at runtime into every tool call description.
> Written for a stateless LLM — be concrete, not abstract.

---

## When to call inspect_ontology

Call `inspect_ontology` **before** writing a query whenever:
- You are unsure whether a property exists on a class
- You want to confirm the correct traversal path between two classes
- You see an unfamiliar prefix or term name
- A query returned 0 results and you suspect a wrong property name

| You want to know | Call |
|---|---|
| All classes in the ontology | `action="list_classes"` |
| All properties on dwc:Event | `action="describe_class", target="dwc:Event"` |
| How Occurrence links to Location | `action="find_path", target="dwc:Occurrence -> dcterms:Location"` |
| Which property holds latitude | `action="search_properties", keyword="latitude"` |

The ontology file is the ground truth. It is always more reliable than
the schema hint. When they conflict, trust inspect_ontology.

---

## Step-by-step protocol for every query

1. **Locate the correct query pattern before writing any SPARQL.**
   Use the decision table at the top of the ontology reference above to find
   your pattern. Copy it exactly. Adapt only the filter values.
   Never write SPARQL from scratch.

2. **Identify what the user wants — pick ONE path and follow it:**

   - Question involves **interactions between species**?
     → Go to the OrganismInteraction section. Use the standard pattern. STOP.
   - Question involves **locations or coordinates**?
     → Use Pattern 2 or 3. Coordinates are NEVER on dwc:Occurrence. STOP.
   - Question is a **count or ranking**?
     → Use Pattern 5 with GROUP BY / ORDER BY DESC. STOP.
   - Question involves **dates or time**?
     → Use Pattern 6. Dates are on dwc:Event, not dwc:Occurrence. STOP.
   - **Unsure what properties exist**?
     → Call inspect_ontology FIRST. Then write the query. STOP.
   - Otherwise → Use Pattern 1 for basic occurrence queries.

3. **Build the query by copying the pattern and adapting filter values only:**
   - Change species names, country codes, year ranges as needed
   - Wrap optional fields in `OPTIONAL { }` — not all records have all properties
   - Do not restructure the pattern or invent new traversal chains

4. **Always validate mentally before sending:**
   - Are all used prefixes declared?
   - Is `dwc:decimalLatitude` on `?loc` (not `?occ`)?
   - Is there a LIMIT clause (unless it is a COUNT/aggregation query)?
   - Are all SPARQL keywords UPPERCASE?

---

## Common mistakes to avoid

| Wrong | Right |
|---|---|
| `?occ dwc:decimalLatitude ?lat` | Traverse to Location first via Event |
| `?occ dwc:eventDate ?date` | `?event dwc:eventDate ?date` |
| Missing PREFIX declarations | Always declare all namespaces |
| No LIMIT on large queries | Always add LIMIT |
| `FILTER(?name = "branta")` | `FILTER(LCASE(?name) = LCASE("Branta canadensis"))` for case safety |
| Lowercase keywords: `as`, `order by`, `filter` | Always uppercase: `AS`, `ORDER BY`, `FILTER` |
| `FILTER(REGEX(?name, "Abu", "i"))` | `FILTER(CONTAINS(LCASE(?name), "abudefduf"))` |
| Using same variable for both occurrences in an interaction query | Use `?subjOcc` and `?objOcc` — distinct variable names for each role |
| Forgetting `?objOcc a dwc:Occurrence` | Declare rdf:type explicitly for BOTH occurrence nodes |
| Looking for `dwc:OrganismInteraction` properties on `dwc:Occurrence` | OrganismInteraction is a separate node — start with `?orgInt a dwc:OrganismInteraction` |
| Writing `?x ?predicate ?value` to explore a class | Read the ontology reference above or call inspect_ontology instead |

---

## When a query returns 0 results

Try these in order:
1. Remove FILTER clauses one by one to see where results disappear
2. Check that traversal chain uses `dwcdp:happenedDuring` then `dwcdp:spatialLocation`
3. Wrap all non-essential triples in OPTIONAL and add them back gradually
4. Run a COUNT with no filters to confirm the data class exists

---

## Result size guidance

| Query type | Suggested LIMIT |
|---|---|
| Exploring / browsing | 20–100 |
| Filtered by species | 500 |
| Filtered by species + location | 1000 |
| Aggregations (COUNT, GROUP BY) | No LIMIT needed |
| Full export | 5000 max |