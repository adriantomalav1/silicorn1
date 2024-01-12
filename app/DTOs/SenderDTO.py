from typing import Optional
from pydantic import BaseModel

class SenderDTO(BaseModel):
    id: str
    name: str
    email: str
    domain: str
    variables: Optional[dict] = None

class AddSenderDTO(BaseModel):
    name: str
    email: str
    domain: str
    variables: Optional[dict] = None
