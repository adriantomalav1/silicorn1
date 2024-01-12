import json
from typing import List
from fastapi import APIRouter, Depends, Response, File, UploadFile
from io import StringIO
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import OAuth2PasswordRequestForm

from app.DTOs.CampaignDTO import AddCampaignDTO, CampaignDTO, StartCampaignDTO
from app.DTOs.SenderDTO import AddSenderDTO, SenderDTO
from app.exceptions.MessageExceptions import MessageNotFoundException, MissingVariablesError
from app.models.models import User
from app.services.MessageTemplateService import MessageTemplateService

from app.services.SendgridService import SendgridService
from app.services.AuthService import AuthService
from app.services.CampaignService import CampaignService
from app.services.SendersService import SenderService

import pandas as pd
import numpy as np

router = APIRouter()

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        print(obj)
        if isinstance(obj, float):
            if np.isnan(obj):
                return None  # Convert NaN to None (which will be converted to null in JSON)
            if np.isinf(obj):
                return str(obj)  # Convert to a string representation of inf or -inf
            else:
                return None
        else:
            return None
        return super().default(obj)

@router.post("/login", tags=["Authentication"])
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    token = AuthService.login(form_data.username, form_data.password)
    return {
        "access_token": token,
        "token_type": "bearer"
    }

@router.post("/register", tags=["Authentication"])
def register(form_data: OAuth2PasswordRequestForm = Depends()):
    AuthService.register(form_data.username, form_data.password)
    return {
        "message": "User registered successfully"
    }

@router.get("/users/me", tags=["User"])
def user(user: User = Depends(AuthService.get_current_user)):
    return {"message": f"Hello, {user.email}"}

@router.post("/campaigns", tags=["Campaign"], response_model=CampaignDTO)
def create_campaign(form_data: AddCampaignDTO):
    campaign = CampaignService.create_campaign(form_data)
    return campaign


@router.get("/campaigns", tags=["Campaign"], response_model=List[CampaignDTO])
def get_campaigns():
    campaigns = CampaignService.get_all_campaigns()
    return campaigns

@router.get("/senders", tags=["Sender"], response_model=List[SenderDTO])
def get_senders():
    senders = SenderService.get_all_senders()
    return senders

@router.post("/senders", tags=["Sender"], response_model=SenderDTO)
def add_sender(form_data: AddSenderDTO):
    senders = SenderService.add(form_data)
    return senders

@router.get("/campaigns/{id}", tags=["Campaign"], response_model=CampaignDTO)
def get_campaign(id: str):
    senders = CampaignService.find_by_id(id)
    return senders

@router.post("/campaign-message/{id}", tags=["Campaign"])
def get_customized_html(id:str, vars_dict: dict):
    try:
        return HTMLResponse(content=CampaignService.render_template(id, vars_dict))
    except MissingVariablesError as e:
        return { "error": e }

@router.post("/campaigns/start", tags=["Campaign"])
def start_campaign(body: StartCampaignDTO):
    try:
        campaign_started = CampaignService.start_campaign(body.campaign_id, body.contacts)
        if campaign_started:
            return { "message": f"Campaign {body.campaign_id} scheduled for {len(body.contacts)} contact(s)." }
        else:
            return Response(status_code=500, content="Internal Server Error")
    except Exception as e:
        return Response(status_code=500, content=str(e))

@router.post("/campaigns/follow-up/{count}", tags=["Campaign"])
def start_follow_up_campaigns(count: int):
    CampaignService.start_follow_up_campaigns(count)
    return Response(status_code=200, content="Follow up campaigns started")


@router.post('/webhooks/sendgrid-events', tags=['Webhooks'])
def handle_sendgrid_event(data: List[dict]):
    try:
        for event in data:
            event = SendgridService.handle_sendgrid_events(event)
        return Response(status_code=200, content="Event processed successfully")
    except MessageNotFoundException as e:
        return Response(status_code=404, content=e.message)
    except Exception as e:
        return Response(status_code=500, content="Internal Server Error")

@router.post('/sendgrid/read_csv', tags=['Sendgrid'])
async def read_data_from_csv(file: UploadFile = File(...)):
    contents = await file.read()
    string_io = StringIO(contents.decode("utf-8"))
    df = pd.read_csv(string_io)
    df.fillna(0, inplace=True)
    return df.to_dict(orient="records")

@router.post('/sendgrid/add_or_update_template', tags=['Sendgrid'])
def add_or_update_template(template_external_id: str):
    template_id = MessageTemplateService.add_or_update_from_sendgrid(template_external_id)
    return Response(status_code=200, content=f"Template {template_id} added or updated successfully")
