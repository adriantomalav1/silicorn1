from sqlalchemy import JSON, Boolean, Text, Column, Index, Integer, String, ForeignKey, DateTime, func, Float
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from conf.database import engine


Base = declarative_base()

class BaseModel(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    created_at = Column(DateTime, default=func.now())
    last_updated = Column(DateTime, onupdate=func.now())

class User(BaseModel):
    __tablename__ = "users"
    username = Column(String(255), unique=True, index=True)
    full_name = Column(String(255), unique=False, index=False)
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))
    disabled = Column(Boolean, unique=False, default=False)

class UnprocessedCompany(BaseModel):
    __tablename__ = "unprocessed_companies"

    linkedin = Column(String(255), nullable=True)
    domain = Column(String(255), nullable=True)
    location = Column(String(500), nullable=True)
    name = Column(String(255), nullable=True)
    country = Column(String(255), nullable=True)
    external_id = Column(String(12), unique=True, nullable=False)
    industry = Column(String(255), nullable=True)
    tags = Column(String(2000), nullable=True)
    size = Column(String(255), nullable=True)
    region = Column(String(255), nullable=True)
    sic_definitions = Column(String(2000), nullable=True)
    city = Column(String(255), nullable=True)
    yearly_revenue = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    ceo_id = Column(String(12), nullable=True)
    source = Column(String(25), nullable=True)

class UnprocessedContact(BaseModel):
    __tablename__ = "unprocessed_contacts"

    email = Column(String(255), nullable=True)
    phone = Column(String(255), nullable=True)
    name = Column(String(255), nullable=True)
    linkedin = Column(String(255), nullable=True)
    external_id = Column(String(12), unique=True, nullable=False)
    title = Column(String(255), nullable=True)
    company_external_id = Column(String(12), nullable=True)

class Company(BaseModel):
    __tablename__ = "companies"

    linkedin = Column(String(255), nullable=True)
    domain = Column(String(255), nullable=True)
    location = Column(String(500), nullable=True)
    name = Column(String(255), nullable=True)
    external_id = Column(String(12), unique=True, nullable=True)
    city = Column(String(255), nullable=True)
    yearly_revenue = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    unprocessed_company_id = Column(Integer, ForeignKey("unprocessed_companies.id"), nullable=True)

    unprocessed_company = relationship("UnprocessedCompany")

class Contact(BaseModel):
    __tablename__ = "contacts"

    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=False)
    phone = Column(String(255), nullable=True)
    linkedin = Column(String(255), nullable=True)
    title = Column(String(255), nullable=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    unprocessed_contact_id = Column(Integer, ForeignKey("unprocessed_contacts.id"), nullable=True)
    status = Column(String(20), nullable=False)
    lead_score = Column(Float, nullable=False, default=0.1)
    locked_until = Column(DateTime, nullable=True)

    company = relationship("Company")
    unprocessed_contact = relationship("UnprocessedContact")

    __table_args__ = (
        Index("contact_email_index", email),
        Index("contact_locked_until_index", locked_until),
    )

class Sender(BaseModel):
    __tablename__ = "senders"

    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    domain = Column(String(255), nullable=False)
    variables = Column(JSON, default={})

class Campaign(BaseModel):
    __tablename__ = "campaigns"

    name = Column(String(500), nullable=False)
    status = Column(String(255), nullable=False)
    effort_type = Column(String(50), nullable=False)
    stage_type = Column(String(50), nullable=False)
    description = Column(String(2000), nullable=True)
    cooldown_days_after_send = Column(Integer, default=7)

class CampaignMessage(BaseModel):
    __tablename__ = "campaign_messages"

    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("senders.id"), nullable=False)
    message_template_id = Column(Integer, ForeignKey("message_template.id"), nullable=False)
    target_channel = Column(String(20), nullable=False)
    send_day = Column(Integer, nullable=False)

    campaign = relationship("Campaign")
    sender = relationship("Sender")
    message_template = relationship("MessageTemplate")

class MessageTemplate(BaseModel):
    __tablename__ = "message_template"

    name = Column(String(1000), nullable=False)
    subject = Column(String(1000), nullable=False)
    external_id = Column(String(100), nullable=False)
    html_content = Column(Text)
    plain_text = Column(Text)

class CampaignContact(BaseModel):
    __tablename__ = "campaign_contacts"

    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=False)
    context = Column(JSON, nullable=True)

    campaign = relationship("Campaign")
    contact = relationship("Contact")

class CampaignContactMessage(BaseModel):
    __tablename__ = "campaign_contact_messages"

    campaign_contact_id = Column(Integer, ForeignKey("campaign_contacts.id"), nullable=False)
    campaign_message_id = Column(Integer, ForeignKey("campaign_messages.id"), nullable=False)
    status = Column(String(50), nullable=False)
    send_at = Column(DateTime, nullable=False)
    sent_at = Column(DateTime, nullable=True)
    external_message_id = Column(String(200), nullable=True)
    cancel_reason = Column(String(200), nullable=True)

    campaign_contact = relationship("CampaignContact")
    campaign_message = relationship("CampaignMessage")

    __table_args__ = (
        Index("campaign_contact_message_status_index", status),
        Index("campaign_contact_message_send_at_index", send_at),
        Index("campaign_contact_message_sent_at_index", sent_at),
        Index("campaign_contact_message_external_message_id_index", external_message_id)
    )

class MessageEvent(BaseModel):
    __tablename__ = "message_events"

    campaign_contact_message_id = Column(Integer, ForeignKey("campaign_contact_messages.id"), nullable=False)
    event_type = Column(String(50), nullable=False)
    user_agent = Column(String(400), nullable=True)

    campaign_contact_message = relationship("CampaignContactMessage")

    __table_args__ = (
        Index("message_event_event_type_index", event_type),
    )

class Segment(BaseModel):
    __tablename__ = "segments"

    property = Column(String(255), nullable=False)
    value = Column(String(255), nullable=False)

class ContactSegment(BaseModel):
    __tablename__ = "contact_segments"

    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=False)
    segment_id = Column(Integer, ForeignKey("segments.id"), nullable=False)

    contact = relationship("Contact")
    segment = relationship("Segment")

class CompanySegment(BaseModel):
    __tablename__ = "company_segments"

    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    segment_id = Column(Integer, ForeignKey("segments.id"), nullable=False)

    company = relationship("Company")
    segment = relationship("Segment")

class CampaignSegment(BaseModel):
    __tablename__ = "campaign_segments"

    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    segment_id = Column(Integer, ForeignKey("segments.id"), nullable=False)

    campaign = relationship("Campaign")
    segment = relationship("Segment")

Base.metadata.create_all(bind=engine)
