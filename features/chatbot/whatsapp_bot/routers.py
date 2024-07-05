"""_summary_

Returns:
    _type_: _description_
"""

from fastapi import APIRouter, Depends, File, HTTPException, Request, Response
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from features.chatbot.whatsapp_bot.schema import AddWhatsappUser

from configuration import configure
from db.db_setup import get_db
from features.chatbot.whatsapp_bot.bot_v4 import chat_function
from features.chatbot.whatsapp_bot.dependency import (
    get_chat,
    upload_business_details,
    upload_chat,
    get_chats_data,
    add_whatsapp_user,
    get_vendor_id_by_whatsapp,
)
from features.chatbot.whatsapp_bot.schema import Chat, ChatInput
from utilities.module_utils import get_user_role
import os
whatsapp_chatbot = APIRouter()


@whatsapp_chatbot.post(
    "/whatsapp_chatbot/whataspp_process_input", tags=["Whatsapp_chatbot"]
)
def process_input(chat_input: ChatInput, db: Session = Depends(get_db)) -> dict:
    """_summary_

    Args:
        chat_input (ChatInput): _description_

    Returns:
        _type_: _description_
    """
    vendor_id = get_vendor_id_by_whatsapp(db, chat_input.business_id)
    vendor_id = str(vendor_id)
    add_whatsapp_user(db, chat_input.user_no, vendor_id)
    # Process user input and get AI response
    result = chat_function(
        db=db,
        user_no=chat_input.user_no,
        business_id=vendor_id,
        user_input=chat_input.user_input,
    )
    return {"status": "success", "ai_response": result}


@whatsapp_chatbot.post(
    "/whatsapp_chatbot/whatsapp_chat_history", tags=["Whatsapp_chatbot"]
)
def chat_data(chat: Chat, db: Session = Depends(get_db)) -> dict:
    """_summary_

    Args:
        chat_input (ChatInput): _description_

    Returns:
        _type_: _description_
    """
    # Process user input and get AI response
    return get_chat(
        db=db,
        user_no=chat.user_no,
        vendor_id=chat.vendor_id,
    )


@whatsapp_chatbot.get("/whatsapp_chatbot/whatsapp_get_chats", tags=["Whatsapp_chatbot"])
async def get_user_list(db: Session = Depends(get_db)) -> dict:
    chats = get_chats_data(db=db)
    return chats


WEBHOOK_VERIFY_TOKEN = configure.webhook_verify_token
GRAPH_API_TOKEN = configure.whatsapp_access_token
PORT = configure.port
PHONE_NUMBER_ID = configure.phone_number_id
VERSION = configure.meta_version



class WebhookPayload(BaseModel):
    object: str
    entry: list[dict]



@whatsapp_chatbot.post('/webhook',tags=["Whatsapp_chatbot"])
async def webhook(payload: WebhookPayload, response: Response, db: Session = Depends(get_db)):
    ACCESS_TOKEN = configure.FB_graph_token

    business_phone_num=payload.entry[0].get('changes')[0].get('value').get('metadata').get('display_phone_number')
    message_data = payload.entry[0].get('changes', [{}])[0].get('value', {}).get('messages', [{}])[0]
    print(message_data)
    # print(display_phone_number)   

    try:
        if message_data.get('type') == 'text':
            user_input = message_data.get('text').get('body')
            print(user_input)
            phone_number = message_data.get('from')
            print(phone_number)
            timestamp = message_data.get('timestamp')
            print(timestamp)

            vendor_id = get_vendor_id_by_whatsapp(db, business_phone_num)
            vendor_id = str(vendor_id)
    
            add_whatsapp_user(db, phone_number, business_phone_num)

            result = chat_function(
                db=db,
                user_no=phone_number,
                business_id=vendor_id,
                user_input=user_input,
            )
            print(result)
            path='./images/pexels-pixabay-60597.jpg'
            # print(phone_number)
            send_text_message(phone_number, result)
            # send_image_message(phone_number,path)

        if message_data.get('type') == 'audio':
            vendor_id = get_vendor_id_by_whatsapp(db, business_phone_num)
            vendor_id = str(vendor_id)

            AUDIO_ID = message_data.get('audio').get('id')
            print(AUDIO_ID)
            phone_number = message_data.get('from')
            print(phone_number)
            timestamp = message_data.get('timestamp')
            print(timestamp)
            print("An audio message has been received from the recipient.")
            headers = {
                "Authorization": "Bearer " + ACCESS_TOKEN,
            }
            response = requests.get(f'https://graph.facebook.com/{VERSION}/{AUDIO_ID}', headers=headers)
            if response.status_code == 200:
                audio = response.content
                voice_path = "features/chatbot/voices/voices_db"
                save_path = f"{voice_path}/received_{phone_number}_{vendor_id}_{timestamp}_{AUDIO_ID}.ogg"
                with open(save_path, "wb") as audio_file:
                    audio_file.write(audio)
                    print(f"Audio downloaded and saved successfully to: {save_path}")
            else:
                print(f"Error downloading audio: {response.text}")
    
            add_whatsapp_user(db, phone_number, business_phone_num)


    except Exception as e: 
        print(e)
        user_input=''
        
    return {'status': 'success'}

@whatsapp_chatbot.get('/webhook',tags=["whatsapp_chatbot"])
async def verify_webhook(request: Request, mode: Optional[str] = None, token: Optional[str] = None, challenge: Optional[str] = None):
    mode = request.query_params.get('hub.mode')
    token = request.query_params.get('hub.verify_token')
    challenge = request.query_params.get('hub.challenge')
    # Check the mode and token sent are correct
    if mode == 'subscribe' and token == WEBHOOK_VERIFY_TOKEN:
        # Respond with challenge token from the request
        print("Webhook verified successfully!")
        return Response(content=challenge, status_code=200)
    else:
        # Respond with '403 Forbidden' if verify tokens do not match
        raise HTTPException(status_code=403, detail="Verification failed")



import requests

def send_text_message(recipient, text):

    ACCESS_TOKEN = configure.FB_graph_token

    url = f"https://graph.facebook.com/{VERSION}/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": "Bearer " + ACCESS_TOKEN,
        "Content-Type": "application/json",
    }
    data = {
        "messaging_product": "whatsapp",
        "to": recipient,
        "type": "text",
        "text": {"preview_url": False, "body": text},
    }
    response = requests.post(url, headers=headers, json=data)
    return response



def send_image_message(recipient, image_path):
    ACCESS_TOKEN = configure.FB_graph_token
  
    url = f"https://graph.facebook.com/{VERSION}/{PHONE_NUMBER_ID}/media"
    headers = {
        "Authorization": "Bearer " + ACCESS_TOKEN
    }
    params = {
    'messaging_product': 'whatsapp'
    }

    with open(image_path, "rb") as image_file:
       
        image_data = image_file.read()

    files = {
        "file": (
            "image.jpeg",
            image_data,
            "image/jpeg"
        )
    }
    print(f"files: {files}")
    response = requests.post(url, headers=headers, files=files, params=params)
    print(response)

    if response.status_code == 200:
        # Parse the response to get the media ID
        response_json = response.json()
        media_id = response_json.get("id")
        print(media_id)

        if media_id:
            url = f"https://graph.facebook.com/{VERSION}/{PHONE_NUMBER_ID}/messages"
            message_data = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": recipient,
                "type": "image",
                "image": {"id": media_id},
                # "image": {"id": "270739389424306"}
            }
            headers = {
                "Authorization": "Bearer " + ACCESS_TOKEN,
                "Content-Type": "application/json",
            }
            message_response = requests.post(url=url, headers=headers, json=message_data)
            # print(message_response)

            if message_response.status_code == 200:
                print(f"Image sent successfully. Media ID: {media_id}")
                return media_id  # Return the media ID for potential tracking
            else:
                print(f"Error sending image message: {message_response.text}")
                return None 
        else:
            print(f"Error getting media ID from upload response: {response.text}")
            return None 
    else:
        print(f"Error uploading image: {response.text}")
        return None 
    

def send_audio_message(recipient, audio_path):
    ACCESS_TOKEN = configure.FB_graph_token

    url = f"https://graph.facebook.com/{VERSION}/{PHONE_NUMBER_ID}/media"
    headers = {
        "Authorization": "Bearer " + ACCESS_TOKEN
    }
    params = {
        'messaging_product': 'whatsapp'
    }

    with open(audio_path, "rb") as audio_file:
        audio_data = audio_file.read()

    files = {
        "file": (
            "audio.ogg",  # Assuming the audio format is ogg
            audio_data,
            "audio/ogg"
        )
    }

    response = requests.post(url, headers=headers, files=files, params=params)

    if response.status_code == 200:
        # Parse the response to get the media ID
        response_json = response.json()
        media_id = response_json.get("id")
        print(media_id)

        if media_id:
            url = f"https://graph.facebook.com/{VERSION}/{PHONE_NUMBER_ID}/messages"
            message_data = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": recipient,
                "type": "audio",
                "audio": {"id": media_id},
            }
            headers = {
                "Authorization": "Bearer " + ACCESS_TOKEN,
                "Content-Type": "application/json",
            }
            message_response = requests.post(url=url, headers=headers, json=message_data)

            if message_response.status_code == 200:
                print(f"Audio sent successfully. Media ID: {media_id}")
                return media_id  # Return the media ID for potential tracking
            else:
                print(f"Error sending audio message: {message_response.text}")
                return None
        else:
            print(f"Error getting media ID from upload response: {response.text}")
            return None
    else:
        print(f"Error uploading audio: {response.text}")
        return None



# @chat_bot.get('/send_msg',tags=["Chat_Bot"])
# async def verify_webhook():
#     RECIPIENT_WAID = '+923483250426'
#     send_text_message(RECIPIENT_WAID, 'hi')

#     return 0