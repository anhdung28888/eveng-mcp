"""Integration tests for MCP stdio workflows."""

from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import timedelta
from pathlib import Path
from uuid import uuid4

import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


EXPECTED_TOOLS = {
    "connect_eveng_server",
    "disconnect_eveng_server",
    "test_connection",
    "get_server_info",
    "list_labs",
    "create_lab",
    "get_lab_details",
    "delete_lab",
}

EXPECTED_RESOURCES = {
    "eveng://server/status",
    "eveng://help/api-reference",
    "eveng://help/topology-examples",
    "eveng://help/troubleshooting",
}

EXPECTED_PROMPTS = {
    "create_simple_lab",
    "create_enterprise_topology",
    "diagnose_connectivity",
    "configure_lab_automation",
    "analyze_lab_performance",
    "debug_node_issues",
}

PROJECT_ROOT = Path(__file__).resolve().parents[2]


@asynccontextmanager
async def stdio_session(python_executable: str, server_env: dict[str, str]):
    """Create a stdio MCP session against the local project."""
    params = StdioServerParameters(
        command=python_executable,
        args=["-m", "eveng_mcp_server.cli", "run", "--transport", "stdio"],
        env=server_env,
        cwd=PROJECT_ROOT,
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            yield session


def _text_content(result) -> str:
    """Extract the first text payload from a tool result."""
    if not result.content:
        return ""
    return result.content[0].text


@pytest.mark.asyncio
@pytest.mark.stdio
async def test_stdio_surface_lists_tools_resources_and_prompts(
    python_executable: str, server_env: dict[str, str]
) -> None:
    """The stdio server should expose the expected MCP surface."""
    async with stdio_session(python_executable, server_env) as session:
        tools = await session.list_tools()
        tool_names = {tool.name for tool in tools.tools}
        assert EXPECTED_TOOLS.issubset(tool_names)
        assert len(tool_names) >= 26

        resources = await session.list_resources()
        resource_uris = {str(resource.uri) for resource in resources.resources}
        assert resource_uris == EXPECTED_RESOURCES

        prompts = await session.list_prompts()
        prompt_names = {prompt.name for prompt in prompts.prompts}
        assert prompt_names == EXPECTED_PROMPTS


@pytest.mark.asyncio
@pytest.mark.live_eveng
@pytest.mark.stdio
async def test_stdio_live_eveng_lab_workflow(
    python_executable: str,
    server_env: dict[str, str],
    require_live_eveng: dict[str, str | int],
) -> None:
    """The stdio server should manage a real lab against EVE-NG."""
    lab_name = f"codex-int-{uuid4().hex[:8]}"
    lab_path = f"/{lab_name}.unl"

    async with stdio_session(python_executable, server_env) as session:
        connect_result = await session.call_tool(
            "connect_eveng_server",
            {
                "arguments": {
                    "host": require_live_eveng["host"],
                    "username": require_live_eveng["username"],
                    "password": require_live_eveng["password"],
                    "port": require_live_eveng["port"],
                    "protocol": require_live_eveng["protocol"],
                }
            },
            read_timeout_seconds=timedelta(seconds=45),
        )
        assert not connect_result.isError
        assert "Successfully connected" in _text_content(connect_result)

        test_result = await session.call_tool("test_connection", {"arguments": {}})
        assert not test_result.isError
        assert "Connection test successful" in _text_content(test_result)

        create_result = await session.call_tool(
            "create_lab",
            {
                "name": lab_name,
                "path": "/",
                "description": "Integration test lab",
                "author": "Codex",
                "version": "1",
            },
            read_timeout_seconds=timedelta(seconds=45),
        )
        assert not create_result.isError
        assert "Successfully created lab" in _text_content(create_result)

        try:
            labs_result = await session.call_tool("list_labs", {"path": "/"})
            assert not labs_result.isError
            assert lab_name in _text_content(labs_result)

            details_result = await session.call_tool(
                "get_lab_details",
                {"lab_path": lab_path},
                read_timeout_seconds=timedelta(seconds=45),
            )
            assert not details_result.isError
            details_text = _text_content(details_result)
            assert "Lab Details" in details_text
            assert lab_name in details_text
        finally:
            delete_result = await session.call_tool(
                "delete_lab",
                {"lab_path": lab_path},
                read_timeout_seconds=timedelta(seconds=45),
            )
            assert not delete_result.isError
            assert "Successfully deleted lab" in _text_content(delete_result)
