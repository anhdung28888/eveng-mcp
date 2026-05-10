# Testing Guide

The automated test pipeline for this repository is integration-test focused.

## Scope

The maintained automated suite covers:

- CLI integration checks
- MCP `stdio` transport checks
- MCP `sse` transport checks
- Live EVE-NG workflow checks when credentials are provided

The following content is not part of the default automated gate:

- `tests/unit/`
- `tests/e2e/`
- `tests/legacy/`
- ad-hoc helper scripts in `tests/integration/` that are not named `test_*.py`

## Prerequisites

- Python 3.11 or higher
- `uv`
- Optional live EVE-NG server access for `live_eveng` tests

## Install Dependencies

```bash
uv sync --extra test
```

## Automated Commands

Run automated integration tests that do not require a live EVE-NG server:

```bash
uv run python -m pytest tests/integration -m "not live_eveng" -q
```

Run live integration tests:

```bash
uv run python -m pytest tests/integration -m live_eveng -q \
  --eveng-host 192.168.168.141 \
  --eveng-user admin \
  --eveng-pass eve \
  --eveng-port 80 \
  --eveng-protocol http
```

Collect the integration suite only:

```bash
uv run python -m pytest tests/integration --collect-only -q
```

Use the lightweight runner:

```bash
python tests/run_tests.py
python tests/run_tests.py --collect-only
python tests/run_tests.py --live --eveng-host 192.168.168.141 --eveng-user admin --eveng-pass eve
```

## Live Test Configuration

You can provide live EVE-NG settings either by CLI options or environment variables:

```bash
TEST_EVENG_HOST=192.168.168.141
TEST_EVENG_USERNAME=admin
TEST_EVENG_PASSWORD=eve
TEST_EVENG_PORT=80
TEST_EVENG_PROTOCOL=http
```

## Current Automated Coverage

- `test_cli_integration.py`
  - `version`
  - `config-info`
  - `test-connection` against a live server
- `test_mcp_http.py`
  - `stdio` MCP surface
  - live lab lifecycle through MCP tools
- `test_socat_bridge.py`
  - `sse` MCP surface

## Notes

- The live suite creates a temporary lab and deletes it during cleanup.
- On Windows, the upstream MCP client can emit subprocess shutdown noise; the suite filters the known harmless warning.
