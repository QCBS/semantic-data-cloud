from contextlib import asynccontextmanager
#
from mcp.client.streamable_http import streamable_http_client
from mcp import ClientSession
import pytest


MCP_URL = "http://biomcp:9000/mcp"


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