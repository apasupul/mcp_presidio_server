import asyncio
import logging, logging.config, uuid
from typing import List, Dict, Any

from mcp.server.fastmcp import FastMCP, Context
from app.services import storage
from app.services.anonymizer import content_anonymizer, reverse_mapping, content_deanonymizer
from collections import defaultdict

logging.config.fileConfig("logging.conf")
logger = logging.getLogger(__name__)

mcp = FastMCP("mcp-presidio-server")

@mcp.tool()
async def generate_session_id(ctx: Context) -> Dict[str, str]:
    """Generate and persist a new session id."""
    sid = str(uuid.uuid4())
    storage.create_session(sid)
    return {"session_id": sid}

@mcp.tool()
async def anonymize(session_id: str, texts: List[str]) -> Dict[str, Any]:
    """Anonymize a list of texts and store mappings under session_id."""
    storage.create_session(session_id)
    entity_mapping = defaultdict(dict)
    entity_counter = defaultdict(int)
    anon_texts: List[str] = []
    for t in texts:
        anon, entity_mapping, entity_counter = content_anonymizer(t, entity_mapping, entity_counter)
        anon_texts.append(anon)
    rev = reverse_mapping(entity_mapping)  # placeholder -> original
    storage.save_mappings(session_id, rev)
    return {"session_id": session_id, "texts": anon_texts}

@mcp.tool()
async def deanonymize(session_id: str, text: str) -> Dict[str, str]:
    """Given session_id and anonymized text, return deanonymized text."""
    rev = storage.get_mapping(session_id)
    if not rev:
        return {"error": "No mapping for session_id", "text": text}
    return {"text": content_deanonymizer(text, rev), "session_id": session_id}

if __name__ == "__main__":
    # Run an stdio MCP server
    mcp.run()
