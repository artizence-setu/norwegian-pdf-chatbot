from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import httpx
import os

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class WebhookRequestData(BaseModel):
    object: str = ""
    entry: List = []


@app.get("/")
def read_root():
    return Response(content="FB Bot Messanger api")


@app.get("/webhook")
def verifyHook(req: Request, res: Response):
    mode = req._query_params.get('hub.mode')
    token = req._query_params.get('hub.verify_token')
    challenge = req._query_params.get('hub.challenge')
    if(mode and token):
        if (mode == "subscribe" and token == os.environ['AUTH_TOKEN']):
            print('Verified request.')
            return Response(content=challenge, status_code=200)
        else:
            return Response(content="Cannot authenticat", status_code=401)
    return Response(content="Parameters not found.", status_code=400)



async def sendMessage(
    page_access_token: str,
    recipient_id: str,
    message_text: str,
    message_type: str = "UPDATE"
    ):
    r = httpx.post(
        "https://graph.facebook.com/v19.0/me/messages",
        params={"access_token": page_access_token},
        headers={"Content-Type": "application/json"},
        json={
            "recipient": {"id": recipient_id},
            "message": {"text": message_text},
            "messaging_type": message_type,
        },
    )
    r.raise_for_status()


@app.post('/webhook')
async def handleWebhook(data : WebhookRequestData):
    print("Event received.")
    if data.object == "page":
        for entry in data.entry:
            messaging_events = [ event for event in entry.get("messaging", []) if event.get("message") ]
            for event in messaging_events:
                message = event.get("message")
                sender_id = event["sender"]["id"]
                if(sender_id == os.environ['SELF_ID']):
                    print("Received event for self message. Returning status 200.")
                    return Response(content="success", status_code=200)
                print(sender_id, message, event)
                await sendMessage(page_access_token=os.environ["ACCESS_TOKEN"],
                                   recipient_id=sender_id,
                                   message_text="Hello world",
                                   message_type="RESPONSE")
    return Response(content="success", status_code=200)