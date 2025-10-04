# triepod-memory-cache

**MCP Server for Redis-based LLM response caching and general-purpose key-value operations**

## Overview

This project provides a [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server that exposes Redis operations through standardized MCP tools. It supports both HTTP API mode and stdio transport for MCP protocol communication.

### Key Features

- **7 Redis MCP Tools**: Basic operations, LLM caching, and cache management
- **Dual-Mode Operation**: HTTP API (FastAPI) + MCP stdio transport
- **Docker Compose Stack**: Integrated Redis and TimescaleDB services
- **Environment-Based Configuration**: Flexible prefix/TTL settings
- **Clean stdio Protocol**: MCP-compliant wrapper script with proper logging

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

**Last Validated**: 2025-10-04

## Architecture

### Docker Compose Stack

```yaml
triepod-memory-cache (Python MCP server)
  ├── triepod-redis (Redis 7)
  └── triepod-timescaledb (TimescaleDB on PostgreSQL 14)
```

### Dual-Mode Operation

1. **HTTP API Mode** (default container process)
   - Runs: `python app.py`
   - Starts: Uvicorn FastAPI server on port 8080
   - Purpose: HTTP REST API endpoints

2. **MCP stdio Mode** (via wrapper script)
   - Runs: `python3 mcp_stdio.py` via `docker exec`
   - Transport: JSON-RPC over stdin/stdout
   - Purpose: MCP protocol communication

**Important**: The separation prevents port conflicts and maintains clean stdio channels required by MCP protocol.

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

Environment variables are set in `docker-compose.yml` and can be overridden via wrapper script or `~/auth/.env`:

| Variable | Default | Description |
|----------|---------|-------------|
| `REDIS_HOST` | `triepod-redis` | Redis server hostname |
| `REDIS_PORT` | `6379` | Redis server port |
| `LLM_CACHE_PREFIX` | `llm_cache_prod` | Prefix for LLM cache keys |
| `LLM_CACHE_TTL` | `3600` | Default TTL for LLM cache (seconds) |

## Usage

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
│   ├── app.py              # Main FastAPI + MCP server (HTTP mode)
│   └── mcp_stdio.py        # MCP stdio entrypoint (separates concerns)
├── docker-compose.yml      # Multi-container orchestration
├── Dockerfile              # Container build definition
├── requirements.txt        # Python dependencies
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

### Port 8080 already in use
This is expected. The HTTP server runs as the container's main process. The MCP stdio wrapper uses `docker exec` to run a separate `mcp_stdio.py` process that doesn't bind any ports.

### stdio output contaminated
Ensure you're using `~/run-redis-mcp.sh` wrapper, not running `docker exec` manually. The wrapper properly redirects all logs to files, keeping stdio clean for MCP JSON-RPC.

## License

Inherits MIT License from original chuckwilliams37/mcp-server-docker project.

## References

- [Model Context Protocol Specification](https://spec.modelcontextprotocol.io)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Original Base Repository](https://github.com/chuckwilliams37/mcp-server-docker)
