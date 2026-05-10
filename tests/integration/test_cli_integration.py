"""Integration tests for the project CLI."""

from __future__ import annotations

import subprocess
import time
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _run_cli(
    python_executable: str, args: list[str], env: dict[str, str], timeout: int = 60
) -> subprocess.CompletedProcess[str]:
    """Run the packaged CLI inside uv."""
    return subprocess.run(
        [python_executable, "-m", "eveng_mcp_server.cli", *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        env=env,
        cwd=PROJECT_ROOT,
    )


def test_cli_version(server_env: dict[str, str], python_executable: str) -> None:
    """The CLI should print version information."""
    result = _run_cli(python_executable, ["version"], server_env)
    assert result.returncode == 0
    assert "EVE-NG MCP Server" in result.stdout


def test_cli_config_info(server_env: dict[str, str], python_executable: str) -> None:
    """The CLI should print effective configuration."""
    result = _run_cli(python_executable, ["config-info"], server_env)
    assert result.returncode == 0
    assert "EVE-NG Configuration" in result.stdout
    assert "MCP Configuration" in result.stdout


@pytest.mark.live_eveng
def test_cli_test_connection(
    server_env: dict[str, str],
    require_live_eveng: dict[str, str | int],
    python_executable: str,
) -> None:
    """The CLI should connect successfully to the live EVE-NG server."""
    args = [
        "test-connection",
        "--host",
        str(require_live_eveng["host"]),
        "--username",
        str(require_live_eveng["username"]),
        "--password",
        str(require_live_eveng["password"]),
        "--port",
        str(require_live_eveng["port"]),
        "--protocol",
        str(require_live_eveng["protocol"]),
    ]

    result = None
    for attempt in range(3):
        result = _run_cli(python_executable, args, server_env)
        if result.returncode == 0:
            break
        time.sleep(1 + attempt)

    assert result is not None
    assert result.returncode == 0
    assert "Connection successful" in result.stdout
