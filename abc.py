from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
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
    entry: List[dict] = []

@app.get("/")
def read_root():
    return Response(content="FB Bot Messenger API")

@app.get("/webhook")
def verifyHook(req: Request, res: Response):
    mode = req.query_params.get('hub.mode')
    token = req.query_params.get('hub.verify_token')
    challenge = req.query_params.get('hub.challenge')
    if(mode and token):
        if (mode == "subscribe" and token == os.environ['AUTH_TOKEN']):
            print('Verified request.')
            return Response(content=challenge, status_code=200)
        else:
            return Response(content="Cannot authenticate", status_code=401)
    return Response(content="Parameters not found.", status_code=400)

async def sendMessageToFlaskApp(pdf: str, questions: List[str]):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            'http://localhost:5000/',  # URL of the Flask app
            json={"pdf": pdf, "questions": questions},
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()

@app.post('/webhook')
async def handleWebhook(data: WebhookRequestData):
    print("Event received.")
    print(f"Received data: {data}")

    if data.object == "page":
        for entry in data.entry:
            messaging_events = entry.get("messaging", [])
            for event in messaging_events:
                message = event.get("message", {})
                sender = event.get("sender", {})
                sender_id = sender.get("id")

                if sender_id:
                    if sender_id == os.environ['SELF_ID']:
                        print("Received event for self message. Returning status 200.")
                        return Response(content="success", status_code=200)
                    print(sender_id, message, event)
                    flask_response = await sendMessageToFlaskApp(pdf="example_pdf", questions=[message.get("text", "")])
                    print(flask_response)
                else:
                    print("Sender ID not found in event:", event)

    return Response(content="success", status_code=200)
