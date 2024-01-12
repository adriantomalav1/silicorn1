import json
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, From
from app.DTOs.CampaignDTO import MessageTemplateDTO
from app.DTOs.ContactDTO import ContactStatus
from app.DTOs.MessageDTO import MessageStatus
from app.DTOs.SenderDTO import SenderDTO
from app.exceptions.MessageExceptions import MessageNotFoundException
from app.models.models import CampaignContactMessage, MessageEvent, MessageTemplate

from conf.config import AUTOMATED_USER_AGENTS, SENDGRID_API_KEY
from conf.database import session_maker

sg = SendGridAPIClient("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")

class SendgridService:
    @staticmethod
    def send(sender: SenderDTO, recipient: str, subject: str, html_content: str):
        message = Mail(
            from_email=From(
                email=sender.email,
                name=sender.name
            ),
            to_emails=recipient,
            subject=subject,
            html_content=html_content
        )
        try:
            response = sg.send(message)
            return response
        except Exception as e:
            raise e

    @staticmethod
    async def create_new_template(message_template: MessageTemplateDTO) -> dict:
        template_id = message_template.id
        data = {
            "template_id": template_id,
            "active": 1,
            "name": message_template.name if message_template.name else "",
            "html_content": message_template.html_content,
            "generate_plain_content": False,
            "subject": message_template.subject,
            "editor": "test",
            "plain_content": message_template.plain_text if message_template.plain_text else ""
        }

        response: dict = await sg.client.templates._(template_id).versions.post(
            request_body=data
        )
        return response.get("body")

    @staticmethod
    def get_template(template_external_id: str):
        template_external_id = "d-727b45cd87274bbca7fe33a2da114681"
        response = sg.client.templates._(template_external_id).get()
        print(response)
        return json.loads(response.body)

    @staticmethod
    def handle_sendgrid_events(event_data: dict):
        event_type = event_data.get("event")
        event_user_agent = event_data.get("useragent")

        message_id = event_data.get("sg_message_id")
        message_id = message_id[:message_id.find('.')]

        session = session_maker()
        message = session.query(CampaignContactMessage).filter(CampaignContactMessage.external_message_id == message_id).first()

        if not message:
            raise MessageNotFoundException(message_id)

        if event_type == "bounce":
            message.status = MessageStatus.BOUNCED
        elif event_type == "deferred":
            pass
        elif event_type == "spamreport":
            message.campaign_contact.contact.status = ContactStatus.BLACKLISTED
        elif event_user_agent not in AUTOMATED_USER_AGENTS:
            if event_type == "open" and message.status != MessageStatus.CLICKED:
                message.status = MessageStatus.OPENED
            elif event_type == "delivered":
                message.status = MessageStatus.DELIVERED
            elif event_type == "click":
                message.status = MessageStatus.CLICKED

        new_message_event = MessageEvent(
            campaign_contact_message_id = message.id,
            event_type = event_type,
            user_agent = event_user_agent
        )
        session.add(new_message_event)

        session.commit()
        session.close()
