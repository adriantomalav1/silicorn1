from random import randint
from typing import List
from app.DTOs.CampaignDTO import AddCampaignDTO, CampaignDTO, StageType
from app.DTOs.ContactDTO import CampaignContactDTO, SaveCampaignContactDTO
from app.exceptions.MessageExceptions import MissingVariablesError
from app.models.CampaignContactModel import CampaignContactModel
from app.models.CampaignModel import CampaignModel, campaign_message_DTO_builder
from app.models.ContactModel import ContactModel, build_contact_DTO
from app.models.SenderModel import sender_DTO_builder
from app.utils.hashids import *

class CampaignService:

    @staticmethod
    def get_all_campaigns() -> CampaignDTO:
        return CampaignModel.get_campaigns()

    @staticmethod
    def create_campaign(form_data: AddCampaignDTO):
        campaign = CampaignModel.add_campaign(form_data)
        return campaign

    @staticmethod
    def render_template(message_id: str, vars: dict):
        def customize_string(base_string, vars_dict):
            def replace_placeholder(match):
                key = match.group(1)
                if key not in vars_dict:
                    missing_variables.append(key)
                    return match.group(0)
                return str(vars_dict[key])

            import re
            missing_variables = []
            pattern = r"\{\{(\w+)\}\}"
            customized_string = re.sub(pattern, replace_placeholder, base_string)

            if missing_variables:
                raise MissingVariablesError(missing_variables)

            return customized_string

        campaign_message = CampaignModel.get_message(unhash_id(message_id))

        base_string = campaign_message.message_template.html_content
        result = customize_string(base_string, vars)

        return result

    @staticmethod
    def find_by_id(id: str) -> CampaignDTO:
        return CampaignModel.find_by_id(unhash_id(id))

    @staticmethod
    def start_campaign(id: str, contacts: List[SaveCampaignContactDTO]) -> bool:
        updated_contacts: List[CampaignContactDTO] = []
        for contact in contacts:
            updated_contacts.append(
                CampaignContactDTO(
                    contact=ContactModel.add_or_update_by_email(
                        contact.contact.email, contact.contact
                    ), context=contact.context
                )
            )

        campaign_contacts_added = CampaignContactModel.add_all(unhash_id(id), updated_contacts)
        return campaign_contacts_added

    @staticmethod
    def start_follow_up_campaigns(count: int):
        target_contacts = ContactModel.get_top_available_contacts(count)
        avaiable_follow_up_campaigns = CampaignModel.get_avaiable_campaigns_by_stage_type(StageType.FOLLOW_UP)
        for contact in target_contacts:
            contact = build_contact_DTO(contact)
            CampaignContactModel.assign_campaign_to_contact(avaiable_follow_up_campaigns[randint(0, len(avaiable_follow_up_campaigns) - 1)], contact, {})
