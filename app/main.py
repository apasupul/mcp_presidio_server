import logging, logging.config, uuid
from fastapi import FastAPI, HTTPException
from app.models.schemas import (Message, AnonymizeRequest, AnonymizeResponse,
                                DeAnonymizeRequest, DeAnonymizeResponse, SessionResponse)
from app.services.anonymizer import content_anonymizer, reverse_mapping, content_deanonymizer
from app.services import storage
from collections import defaultdict

logging.config.fileConfig("logging.conf")
logger = logging.getLogger("app")

app = FastAPI(title="MCP Presidio Anonymizer API", version="1.0.0")

@app.post("/session", response_model=SessionResponse)
def new_session():
    sid = str(uuid.uuid4())
    storage.create_session(sid)
    return SessionResponse(session_id=sid)

@app.post("/anonymize", response_model=AnonymizeResponse)
def anonymize(req: AnonymizeRequest):
    storage.create_session(req.session_id)
    entity_mapping = defaultdict(dict)
    entity_counter = defaultdict(int)
    out_messages = []
    for msg in req.messages:
        anon_text, entity_mapping, entity_counter = content_anonymizer(
            msg.content, entity_mapping, entity_counter
        )
        out_messages.append(Message(content=anon_text))

    # Persist reverse map
    rev = reverse_mapping(entity_mapping)  # placeholder -> original
    storage.save_mappings(req.session_id, rev)
    return AnonymizeResponse(session_id=req.session_id, messages=out_messages)

@app.post("/deanonymize", response_model=DeAnonymizeResponse)
def deanonymize(req: DeAnonymizeRequest):
    rev = storage.get_mapping(req.session_id)
    if not rev:
        raise HTTPException(status_code=404, detail="No mapping for session_id")
    text = content_deanonymizer(req.text, rev)
    return DeAnonymizeResponse(session_id=req.session_id, text=text)

@app.get("/sessions")
def sessions():
    return {"sessions": storage.list_sessions()}
