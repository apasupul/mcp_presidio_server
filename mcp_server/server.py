import logging, logging.config, uuid
from typing import List, Dict, Any
from pathlib import Path
from mcp.server.fastmcp import FastMCP, Context
from app.services import storage
from app.services.anonymizer import content_anonymizer, reverse_mapping, content_deanonymizer
from collections import defaultdict

try:
    _CONF = Path(__file__).resolve().parents[1] / "logging.conf"
    logging.config.fileConfig(_CONF)
except Exception:
    logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)
mcp = FastMCP("mcp-presidio-server")

@mcp.tool()
async def generate_session_id(ctx: Context) -> Dict[str, str]:
    sid = str(uuid.uuid4())
    storage.create_session(sid)
    return {"session_id": sid}

@mcp.tool()
async def anonymize(session_id: str, texts: List[str]) -> Dict[str, Any]:
    storage.create_session(session_id)
    entity_mapping = defaultdict(dict)
    entity_counter = defaultdict(int)
    anon_texts: List[str] = []
    for t in texts:
        anon, entity_mapping, entity_counter = content_anonymizer(
            t, entity_mapping, entity_counter, session_id=session_id
        )
        anon_texts.append(anon)
    rev = reverse_mapping(entity_mapping)
    storage.save_mappings(session_id, rev)
    return {"session_id": session_id, "texts": anon_texts}

@mcp.tool()
async def deanonymize(session_id: str, text: str) -> Dict[str, str]:
    rev = storage.get_mapping(session_id)
    if not rev:
        return {"error": "No mapping for session_id", "text": text}
    return {"text": content_deanonymizer(text, rev), "session_id": session_id}

if __name__ == "__main__":
    mcp.run()
