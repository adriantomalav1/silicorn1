from app.models.MessageTemplateModel import MessageTemplateModel
from app.services.SendgridService import SendgridService
from app.utils.hashids import hash_id

class MessageTemplateService:
    @staticmethod
    def add_or_update_from_sendgrid(template_external_id: str) -> str:
        template = SendgridService.get_template(template_external_id)
        template_id = MessageTemplateModel.add_or_update_from_sendgrid_template(template)
        return hash_id(template_id)