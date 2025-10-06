"""
ASGI application module for uvicorn to import.
Exports the FastMCP streamable HTTP app for HTTP transport.

This uses FastMCP's built-in streamable_http_app() method which automatically
handles schema generation, session management, and MCP protocol compliance.

The streamable HTTP transport exposes the /mcp endpoint with GET, POST, DELETE methods:
- GET /mcp: Initialize session
- POST /mcp: Send messages
- DELETE /mcp: Close session

This is compatible with MCP Inspector and other MCP clients expecting streamable HTTP.
"""
from app import mcp

# Get the FastAPI app from FastMCP's streamable HTTP implementation
# This ensures proper tool schema generation and MCP protocol compliance
app = mcp.streamable_http_app()
