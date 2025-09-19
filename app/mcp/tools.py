from typing import Optional, List, Dict, Any
from fastmcp import FastMCP
from ..models.schemas import Message
from ..services.anonymization import ensure_union_input, anonymize_text, split_back, deanonymize_text

mcp = FastMCP(app_name="presidio-mcp")

@mcp.tool()
async def anonymize(session_id: str, text: Optional[str] = None, messages: Optional[List[Message]] = None, language: str = "en") -> Dict[str, Any]:
    joined, msgs, is_msgs = ensure_union_input(text, messages)
    anonymized, entity_map, reverse_map = anonymize_text(session_id, joined, language)
    if is_msgs and msgs is not None:
        return {"session_id": session_id, "messages": [m.model_dump() for m in split_back(anonymized, msgs)], "entity_map": entity_map, "reverse_map": reverse_map}
    return {"session_id": session_id, "text": anonymized, "entity_map": entity_map, "reverse_map": reverse_map}

@mcp.tool()
async def deanonymize(session_id: str, text: Optional[str] = None, messages: Optional[List[Message]] = None, entity_map: Optional[Dict[str, Dict[str, str]]] = None, reverse_map: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    joined, msgs, is_msgs = ensure_union_input(text, messages)
    if reverse_map:
        rmap = reverse_map
    elif entity_map:
        rmap = {v: k for ent in entity_map.values() for k, v in ent.items()}
    else:
        raise ValueError("Provide reverse_map or entity_map")
    dean = deanonymize_text(joined, rmap)
    if is_msgs and msgs is not None:
        return {"session_id": session_id, "messages": [m.model_dump() for m in split_back(dean, msgs)]}
    return {"session_id": session_id, "text": dean}
