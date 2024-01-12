from enum import Enum
from pydantic import BaseModel
from typing import List, Optional
from app.DTOs.ContactDTO import SaveCampaignContactDTO

from app.DTOs.SenderDTO import SenderDTO

class MessageTemplateDTO(BaseModel):
    id: str
    name: str
    subject: str
    html_content: str
    plain_text: Optional[str] = None
    external_id: Optional[str] = None

class CampaignMessageDTO(BaseModel):
    id: str
    send_day: int
    message_template: MessageTemplateDTO
    sender: SenderDTO
    target_channel: str

class AddCampaignMessageDTO(BaseModel):
    subject: str
    send_day: int
    template: str
    target_channel: str
    sender_id: str

class CampaignDTO(BaseModel):
    id: str
    name: str
    stage_type: str
    cooldown_days_after_send: int
    description: str
    status: str
    effort_type: str
    messages: List[CampaignMessageDTO]
    created_at: Optional[str] = None
    last_updated: Optional[str] = None

class AddCampaignDTO(BaseModel):
    name: str
    stage_type: str
    cooldown_days_after_send: int
    description: str
    status: str
    effort_type: str
    messages: List[AddCampaignMessageDTO]


class StartCampaignDTO(BaseModel):
    campaign_id: str
    contacts: List[SaveCampaignContactDTO]

class StageType(str, Enum):
    FOLLOW_UP = "FOLLOW_UP"
    ENROLLMENT = "ENROLLMENT"

class CampaignStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
