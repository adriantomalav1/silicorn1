class MissingVariablesError(Exception):
    def __init__(self, missing_variables):
        self.missing_variables = missing_variables
        super().__init__(f"Missing variables: {', '.join(missing_variables)}")
class NotificationWithoutTargetException(Exception):
    def __init__(self, message="Notification targets are empty"):
        self.message = message
        super().__init__(self.message)

class TemplateNotFoundException(Exception):
    def __init__(self, template_name: str):
        self.message = f"Template {template_name} not found"
        super().__init__(self.message)

class CampaignNotFoundException(Exception):
    def __init__(self, campaign_id: str):
        self.message = f"Campaign {campaign_id} not found"
        super().__init__(self.message)

class MessageNotFoundException(Exception):
    def __init__(self, status_code: int, message_external_id: str):
        self.status_code = status_code
        self.message = f"Message {message_external_id} not found"
        super().__init__(404, self.message)
