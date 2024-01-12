import asyncio
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.DTOs.MessageDTO import MessageStatus
from app.models.models import CampaignContactMessage
from app.services.EmailService import EmailService

from conf.database import session_maker

async def jobs():
    while True:
        loop = asyncio.get_event_loop()
        loop.create_task(periodic_job())
        await asyncio.sleep(10)

async def periodic_job():
    session = session_maker()

    current_datetime = datetime.now()
    scheduled_messages = session.query(CampaignContactMessage).filter(
            and_(
                CampaignContactMessage.status == MessageStatus.SCHEDULED,
                CampaignContactMessage.send_at <= current_datetime,
                CampaignContactMessage.send_at > current_datetime - timedelta(days=1)
            )
        ).order_by(CampaignContactMessage.id.desc()).limit(100).all()

    for msg in scheduled_messages:
        msg.status = MessageStatus.SENDING

    session.commit()
    email_send_tasks = []
    for msg in scheduled_messages:
        task = asyncio.create_task(send_email(msg, session))
        email_send_tasks.append(task)

    await asyncio.gather(*email_send_tasks)
    session.close()

async def send_email(msg: CampaignContactMessage, session: Session):
    try:
        msg_sent = await EmailService.send(msg)
        if msg_sent:
            msg.status = MessageStatus.DELIVERED
            msg.sent_at = datetime.now()
            msg.external_message_id = msg_sent
    except Exception as e:
        print(e)
        msg.status = MessageStatus.ERROR
    finally:
        session.commit()
