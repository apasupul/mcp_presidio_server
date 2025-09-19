from pydantic import BaseModel, Field
from typing import List, Optional

class Message(BaseModel):
    content: str

class AnonymizeRequest(BaseModel):
    session_id: str
    messages: List[Message]

class AnonymizeResponse(BaseModel):
    session_id: str
    messages: List[Message]

class DeAnonymizeRequest(BaseModel):
    session_id: str
    text: str

class DeAnonymizeResponse(BaseModel):
    session_id: str
    text: str

class SessionResponse(BaseModel):
    session_id: str
