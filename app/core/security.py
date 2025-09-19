import base64
import hashlib
import hmac
from .config import settings

if not settings.PLACEHOLDER_SECRET:
    settings.PLACEHOLDER_SECRET = base64.urlsafe_b64encode(hashlib.sha256(b"ephemeral").digest()).decode()

def hmac_placeholder(entity_type: str, original: str, session_id: str) -> str:
    msg = f"{session_id}|{entity_type}|{original}".encode()
    digest = hmac.new(settings.PLACEHOLDER_SECRET.encode(), msg, hashlib.sha256).hexdigest()
    return f"<<{entity_type}_{digest[:10]}>>"
