#!/usr/bin/env python3
"""MCP stdio server process for the engineering-learnings vault.

This is the process boundary only (spec 0002): a stdio transport wired up
via the official `mcp` SDK, with zero tools registered. search_learnings
(#4) and add_learning (#5) attach their tools to `mcp` below with
`@mcp.tool()` -- this module holds no ranking or writing logic of its own,
mirroring reindex.py's separation of pure build logic from its CLI shell.
"""
import json
import os
import sys
from pathlib import Path

from mcp.server.mcpserver import MCPServer

from mcp_server.search import search_learnings as _search_learnings

# The server's only required configuration: where the vault lives.
REPO_PATH_ENV = "LEARNINGS_REPO_PATH"

mcp = MCPServer("engineering-learnings")


@mcp.tool(name="search_learnings")
def search_learnings_tool(query: str = None, tags: list[str] = None, project: str = None) -> list[dict]:
    """Search this vault's Learnings by query text, tags, and/or project.

    Ranked results: corroboration boosts, superseded entries rank lower but
    still appear. Thin adapter over the pure search_learnings() -- reads
    INDEX.json here so the ranking function itself stays filesystem-free.
    """
    index_path = get_repo_path() / "INDEX.json"
    entries = json.loads(index_path.read_text())
    return _search_learnings(entries, query=query, tags=tags, project=project)


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
