import asyncio
from contextlib import asynccontextmanager
#
from mcp.client.streamable_http import streamable_http_client
from mcp import ClientSession
import pytest


MCP_URL = "http://biomcp:9000/mcp"
#
OCCURRENCE_QUERY = "PREFIX dwc: <http://rs.tdwg.org/dwc/terms/> SELECT ?occ WHERE { ?occ a dwc:Occurrence } LIMIT 1"


@asynccontextmanager
async def get_client():
    async with streamable_http_client(MCP_URL) as (
        read_stream,
        write_stream,
        terminate_on_close,
    ):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            yield session


@pytest.mark.asyncio
async def test_initialize():
    async with get_client() as client:
        assert client is not None


@pytest.mark.asyncio
async def test_list_tools():
    async with get_client() as client:
        result = await client.list_tools()
        assert result.tools
        assert len(result.tools) > 0


@pytest.mark.asyncio
async def test_all_tools_have_descriptions():
    async with get_client() as client:
        result = await client.list_tools()

        for tool in result.tools:
            assert tool.name
            assert tool.description
            assert tool.inputSchema


@pytest.mark.asyncio
async def test_sparql_query_available():
    async with get_client() as client:
        result = await client.list_tools()
        assert any(tool.name == "sparql_query" for tool in result.tools)


@pytest.mark.asyncio
async def test_sparql_query_schema_has_required_fields():
    async with get_client() as client:
        result = await client.list_tools()
        tool = next(t for t in result.tools if t.name == "sparql_query")
        schema = tool.inputSchema

        assert "sparql" in schema["properties"]
        assert "sparql" in schema.get("required", [])

        for optional_param in ("bbox", "temporal", "licenses"):
            assert optional_param in schema["properties"]
            assert optional_param not in schema.get("required", [])


@pytest.mark.asyncio
async def test_sparql_query_returns_markdown_table():
    async with get_client() as client:
        result = await client.call_tool(
            "sparql_query",
            {
                "sparql": OCCURRENCE_QUERY,
            },
        )

        assert result.content
        #
        text = result.content[0].text
        #
        assert text
        assert "|" in text
        assert "---" in text
        assert "row(s) returned" in text


@pytest.mark.asyncio
async def test_sparql_query_with_bbox():
    async with get_client() as client:
        result = await client.call_tool(
            "sparql_query",
            {
                "sparql": OCCURRENCE_QUERY,
                "bbox": [-180.0, -90.0, 180.0, 90.0],
            },
        )

        text = result.content[0].text
        #
        assert text
        assert "|" in text
        assert "row(s) returned" in text
 
 
@pytest.mark.asyncio
async def test_sparql_query_with_temporal():
    async with get_client() as client:
        result = await client.call_tool(
            "sparql_query",
            {
                "sparql": OCCURRENCE_QUERY,
                "temporal": ["0001-01-01", "2038-01-19"],
            },
        )

        text = result.content[0].text
        #
        assert text
        assert "|" in text
        assert "row(s) returned" in text


@pytest.mark.asyncio
async def test_sparql_query_with_license_filter():
    async with get_client() as client:
        result = await client.call_tool(
            "sparql_query",
            {
                "sparql": OCCURRENCE_QUERY,
                "licenses": ["CC0-1.0", "CC-BY-4.0"],
            },
        )

        text = result.content[0].text
        #
        assert text
        assert "|" in text
        assert "row(s) returned" in text


@pytest.mark.asyncio
async def test_sparql_query_with_all_optional_params():
    async with get_client() as client:
        result = await client.call_tool(
            "sparql_query",
            {
                "sparql": OCCURRENCE_QUERY,
                "bbox": [-180.0, -90.0, 180.0, 90.0],
                "temporal": ["0001-01-01", "2038-01-19"],
                "licenses": ["CC0-1.0", "CC-BY-4.0"],
            },
        )

        text = result.content[0].text
        #
        assert text
        assert "|" in text
        assert "row(s) returned" in text


@pytest.mark.asyncio
async def test_sparql_missing_prefix_returns_error_guidance():
    async with get_client() as client:
        result = await client.call_tool(
            "sparql_query",
            {
                "sparql": "SELECT ?occ WHERE { ?occ a dwc:Occurrence } LIMIT 1",
            },
        )

        text = result.content[0].text
        #
        assert text
        assert "API error" in text
        assert "Missing PREFIX declarations" in text or "PREFIX" in text


@pytest.mark.asyncio
async def test_sparql_no_results_returns_debugging_guidance():
    async with get_client() as client:
        result = await client.call_tool(
            "sparql_query",
            {
                "sparql": 'PREFIX dwc: <http://rs.tdwg.org/dwc/terms/> SELECT ?occ WHERE { ?occ a dwc:Occurrence ; dwc:scientificName "Homo technologicus" } LIMIT 1',
            },
        )

        text = result.content[0].text
        #
        assert text
        assert "No results returned" in text
        assert "OPTIONAL" in text


@pytest.mark.asyncio
async def test_sparql_empty_string_is_rejected():
    async with get_client() as client:
        result = await client.call_tool(
            "sparql_query",
            {
                "sparql": "",
            },
        )

        text = result.content[0].text
        #
        assert text
        assert "validation error for call[sparql_query]" in text
        assert "String should have at least 1 character" in text


@pytest.mark.asyncio
async def test_sparql_non_numeric_spatial_value_rejected():
    async with get_client() as client:
        result = await client.call_tool(
            "sparql_query",
            {
                "sparql": OCCURRENCE_QUERY,
                "bbox": [-74.0684, 4.5958, -74.0684, "pumpernickel"],
            },
        )

        text = result.content[0].text
        #
        assert text
        assert "validation error for call[sparql_query]" in text
        assert "Input should be a valid number, unable to parse string as a number" in text


@pytest.mark.asyncio
async def test_sparql_too_short_bbox_is_rejected():
    async with get_client() as client:
        result = await client.call_tool(
            "sparql_query",
            {
                "sparql": OCCURRENCE_QUERY,
                "bbox": [-74.0684, 4.5958, -74.0684],
            },
        )

        text = result.content[0].text
        #
        assert text
        assert "validation error for call[sparql_query]" in text
        assert "List should have at least 4 items after validation" in text


@pytest.mark.asyncio
async def test_sparql_too_long_bbox_is_rejected():
    async with get_client() as client:
        result = await client.call_tool(
            "sparql_query",
            {
                "sparql": OCCURRENCE_QUERY,
                "bbox": [-74.0684, 4.5958, -74.0684, 4.5958, -74.0684],
            },
        )

        text = result.content[0].text
        #
        assert text
        assert "validation error for call[sparql_query]" in text
        assert "List should have at most 4 items after validation" in text


@pytest.mark.asyncio
async def test_sparql_too_short_temporal_is_rejected():
    async with get_client() as client:
        result = await client.call_tool(
            "sparql_query",
            {
                "sparql": OCCURRENCE_QUERY,
                "temporal": ["1991-09-17"],
            },
        )

        text = result.content[0].text
        #
        assert text
        assert "validation error for call[sparql_query]" in text
        assert "List should have at least 2 items after validation" in text


@pytest.mark.asyncio
async def test_sparql_too_long_temporal_is_rejected():
    async with get_client() as client:
        result = await client.call_tool(
            "sparql_query",
            {
                "sparql": OCCURRENCE_QUERY,
                "temporal": ["1991-09-17", "2038-01-19", "2038-01-19"],
            },
        )

        text = result.content[0].text
        #
        assert text
        assert "validation error for call[sparql_query]" in text
        assert "List should have at most 2 items after validation" in text


@pytest.mark.asyncio
async def test_sparql_query_concurrent():
    async def make_request():
        async with get_client() as client:
            result = await client.call_tool(
                "sparql_query",
                {
                    "sparql": OCCURRENCE_QUERY,
                },
            )

            text = result.content[0].text
            #
            assert text
            assert "|" in text
            assert "row(s) returned" in text

    await asyncio.gather(*(make_request() for _ in range(20)))