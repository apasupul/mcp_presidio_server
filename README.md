# Presidio MCP + FastAPI Anonymize/Deanonymize (DB-free)

This variant removes all persistence. You must carry `entity_map` or `reverse_map` between calls yourself.

## Run API
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Env
- PLACEHOLDER_SECRET – set in prod for deterministic tags across restarts

## MCP Tools
Import `app.mcp.tools:mcp` in your MCP host; it exposes `anonymize` & `deanonymize` with identical behavior to the API.

## Endpoints
- POST /anonymize → { session_id, text|messages, entity_map, reverse_map }
- POST /deanonymize → requires (reverse_map or entity_map), returns { session_id, text|messages }

## Notes
- Placeholders are HMAC-SHA256 derived: <<TYPE_aaaaaaaaaa>> (first 10 hex chars).
- Deterministic per (session_id, entity_type, original); different sessions yield different tags.
- No database is used; no `map_id` support.
