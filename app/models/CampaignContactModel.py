from datetime import date, time, timedelta, datetime
from typing import List, Union

from app.DTOs.ContactDTO import CampaignContactDTO, ContactDTO
from app.DTOs.MessageDTO import MessageStatus
from app.exceptions.MessageExceptions import CampaignNotFoundException
from app.models.models import Campaign, CampaignContact, CampaignMessage, CampaignContactMessage, Contact
from conf.database import session_maker
from app.utils.hashids import *


class CampaignContactModel:

    @classmethod
    def add_all(cls, id: int, contacts: List[CampaignContactDTO]) -> bool:
        session = session_maker()
        campaign = session.query(Campaign).filter(Campaign.id==id).first()
        session.close()

        if campaign:
            for c in contacts:
                cls.assign_campaign_to_contact(campaign, c.contact, c.context)
            return True
        else:
            raise CampaignNotFoundException(hash_id(id))

    @classmethod
    def assign_campaign_to_contact(cls, campaign: Campaign, contact: ContactDTO, context: dict):
        try:
            session = session_maker()
            contact_id = unhash_id(contact.id)
            campaign_messages = session.query(CampaignMessage).filter(CampaignMessage.campaign_id==campaign.id).all()
            contact = session.query(Contact).filter(Contact.id==contact_id).first()
            if contact:
                current_date = date.today()
                contact.locked_until = current_date + timedelta(days=campaign.cooldown_days_after_send)
                new_campaign_contact = CampaignContact(
                    campaign_id = campaign.id,
                    contact_id = contact_id,
                    context = context
                )
                session.add(new_campaign_contact)
                session.commit()

            for campaign_message in campaign_messages:
                send_at = calculate_send_day(campaign_message.send_day)
                new_campaign_contact_message = CampaignContactMessage(
                    campaign_contact_id = new_campaign_contact.id,
                    campaign_message_id = campaign_message.id,
                    external_message_id = None,
                    send_at = datetime.combine(send_at, time()),
                    sent_at = None,
                    status = MessageStatus.SCHEDULED
                )
                session.add(new_campaign_contact_message)
            session.commit()
        except Exception as e:
            session.rollback()
            print(e)
            raise e
        finally:
            session.rollback()
            session.close()

def calculate_send_day(num_days: int) -> date:
    current_date = date.today()
    send_date = current_date + timedelta(days=num_days)
    if (send_date.weekday() == 5): # if send date is saturday send on next monday
        send_date += timedelta(days=2)
    elif (send_date.weekday() == 6): # if send date is sunday send on next monday
        send_date += timedelta(days=1)
    return send_date
