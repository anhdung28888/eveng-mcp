#!/usr/bin/env python3
"""Integration test runner for the EVE-NG MCP Server."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
INTEGRATION_DIR = Path(__file__).resolve().parent / "integration"
PYTHON_EXE = PROJECT_ROOT / ".venv" / "Scripts" / "python.exe"


def build_pytest_command(args: argparse.Namespace) -> list[str]:
    """Build the pytest command for the integration suite."""
    python_executable = str(PYTHON_EXE if PYTHON_EXE.exists() else sys.executable)
    command = [python_executable, "-m", "pytest", str(INTEGRATION_DIR), "-q"]

    if args.collect_only:
        command.append("--collect-only")

    if args.live:
        command.extend(
            [
                "-m",
                "live_eveng",
                "--eveng-host",
                args.eveng_host,
                "--eveng-user",
                args.eveng_user,
                "--eveng-pass",
                args.eveng_pass,
                "--eveng-port",
                str(args.eveng_port),
                "--eveng-protocol",
                args.eveng_protocol,
            ]
        )
    else:
        command.extend(["-m", "not live_eveng"])

    return command


def main() -> int:
    parser = argparse.ArgumentParser(description="Run integration tests only")
    parser.add_argument("--collect-only", action="store_true", help="Only collect tests")
    parser.add_argument("--live", action="store_true", help="Run live EVE-NG integration tests")
    parser.add_argument("--eveng-host", default=os.getenv("TEST_EVENG_HOST", ""), help="EVE-NG host")
    parser.add_argument("--eveng-user", default=os.getenv("TEST_EVENG_USERNAME", ""), help="EVE-NG user")
    parser.add_argument("--eveng-pass", default=os.getenv("TEST_EVENG_PASSWORD", ""), help="EVE-NG password")
    parser.add_argument("--eveng-port", type=int, default=int(os.getenv("TEST_EVENG_PORT", "80")), help="EVE-NG port")
    parser.add_argument(
        "--eveng-protocol",
        default=os.getenv("TEST_EVENG_PROTOCOL", "http"),
        help="EVE-NG protocol",
    )
    args = parser.parse_args()

    command = build_pytest_command(args)
    result = subprocess.run(command, cwd=PROJECT_ROOT)
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
