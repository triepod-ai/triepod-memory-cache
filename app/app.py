from fastapi import FastAPI
from pydantic import BaseModel
import redis
import os
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()  # Load .env into environment

# Redis connection from env
redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = int(os.getenv("REDIS_PORT", "6379"))
redis_client = redis.Redis(host=redis_host, port=redis_port)

# Create FastAPI app
app = FastAPI()

# Create MCP server
mcp = FastMCP(name="triepod-memory-cache")

# Redis Tools
@mcp.tool()
def redis_get(key: str) -> str:
    """Get value from Redis by key"""
    value = redis_client.get(key)
    return value.decode('utf-8') if value else None

@mcp.tool()
def redis_set(key: str, value: str, ttl: int = None) -> str:
    """Set key-value pair in Redis with optional TTL (seconds)"""
    if ttl:
        redis_client.setex(key, ttl, value)
    else:
        redis_client.set(key, value)
    return f"Set {key} = {value}" + (f" (TTL: {ttl}s)" if ttl else "")

@mcp.tool()
def redis_delete(key: str) -> str:
    """Delete key from Redis"""
    deleted = redis_client.delete(key)
    return f"Deleted {deleted} key(s)"

# LLM Cache Tools
@mcp.tool()
def llm_cache_get(cache_key: str) -> str:
    """Get cached LLM response by cache key"""
    prefix = os.getenv("LLM_CACHE_PREFIX", "llm_cache_prod")
    full_key = f"{prefix}:{cache_key}"
    value = redis_client.get(full_key)
    return value.decode('utf-8') if value else None

@mcp.tool()
def llm_cache_set(cache_key: str, response: str, ttl: int = None) -> str:
    """Cache LLM response with optional TTL (defaults to LLM_CACHE_TTL env var)"""
    prefix = os.getenv("LLM_CACHE_PREFIX", "llm_cache_prod")
    default_ttl = int(os.getenv("LLM_CACHE_TTL", "3600"))
    ttl = ttl or default_ttl
    full_key = f"{prefix}:{cache_key}"
    redis_client.setex(full_key, ttl, response)
    return f"Cached {full_key} (TTL: {ttl}s)"

# Cache Management Tools
@mcp.tool()
def cache_stats() -> dict:
    """Get Redis cache statistics"""
    info = redis_client.info()
    prefix = os.getenv("LLM_CACHE_PREFIX", "llm_cache_prod")
    llm_keys = redis_client.keys(f"{prefix}:*")
    return {
        "total_keys": redis_client.dbsize(),
        "llm_cache_keys": len(llm_keys),
        "memory_used": info.get('used_memory_human'),
        "connected_clients": info.get('connected_clients'),
        "uptime_days": info.get('uptime_in_days')
    }

@mcp.tool()
def cache_clear(pattern: str = None) -> str:
    """Clear cache keys matching pattern (default: all LLM cache keys)"""
    prefix = os.getenv("LLM_CACHE_PREFIX", "llm_cache_prod")
    pattern = pattern or f"{prefix}:*"
    keys = redis_client.keys(pattern)
    if keys:
        deleted = redis_client.delete(*keys)
        return f"Deleted {deleted} keys matching '{pattern}'"
    return f"No keys found matching '{pattern}'"

class Input(BaseModel):
    message: str

@app.post("/predict")
def predict(input: Input):
    redis_client.set("last_input", input.message)
    return {"echo": input.message}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("MCP_SERVER_PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
