from datetime import datetime
from typing import List

from sqlalchemy import or_
from app.DTOs.ContactDTO import ContactDTO, ContactStatus, SaveContactDTO
from app.utils.hashids import *
from conf.database import session_maker
from app.models.models import Contact


class ContactModel:

    @staticmethod
    def add_or_update_by_email(email: str, new_contact = SaveContactDTO) -> Contact:
        session = session_maker()
        contact_option = session.query(Contact).filter(Contact.email==email).first()
        if contact_option:
            contact_option.first_name = new_contact.first_name
            contact_option.last_name = new_contact.last_name
            contact_option.phone = new_contact.phone
            contact = contact_option
        else:
            contact = Contact(
                email = new_contact.email,
                first_name = new_contact.first_name,
                last_name = new_contact.last_name,
                phone = new_contact.phone,
                status = ContactStatus.ACTIVE
            )

        session.add(contact)
        session.commit()
        contact = build_contact_DTO(contact)
        session.close()

        return contact

    @staticmethod
    def get_top_available_contacts(count: int) -> List[Contact]:
        current_date = datetime.now()
        session = session_maker()
        contacts = session.query(Contact).filter(
                or_(
                    Contact.locked_until < current_date,
                    Contact.locked_until == None
                )
            ).order_by(Contact.lead_score.desc()).limit(100).all()
        session.close()
        return contacts

def build_contact_DTO(contact: Contact) -> ContactDTO:
    return ContactDTO(
        id = hash_id(contact.id),
        email = contact.email,
        first_name = contact.first_name,
        last_name = contact.last_name,
        phone = contact.phone,
        status = contact.status
    )
