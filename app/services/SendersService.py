from typing import List
from app.DTOs.SenderDTO import AddSenderDTO, SenderDTO
from app.models.SenderModel import SenderModel

class SenderService:

    @staticmethod
    def get_all_senders() ->  List[SenderDTO]:
        return SenderModel.get_senders()

    @staticmethod
    def add(sender: AddSenderDTO) -> SenderDTO:
        return SenderModel.add(sender)
