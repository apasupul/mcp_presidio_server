# MCP Presidio Server (Anonymize/Deanonymize)

This project exposes the same functionality via **MCP tools** and **FastAPI** endpoints.

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate  # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Endpoints
- `POST /session` -> `{ "session_id": "<uuid>" }`
- `POST /anonymize` body:
```json
{
  "session_id": "uuid",
  "messages": [{"content": "Secret is 123, password=foo"}]
}
```
returns anonymized messages and stores mapping for the session.

- `POST /deanonymize` body:
```json
{
  "session_id": "uuid",
  "text": "<<CUSTOM_TOKEN_0>> is 123, <<pass_pattern_...>>"
}
```

### MCP server

Run the stdio MCP server:

```bash
python mcp_server/server.py
```

Register it in your MCP-compatible client pointing to this command.

### Notes
- Storage uses SQLite at `app/data.db` with tables `sessions` and `mappings`.
- Custom patterns mirror the code you provided; add more Presidio recognizers as needed.
- Placeholders look like `<<ENTITY_#>>` and are reversible per `session_id`.
