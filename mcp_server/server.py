#!/usr/bin/env python3
"""MCP stdio server process for the engineering-learnings vault.

This is the process boundary only (spec 0002): a stdio transport wired up
via the official `mcp` SDK, with zero tools registered. search_learnings
(#4) and add_learning (#5) attach their tools to `mcp` below with
`@mcp.tool()` -- this module holds no ranking or writing logic of its own,
mirroring reindex.py's separation of pure build logic from its CLI shell.
"""
import os
import sys
from pathlib import Path

from mcp.server.mcpserver import MCPServer

# The server's only required configuration: where the vault lives.
REPO_PATH_ENV = "LEARNINGS_REPO_PATH"

mcp = MCPServer("engineering-learnings")


def get_repo_path() -> Path:
    """Resolve the target vault repo path from REPO_PATH_ENV.

    Future tools (search_learnings, add_learning) call this to find
    INDEX.json and learnings/ under the configured repo.
    """
    raw = os.environ.get(REPO_PATH_ENV)
    if not raw:
        sys.exit(f"error: {REPO_PATH_ENV} env var is required (path to the engineering-learnings repo)")
    return Path(raw).resolve()


def main():
    get_repo_path()  # fail fast on missing config, before opening the stdio transport
    mcp.run()  # blocks, serving MCP over stdio (transport="stdio" is the default)


if __name__ == "__main__":
    main()
