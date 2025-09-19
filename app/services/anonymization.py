from typing import Dict, List, Tuple
from ..core.security import hmac_placeholder
from ..models.schemas import Message
from .analyzer import analyze

SEP = "\u0000"  # sentinel separator for messages


def ensure_union_input(text, messages):
    if messages is not None:
        return SEP.join([m.content for m in messages]), messages, True
    if text is None:
        raise ValueError("Either `text` or `messages` must be provided")
    return text, None, False


def split_back(joined: str, messages: List[Message]) -> List[Message]:
    parts = joined.split(SEP)
    out = []
    for i, m in enumerate(messages):
        nm = m.copy(deep=True)
        nm.content = parts[i] if i < len(parts) else ""
        out.append(nm)
    return out


def anonymize_text(session_id: str, text: str, language: str = "en") -> Tuple[str, Dict[str, Dict[str, str]], Dict[str, str]]:
    results = analyze(text, language)
    cursor = 0
    pieces: List[str] = []
    entity_map: Dict[str, Dict[str, str]] = {}

    for r in results:
        if r.start < cursor:
            continue
        pieces.append(text[cursor:r.start])
        etype = r.entity_type
        original = text[r.start:r.end]
        entity_map.setdefault(etype, {})
        if original not in entity_map[etype]:
            ph = hmac_placeholder(etype, original, session_id)
            entity_map[etype][original] = ph
        else:
            ph = entity_map[etype][original]
        pieces.append(ph)
        cursor = r.end
    pieces.append(text[cursor:])

    anonymized = "".join(pieces)
    reverse_map = {v: k for ent in entity_map.values() for k, v in ent.items()}
    return anonymized, entity_map, reverse_map


def deanonymize_text(text: str, reverse_map: Dict[str, str]) -> str:
    for ph in sorted(reverse_map.keys(), key=len, reverse=True):
        text = text.replace(ph, reverse_map[ph])
    return text
