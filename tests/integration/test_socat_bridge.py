"""Integration tests for MCP SSE transport."""

from __future__ import annotations

import pytest
from mcp import ClientSession
from mcp.client.sse import sse_client


def _server_url(sse_server: dict[str, str | int]) -> str:
    return f"http://{sse_server['host']}:{sse_server['port']}/sse"


@pytest.mark.asyncio
@pytest.mark.sse
async def test_sse_surface_lists_tools_resources_and_prompts(
    sse_server: dict[str, str | int],
) -> None:
    """The SSE transport should expose the same MCP surface as stdio."""
    async with sse_client(_server_url(sse_server)) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            assert len(tools.tools) >= 26
            assert any(tool.name == "connect_eveng_server" for tool in tools.tools)
            assert any(tool.name == "get_lab_topology" for tool in tools.tools)

            resources = await session.list_resources()
            assert len(resources.resources) == 4

            prompts = await session.list_prompts()
            assert len(prompts.prompts) == 6
