"""Shared pytest configuration for the integration-focused test suite."""

from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
import warnings
from pathlib import Path
from typing import Dict

import pytest


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _env_or_default(name: str, default: str) -> str:
    value = os.getenv(name)
    return value if value not in (None, "") else default


def pytest_addoption(parser: pytest.Parser) -> None:
    """Add command-line options used by integration tests."""
    parser.addoption(
        "--eveng-host",
        action="store",
        default=_env_or_default("TEST_EVENG_HOST", ""),
        help="EVE-NG server host for live integration tests",
    )
    parser.addoption(
        "--eveng-user",
        action="store",
        default=_env_or_default("TEST_EVENG_USERNAME", ""),
        help="EVE-NG username for live integration tests",
    )
    parser.addoption(
        "--eveng-pass",
        action="store",
        default=_env_or_default("TEST_EVENG_PASSWORD", ""),
        help="EVE-NG password for live integration tests",
    )
    parser.addoption(
        "--eveng-port",
        action="store",
        default=int(_env_or_default("TEST_EVENG_PORT", "80")),
        type=int,
        help="EVE-NG port for live integration tests",
    )
    parser.addoption(
        "--eveng-protocol",
        action="store",
        default=_env_or_default("TEST_EVENG_PROTOCOL", "http"),
        help="EVE-NG protocol for live integration tests",
    )


def pytest_configure(config: pytest.Config) -> None:
    """Register markers used by the integration suite."""
    config.addinivalue_line(
        "markers",
        "live_eveng: marks tests that require a reachable live EVE-NG server",
    )
    config.addinivalue_line(
        "markers",
        "stdio: marks tests that exercise the MCP stdio transport",
    )
    config.addinivalue_line(
        "markers",
        "sse: marks tests that exercise the MCP SSE transport",
    )
    warnings.filterwarnings(
        "ignore",
        message=".*I/O operation on closed pipe.*",
        category=pytest.PytestUnraisableExceptionWarning,
    )


@pytest.fixture(scope="session")
def eveng_config(pytestconfig: pytest.Config) -> Dict[str, str | int]:
    """Return live EVE-NG settings used by integration tests."""
    return {
        "host": pytestconfig.getoption("--eveng-host"),
        "username": pytestconfig.getoption("--eveng-user"),
        "password": pytestconfig.getoption("--eveng-pass"),
        "port": pytestconfig.getoption("--eveng-port"),
        "protocol": pytestconfig.getoption("--eveng-protocol"),
    }


@pytest.fixture(scope="session")
def server_env(eveng_config: Dict[str, str | int]) -> Dict[str, str]:
    """Environment for spawning the MCP server with deterministic settings."""
    env = os.environ.copy()
    env.update(
        {
            "DEBUG": "false",
            "TESTING": "true",
            "EVENG_HOST": str(eveng_config["host"]),
            "EVENG_USERNAME": str(eveng_config["username"]),
            "EVENG_PASSWORD": str(eveng_config["password"]),
            "EVENG_PORT": str(eveng_config["port"]),
            "EVENG_PROTOCOL": str(eveng_config["protocol"]),
            "MCP_LOG_FORMAT": "console",
            "MCP_LOG_LEVEL": "INFO",
            "PYTHONIOENCODING": "utf-8",
            "PYTHONUTF8": "1",
        }
    )
    return env


@pytest.fixture(scope="session")
def python_executable() -> str:
    """Python interpreter used to launch the project during tests."""
    venv_python = PROJECT_ROOT / ".venv" / "Scripts" / "python.exe"
    if venv_python.exists():
        return str(venv_python)
    return sys.executable


@pytest.fixture(scope="session")
def require_live_eveng(eveng_config: Dict[str, str | int]) -> Dict[str, str | int]:
    """Skip a test unless live EVE-NG credentials are configured."""
    required = ("host", "username", "password")
    if not all(eveng_config[key] for key in required):
        pytest.skip("Live EVE-NG integration is not configured")
    return eveng_config


def _wait_for_tcp_port(host: str, port: int, timeout_seconds: float = 20.0) -> None:
    """Wait for a TCP port to start accepting connections."""
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1.0)
            if sock.connect_ex((host, port)) == 0:
                return
        time.sleep(0.25)
    raise RuntimeError(f"Timed out waiting for {host}:{port}")


@pytest.fixture
def sse_server(server_env: Dict[str, str], python_executable: str) -> Dict[str, str | int]:
    """Launch the MCP server in SSE mode for the duration of a test."""
    host = "127.0.0.1"
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((host, 0))
        port = sock.getsockname()[1]

    command = [
        python_executable,
        "-m",
        "eveng_mcp_server.cli",
        "run",
        "--transport",
        "sse",
        "--host",
        host,
        "--port",
        str(port),
    ]

    process = subprocess.Popen(
        command,
        cwd=PROJECT_ROOT,
        env=server_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    try:
        _wait_for_tcp_port(host, port)
        yield {"host": host, "port": port, "process": process}
    finally:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=10)
