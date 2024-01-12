from typing import List, Union
from sqlalchemy import create_engine
from app.DTOs.SenderDTO import AddSenderDTO, SenderDTO
from app.utils.hashids import *
from conf.database import session_maker
from app.models.models import Sender


class SenderModel:

    @staticmethod
    def get_senders() -> List[Sender]:
        session = session_maker()
        senders = session.query(Sender).all()
        senders = multiple_senders_DTO_builder(senders)
        session.close()
        return senders

    @staticmethod
    def add(sender: AddSenderDTO) -> SenderDTO:
        session = session_maker()
        new_sender = Sender(
            name = sender.name,
            email = sender.email,
            domain = sender.domain,
            variables = sender.variables
        )
        session.add(new_sender)
        session.commit()
        new_sender = sender_DTO_builder(new_sender)
        session.close()
        return new_sender


def multiple_senders_DTO_builder(senders: List[Sender]) -> List[SenderDTO]:
    senders_list: List[SenderDTO] = []
    for sender in senders:
        senders_list.append(sender_DTO_builder(sender))

    return senders_list

def sender_DTO_builder(sender: Sender) -> SenderDTO:
    return SenderDTO(
        id = hash_id(sender.id),
        name = sender.name,
        email = sender.email,
        domain = sender.domain,
        variables = sender.variables
    )
