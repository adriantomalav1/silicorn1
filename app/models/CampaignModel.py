from typing import List, Union

from sqlalchemy import and_
from app.DTOs.CampaignDTO import AddCampaignDTO, CampaignDTO, CampaignMessageDTO, CampaignStatus, MessageTemplateDTO, StageType
from app.exceptions.MessageExceptions import CampaignNotFoundException
from app.models.SenderModel import sender_DTO_builder
from app.utils.hashids import *
from conf.database import session_maker
from app.models.models import Campaign, CampaignMessage, MessageTemplate, Sender


class CampaignModel:

    @classmethod
    def get_campaigns(cls) -> List[CampaignDTO]:
        session = session_maker()
        all_campaigns = session.query(Campaign).all()
        result: List[CampaignDTO] = []

        for c in all_campaigns:
            messages = session.query(CampaignMessage).filter(CampaignMessage.id==c.id).join(Sender).all()
            campaign = campaignDTOBuilder(c, messages)
            result.append(campaign)

        session.close()
        return result

    @classmethod
    def add_campaign(cls, campaign_data: AddCampaignDTO) -> CampaignDTO:
        try:
            session = session_maker()
            new_campaign = Campaign(
                name=campaign_data.name,
                status=campaign_data.status,
                effort_type=campaign_data.effort_type,
                stage_type=campaign_data.stage_type,
                description=campaign_data.description,
                cooldown_days_after_send=campaign_data.cooldown_days_after_send,
            )
            session.add(new_campaign)

            campaign_messages = []
            for msg in campaign_data.messages:
                sender_id = unhash_id(msg.sender_id)
                sender = session.query(Sender).filter(Sender.id == sender_id).first()

                if sender:
                    new_message_template = MessageTemplate(
                        subject = msg.subject,
                        html_content = msg.template,
                        plain_text = msg.template
                    )
                    session.add(new_message_template)
                    session.commit()

                    new_campaign_message = CampaignMessage(
                        send_day=msg.send_day,
                        target_channel=msg.target_channel
                    )

                    new_campaign_message.campaign_id = new_campaign.id
                    new_campaign_message.sender_id = sender.id
                    new_campaign_message.message_template_id = new_message_template.id
                    campaign_messages.append(new_campaign_message)
                else:
                    raise Exception("Invalid sender id")

            session.add_all(campaign_messages)
            session.commit()
            campaign_created = campaignDTOBuilder(new_campaign, campaign_messages)
            return campaign_created
        except Exception as e:
            session.rollback()
            raise e

    @classmethod
    def find_by_id(cls, id: int) -> CampaignDTO:
        session = session_maker()
        campaign_option = session.query(Campaign).filter(Campaign.id==id).first()

        if campaign_option:
            messages = session.query(CampaignMessage).filter(CampaignMessage.id==campaign_option.id).join(Sender).all()
            campaign = campaignDTOBuilder(campaign_option, messages)
            return campaign
        else:
            raise CampaignNotFoundException(id)

    @classmethod
    def get_message(cls, id: int) -> Union[CampaignMessageDTO, None]:
        session = session_maker()
        campaign_message = session.query(CampaignMessage).filter(CampaignMessage.id==id).first()

        if not campaign_message:
            return None

        campaign_message = campaign_message_DTO_builder(campaign_message)
        session.close()
        return campaign_message

    @classmethod
    def get_avaiable_campaigns_by_stage_type(cls, stage_type: StageType) -> List[Campaign]:
        session = session_maker()
        campaigns = session.query(Campaign).filter(
                and_(
                    Campaign.stage_type == stage_type,
                    Campaign.status == CampaignStatus.APPROVED
                )
            ).all()
        session.close()
        return campaigns

def campaignDTOBuilder(campaign: Campaign, campaign_messages: List[CampaignMessage]) -> CampaignDTO:
    messages_result: List[CampaignMessageDTO] = []

    for m in campaign_messages:
        messages_result.append(campaign_message_DTO_builder(m))

    return CampaignDTO(
        id=hash_id(campaign.id),
        name=campaign.name,
        stage_type=campaign.stage_type,
        cooldown_days_after_send=campaign.cooldown_days_after_send,
        description=campaign.description,
        status=campaign.status,
        effort_type=campaign.effort_type,
        messages=messages_result,
        created_at=str(campaign.created_at),
        last_updated=str(campaign.last_updated)
    )

def campaign_message_DTO_builder(campaign_message: CampaignMessage) -> CampaignMessageDTO:
    return CampaignMessageDTO(
        id=hash_id(campaign_message.id),
        send_day=campaign_message.send_day,
        message_template= messsage_template_DTO_builder(campaign_message.message_template),
        target_channel=campaign_message.target_channel,
        sender=sender_DTO_builder(campaign_message.sender)
    )

def messsage_template_DTO_builder(message_template: MessageTemplate) -> MessageTemplateDTO:
    return MessageTemplateDTO(
        id=hash_id(message_template.id),
        subject=message_template.subject,
        html_content=message_template.html_content
    )
