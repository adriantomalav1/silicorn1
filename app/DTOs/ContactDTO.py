from enum import Enum
from typing import Optional
from pydantic import BaseModel

class ContactDTO(BaseModel):
    id: str
    email: str
    first_name: str
    status: str
    last_name: Optional[str] = None
    phone: Optional[str] = None

class SaveContactDTO(BaseModel):
    email: str
    first_name: str
    last_name: Optional[str] = None
    phone: Optional[str] = None

class SaveCampaignContactDTO(BaseModel):
    contact: SaveContactDTO
    context: Optional[dict] = None

class CampaignContactDTO(BaseModel):
    contact: ContactDTO
    context: Optional[dict] = None

class ContactStatus(str, Enum):
    ACTIVE = "ACTIVE"
    BLACKLISTED = "BLACKLISTED"
