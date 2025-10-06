# triepod-memory-cache

**MCP Server for Redis-based LLM response caching and general-purpose key-value operations**

## Overview

This project provides a [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server that exposes Redis operations through standardized MCP tools. It supports three transport modes: **MCP streamable HTTP** (primary, port 10750), **MCP stdio** (for CLI tools), and **HTTP API** (legacy REST endpoints).

### Key Features

- **7 Redis MCP Tools**: Basic operations, LLM caching, and cache management
- **Triple-Mode Operation**: HTTP API (FastAPI) + MCP stdio transport + MCP streamable HTTP
- **Docker Compose Stack**: Integrated Redis and TimescaleDB services
- **Environment-Based Configuration**: Flexible prefix/TTL settings
- **Clean stdio Protocol**: MCP-compliant wrapper script with proper logging
- **Streamable HTTP Transport**: MCP Inspector compatible on port 10750

## Attribution

- **Original Base**: [chuckwilliams37/mcp-server-docker](https://github.com/chuckwilliams37/mcp-server-docker) (MIT License)
- **MCP Framework**: [FastMCP](https://github.com/jlowin/fastmcp) by jlowin (Apache-2.0 License)
- **Customizations**: triepod-ai

## Evidence & Validation

All claims in this README are substantiated with verifiable evidence. See [`CLAIMS_VALIDATION.md`](CLAIMS_VALIDATION.md) for:

- ✅ Code references for all 7 MCP tools
- ✅ Runtime verification of dual-mode operation
- ✅ Container status and operational evidence
- ✅ Attribution verification with license information
- ✅ Documentation completeness assessment
- ✅ AI readiness score: **HIGH**

**Last Validated**: 2025-10-06 (Streamable HTTP added)

## Architecture

### Docker Compose Stack

```yaml
triepod-memory-cache (Python MCP server)
  ├── triepod-redis (Redis 7)
  └── triepod-timescaledb (TimescaleDB on PostgreSQL 14)
```

### Triple-Mode Operation

1. **MCP Streamable HTTP Mode** (default container process)
   - Runs: `uvicorn http_app:app --host 0.0.0.0 --port 10750`
   - Starts: FastMCP streamable HTTP server on port 10750
   - Endpoint: `/mcp` (GET, POST, DELETE methods)
   - Purpose: MCP Inspector compatible streamable HTTP transport
   - Features: Automatic tool schema generation, session management

2. **HTTP API Mode** (legacy, available via app.py)
   - Runs: `python app.py`
   - Starts: Uvicorn FastAPI server on port 8080
   - Purpose: HTTP REST API endpoints (e.g., `/predict`)

3. **MCP stdio Mode** (via wrapper script)
   - Runs: `python3 mcp_stdio.py` via `docker exec`
   - Transport: JSON-RPC over stdin/stdout
   - Purpose: MCP protocol communication for CLI tools

**Important**: The streamable HTTP mode is the primary transport, providing MCP Inspector compatibility and proper tool schema generation.

## Setup

### Prerequisites

- Docker and Docker Compose installed
- WSL2 (if on Windows)

### Installation

1. **Start the Docker Compose stack**:
   ```bash
   cd /home/bryan/_containers/triepod-memory-cache
   docker-compose up -d
   ```

2. **Verify containers are running**:
   ```bash
   docker ps | grep triepod
   ```

   Expected output:
   ```
   triepod-memory-cache
   triepod-redis
   triepod-timescaledb
   ```

### Configuration

Environment variables are set in `docker-compose.yml` and can be overridden via wrapper script or `.env`:

| Variable | Default | Description |
|----------|---------|-------------|
| `REDIS_HOST` | `triepod-redis` | Redis server hostname |
| `REDIS_PORT` | `6379` | Redis server port |
| `LLM_CACHE_PREFIX` | `llm_cache_prod` | Prefix for LLM cache keys |
| `LLM_CACHE_TTL` | `3600` | Default TTL for LLM cache (seconds) |
| `MCP_HTTP_PORT` | `10750` | Port for MCP streamable HTTP transport |
| `MCP_SERVER_PORT` | `8080` | Port for legacy HTTP API mode |

## Usage

### MCP Streamable HTTP (Recommended)

The server runs FastMCP's streamable HTTP transport by default on port 10750:

```bash
# Access MCP endpoint
curl http://localhost:10750/mcp \
  -H "Accept: application/json, text/event-stream"
```

**MCP Inspector Integration**:
```json
{
  "mcpServers": {
    "triepod-memory-cache": {
      "url": "http://localhost:10750/mcp",
      "transport": "streamable-http"
    }
  }
}
```

**Features**:
- ✅ MCP Inspector compatible
- ✅ Automatic tool schema generation from Pydantic annotations
- ✅ Session management handled by FastMCP
- ✅ RESTful `/mcp` endpoint (GET, POST, DELETE)
- ✅ All 7 Redis tools available via MCP protocol

**How it works**:
1. Session initialization: `GET /mcp` with `Accept: text/event-stream`
2. Message exchange: `POST /mcp` with session ID
3. Session cleanup: `DELETE /mcp` with session ID

**Verification**:
```bash
# Check server is listening on port 10750
netstat -tuln | grep 10750

# Check endpoint responds (should return session ID error - expected behavior)
curl http://localhost:10750/mcp -H "Accept: application/json, text/event-stream"

# View server logs
docker logs triepod-memory-cache --tail 20
```

Expected log output should show:
```
INFO:     Uvicorn running on http://0.0.0.0:10750
StreamableHTTP session manager started
```

### MCP stdio Wrapper

The recommended way to use this MCP server is via the stdio wrapper script:

```bash
~/run-redis-mcp.sh
```

**Features**:
- Clean stdio for MCP JSON-RPC communication
- Automatic logging to `~/.redis-mcp/logs/`
- Environment variable passthrough
- Container health check

**How it works**:
1. Checks if `triepod-memory-cache` container is running
2. Executes `docker exec -i triepod-memory-cache python3 -u mcp_stdio.py`
3. Redirects all logs/errors to timestamped log files
4. Maintains clean stdin/stdout for MCP protocol

### HTTP API (Alternative)

Access the FastAPI server directly:

```bash
curl http://localhost:8080/predict -H "Content-Type: application/json" -d '{"message":"test"}'
```

## MCP Tools

This server exposes **7 Redis tools** via MCP:

### Basic Redis Operations

1. **`redis_get(key: str) -> str`**
   - Get value from Redis by key
   - Returns: Value as string, or `None` if key doesn't exist

2. **`redis_set(key: str, value: str, ttl: int = None) -> str`**
   - Set key-value pair with optional TTL
   - Parameters:
     - `key`: Redis key name
     - `value`: String value to store
     - `ttl`: Optional expiration time in seconds
   - Returns: Confirmation message

3. **`redis_delete(key: str) -> str`**
   - Delete key from Redis
   - Returns: Number of keys deleted

### LLM Cache Operations

4. **`llm_cache_get(cache_key: str) -> str`**
   - Get cached LLM response using configured prefix
   - Actual Redis key: `{LLM_CACHE_PREFIX}:{cache_key}`
   - Returns: Cached response or `None`

5. **`llm_cache_set(cache_key: str, response: str, ttl: int = None) -> str`**
   - Cache LLM response with automatic prefixing
   - Parameters:
     - `cache_key`: Unique identifier for the cached response
     - `response`: LLM response text to cache
     - `ttl`: Optional TTL (defaults to `LLM_CACHE_TTL` env var)
   - Returns: Confirmation with full key and TTL

### Cache Management

6. **`cache_stats() -> dict`**
   - Get comprehensive Redis cache statistics
   - Returns:
     ```json
     {
       "total_keys": 1234,
       "llm_cache_keys": 567,
       "memory_used": "2.5M",
       "connected_clients": 3,
       "uptime_days": 7
     }
     ```

7. **`cache_clear(pattern: str = None) -> str`**
   - Clear cache keys matching pattern
   - Default pattern: `{LLM_CACHE_PREFIX}:*` (all LLM cache keys)
   - Returns: Number of keys deleted

For detailed tool reference and usage examples, see: [`/home/bryan/docs/cli-tools/redis-mcp-tools.md`](../../docs/cli-tools/redis-mcp-tools.md)

## File Structure

```
/home/bryan/_containers/triepod-memory-cache/
├── app/
│   ├── app.py              # Main MCP server with tool definitions
│   ├── http_app.py         # Streamable HTTP ASGI app (port 10750)
│   └── mcp_stdio.py        # MCP stdio entrypoint (separates concerns)
├── docker-compose.yml      # Multi-container orchestration
├── Dockerfile              # Container build definition
├── requirements.txt        # Python dependencies
├── .env                    # Environment configuration
└── README.md              # This file

/home/bryan/
└── run-redis-mcp.sh       # MCP stdio wrapper script with clean protocol
```

## Development

### Adding New Tools

Edit `app/app.py` and add new `@mcp.tool()` decorated functions:

```python
@mcp.tool()
def my_new_tool(param: str) -> str:
    """Tool description for MCP introspection"""
    # Implementation
    return result
```

### Rebuilding Container

```bash
cd /home/bryan/_containers/triepod-memory-cache
docker-compose build
docker-compose up -d
```

### Viewing Logs

**MCP stdio logs**:
```bash
tail -f ~/.redis-mcp/logs/redis-mcp-*.log
```

**Container logs**:
```bash
docker logs triepod-memory-cache -f
```

## Troubleshooting

### Container not running
```bash
cd /home/bryan/_containers/triepod-memory-cache
docker-compose up -d
```

### Port 10750 already in use
The container runs the streamable HTTP transport on port 10750 by default. Check if another service is using this port:
```bash
netstat -tuln | grep 10750
docker ps --filter "publish=10750"
```

### stdio output contaminated
Ensure you're using `~/run-redis-mcp.sh` wrapper, not running `docker exec` manually. The wrapper properly redirects all logs to files, keeping stdio clean for MCP JSON-RPC.

## License

Inherits MIT License from original chuckwilliams37/mcp-server-docker project.

## Implementation Notes

### Streamable HTTP Transport Pattern

The streamable HTTP implementation follows proven patterns from production MCP servers:
- **Pattern Source**: `mcp_streamable_http_patterns` collection in Qdrant
- **Reference Implementations**:
  - `mcp-server-qdrant` (port 10650)
  - `chroma-mcp` (port 10550)
- **Key Learnings**:
  - ✅ Use FastMCP's `streamable_http_app()` method (not SSE)
  - ✅ Create separate ASGI module for uvicorn import
  - ✅ Proper port mapping in docker-compose (not `network_mode: host`)
  - ✅ Automatic schema generation from Pydantic Field annotations

**Critical Pattern**:
```python
# http_app.py - ASGI module
from app import mcp
app = mcp.streamable_http_app()  # Exposes /mcp endpoint
```

This ensures MCP Inspector compatibility and proper tool schema generation without manual schema construction.

## References

- [Model Context Protocol Specification](https://spec.modelcontextprotocol.io)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Original Base Repository](https://github.com/chuckwilliams37/mcp-server-docker)
- [MCP Streamable HTTP Patterns](https://docs.modelcontextprotocol.io/concepts/transports#http-with-sse)
