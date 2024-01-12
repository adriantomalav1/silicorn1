from app.DTOs.MessageDTO import AvailableChannels
from app.models.SenderModel import sender_DTO_builder

from app.models.models import CampaignContactMessage
from app.services.CampaignService import CampaignService
from app.services.SendgridService import SendgridService
from app.utils.hashids import hash_id


class EmailService:

    @staticmethod
    async def send(msg: CampaignContactMessage) -> str:
        if msg.campaign_message.target_channel == AvailableChannels.EMAIL:
            sendgrid_response = SendgridService.send(
                sender=sender_DTO_builder(msg.campaign_message.sender),
                recipient = msg.campaign_contact.contact.email,
                subject = msg.campaign_message.message_template.subject,
                html_content = CampaignService.render_template(hash_id(msg.campaign_message.id), msg.campaign_contact.context)
            )
            if sendgrid_response.status_code == 202:
                return sendgrid_response.headers["X-Message-Id"]
