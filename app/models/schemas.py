from typing import Dict, List, Optional, Union
from pydantic import BaseModel

class Message(BaseModel):
    role: Optional[str] = None
    content: str

TextOrMessages = Union[str, List[Message]]

class AnonymizeRequest(BaseModel):
    session_id: str
    text: Optional[str] = None
    messages: Optional[List[Message]] = None
    language: str = "en"

class AnonymizeResponse(BaseModel):
    session_id: str
    text: Optional[str] = None
    messages: Optional[List[Message]] = None
    entity_map: Dict[str, Dict[str, str]]
    reverse_map: Dict[str, str]

class DeanonymizeRequest(BaseModel):
    session_id: str
    text: Optional[str] = None
    messages: Optional[List[Message]] = None
    entity_map: Optional[Dict[str, Dict[str, str]]] = None
    reverse_map: Optional[Dict[str, str]] = None

class DeanonymizeResponse(BaseModel):
    session_id: str
    text: Optional[str] = None
    messages: Optional[List[Message]] = None
