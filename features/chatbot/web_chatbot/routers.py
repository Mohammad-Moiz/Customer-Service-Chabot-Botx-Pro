"""_summary_

Returns:
    _type_: _description_
"""

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from configuration import constants
from db.db_setup import get_db
from features.chatbot.web_chatbot.bot_v4 import chat_function
from features.chatbot.web_chatbot.dependency import (
    get_chat,
    upload_business_details,
    upload_chat,
    get_chats_data
)
from features.chatbot.web_chatbot.schema import Chat, ChatInput
from utilities.module_utils import get_user_role

chat_bot = APIRouter()


@chat_bot.post("/chat_bot/process_input", tags=["Chat_Bot"])
def process_input(chat_input: ChatInput, db: Session = Depends(get_db)) -> dict:
    """_summary_

    Args:
        chat_input (ChatInput): _description_

    Returns:
        _type_: _description_
    """
    # Process user input and get AI response
    result = chat_function(
        db=db,
        user_id=chat_input.user_id,
        business_id=chat_input.business_id,
        user_input=chat_input.user_input,
    )
    return {"status": "success", "ai_response": result}


@chat_bot.post("/chat_bot/chat_history", tags=["Chat_Bot"])
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
        user_id=chat.user_id,
        vendor_id=chat.vendor_id,
    )


@chat_bot.post("/chat_bot/upload_chat", tags=["Chat_Bot"])
async def create_upload_chat(
    vendor_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if get_user_role(db=db, user_id=vendor_id) != "VENDOR":
        raise HTTPException(
            status_code=400,
            detail={
                "status": False,
                "message": constants.VENDOR_NOT_FOUND,
            },
        )
    return upload_chat(vendor_id=vendor_id, file=file)


@chat_bot.post("/chat_bot/upload_business_detail", tags=["Chat_Bot"])
async def create_upload_business_details(
    vendor_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    # try:
    if get_user_role(db=db, user_id=vendor_id) != "VENDOR":
        raise HTTPException(
            status_code=400,
            detail={
                "status": False,
                "message": constants.VENDOR_NOT_FOUND,
            },
        )
    return upload_business_details(vendor_id=vendor_id, file=file)


# except Exception as e:
#     # Handle other exceptions
#     raise HTTPException(
#         status_code=400,
#         detail={
#             "status": False,
#             "message": constants.SOMETHING_WRONG,
#         },
#     ) from e



@chat_bot.get("/chat_bot/get_chats", tags=["Chat_Bot"])
async def get_user_list(db: Session = Depends(get_db)) -> dict:
    chats = get_chats_data(db=db)
    return chats


#------------------------------------------------------------------

# from pydantic import BaseModel
# from typing import Optional
# from fastapi import FastAPI, HTTPException, Request, Response



# WEBHOOK_VERIFY_TOKEN = "12345"
# GRAPH_API_TOKEN = "EABpxzwZBj7ZCkBOwVAmcxIKh8YitkBCyYZASLSr4SrgfyfZCiZBTSO8HT73kMJquuDrnP64VKhEB78OIEVqdrWZAa3n5BOaRjfcUVt3E8QN1gCVShytgIiefxXbibBVBY6ZA3FS8xeXTCdWBORd4l421ZAF8z30mGzRZC7h9IsbcpRjhk7V0j8hJsPkZASZAZB4QNIxO1NBtZBAuejwQ3TVEwot6r3WUjTAZDZD"
# PORT = 8000
# RECIPIENT_WAID="+923483250426"




# class WebhookPayload(BaseModel):
#     object: str
#     entry: list[dict]



# @chat_bot.post('/webhook',tags=["Chat_Bot"])
# async def webhook(payload: WebhookPayload, response: Response, db: Session = Depends(get_db)):
#     message_data = payload.entry[0].get('changes', [{}])[0].get('value', {}).get('messages', [{}])[0]
#     print(message_data)

#     phone_number = message_data.get('from')
#     # timestamp = message_data.get('timestamp')
#     try:
#         user_input = message_data.get('text').get('body')

#         result = chat_function(
#             db=db,
#             user_id='2',
#             business_id='1',
#             user_input=user_input,
#         )
#         print(result)

#         send_text_message(RECIPIENT_WAID, result)


#     except:
#         user_input=''
        
   
#     # return {"status": "success", "ai_response": result}


#     # send_text_message(RECIPIENT_WAID, 'hi')



  


#     # print(text)
#     # print(phone_number)

#     # # Store the conversation
#     # conversation.append({'from': RECIPIENT_WAID, 'text': text})  # assuming the recipient is responding
#     # print(f"Recipient: {text}")

#     # # Process user's message
#     # user_input = input("Enter your message : ")
#     # if user_input.lower() == 'q':
#     #     return {'status': 'Conversation ended'}

#     # # Send the user's message
#     # send_text_message(RECIPIENT_WAID, user_input)

#     # # Store the conversation
#     # conversation.append({'from': 'User', 'text': user_input})
#     # print(f"You: {user_input}")

#     return {'status': 'success'}


# @chat_bot.get('/webhook',tags=["Chat_Bot"])
# async def verify_webhook(request: Request, mode: Optional[str] = None, token: Optional[str] = None, challenge: Optional[str] = None):
#     mode = request.query_params.get('hub.mode')
#     token = request.query_params.get('hub.verify_token')
#     challenge = request.query_params.get('hub.challenge')
#     # Check the mode and token sent are correct
#     if mode == 'subscribe' and token == WEBHOOK_VERIFY_TOKEN:
#         # Respond with challenge token from the request
#         print("Webhook verified successfully!")
#         return Response(content=challenge, status_code=200)
#     else:
#         # Respond with '403 Forbidden' if verify tokens do not match
#         raise HTTPException(status_code=403, detail="Verification failed")



    

# import requests


# def send_text_message(recipient, text):

#     ACCESS_TOKEN = 'EABpxzwZBj7ZCkBO6czpwuDnHMEm5NH5WJyzzZCI6dUH99kcg06D8xxVfRwPTOLwpPZCIZAS2MReUZCwQMB1U9tx5hQuYjsQlKugoaQexcY5uXB5todndjktcIjyQipBHVdX2yZAVKrJUn7pw81kTv85By0ZCU8jTN55R7a1RQmLAtuZBfjrdCDMtxtZB95WUAzxM2XixKibURgdLVuekNYioSpG5rACWgZD'
#     RECIPIENT_WAID = '+923483250426'
#     PHONE_NUMBER_ID = '284426971410101'
#     VERSION = 'v19.0'


#     url = f"https://graph.facebook.com/{VERSION}/{PHONE_NUMBER_ID}/messages"
#     headers = {
#         "Authorization": "Bearer " + ACCESS_TOKEN,
#         "Content-Type": "application/json",
#     }
#     data = {
#         "messaging_product": "whatsapp",
#         "to": recipient,
#         "type": "text",
#         "text": {"preview_url": False, "body": text},
#     }
#     response = requests.post(url, headers=headers, json=data)
#     return response


# @chat_bot.get('/send_msg',tags=["Chat_Bot"])
# async def verify_webhook():
#     RECIPIENT_WAID = '+923483250426'
#     send_text_message(RECIPIENT_WAID, 'hi')

#     return 0
