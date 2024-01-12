from typing import Union
from app.models.models import MessageTemplate
from conf.database import session_maker

class MessageTemplateModel:
    @staticmethod
    def add_or_update_from_sendgrid_template(sendgrid_template: dict) -> int:
        template_external_id: str = sendgrid_template.get("id")

        session = session_maker()
        template = session.query(MessageTemplate).filter(MessageTemplate.external_id == template_external_id).first()

        versions = sendgrid_template.get("versions")
        if len(versions) > 0:
            active_template = next((d for d in versions if d['active']), None)

            if template:
                template.html_content = active_template.get("html_content")
                template.subject = active_template.get("subject")
                template.plain_text = active_template.get("plain_content")
            else:
                new_template = MessageTemplate(
                    name = sendgrid_template.get("name"),
                    subject = active_template.get("subject"),
                    external_id = sendgrid_template.get("id"),
                    html_content = active_template.get("html_content"),
                    plain_text = active_template.get("plain_content")
                )
                session.add(new_template)
            session.commit()
        template_id = new_template.id

        session.close()
        return template_id