## Redis MCP Server - triepod-memory-cache

### Purpose
Redis-based LLM response caching and general key-value operations via MCP protocol

### Architecture
- **Wrapper Script**: `~/run-redis-mcp.sh` - MCP stdio transport with clean protocol compliance
- **Container**: `triepod-memory-cache` - Docker Compose stack with Redis + TimescaleDB
- **Dual-Mode Operation**:
  - **HTTP API**: Container main process runs `python app.py` (FastAPI on port 8080)
  - **MCP stdio**: Wrapper runs `docker exec python3 mcp_stdio.py` (clean JSON-RPC transport)

### MCP Tools (7 Available)
- **Basic Redis**: `redis_get`, `redis_set`, `redis_delete`
- **LLM Cache**: `llm_cache_get`, `llm_cache_set` (with automatic prefix management)
- **Management**: `cache_stats`, `cache_clear`

### Environment Variables
- `LLM_CACHE_PREFIX=llm_cache_prod` - Isolates LLM cache keys
- `LLM_CACHE_TTL=3600` - Default cache expiration (1 hour)
- `REDIS_HOST=triepod-redis`, `REDIS_PORT=6379`

### Attribution
- **Base**: [chuckwilliams37/mcp-server-docker](https://github.com/chuckwilliams37/mcp-server-docker)
- **Framework**: FastMCP by jlowin
- **Customizations**: triepod-ai

### Documentation
- **Main README**: `~/_containers/triepod-memory-cache/README.md`
- **Tools Reference**: `~/docs/cli-tools/redis-mcp-tools.md`

### Critical Patterns
- **stdio must remain clean** for MCP protocol - all logs redirect to `~/.redis-mcp/logs/`
- **Dual-mode separation** prevents port conflicts and maintains clean JSON-RPC channels

### Status
✅ **Operational & Validated** (2025-10-04)
- 7 tools implemented and tested
- Clean stdio protocol compliance verified
- Proper dual-mode HTTP/stdio separation
- Documentation complete with verified claims
- CLAIMS_VALIDATION.md created with full evidence
- LICENSE file added (MIT + Apache-2.0 attributions)
- AI readiness score: HIGH
