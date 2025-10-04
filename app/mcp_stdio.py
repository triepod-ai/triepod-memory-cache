#!/usr/bin/env python3
"""
MCP Server - stdio mode entrypoint
Runs the triepod-memory-cache MCP server using stdio transport for MCP protocol.
"""

from app import mcp

if __name__ == "__main__":
    # Run MCP server in stdio mode (JSON-RPC over stdin/stdout)
    mcp.run()
