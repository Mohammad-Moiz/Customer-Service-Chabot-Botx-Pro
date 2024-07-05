import json
from datetime import datetime
from typing import Any

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from configuration import constants
from features.authentication.models import UserModel
from features.chatbot.web_chatbot.models import ChatHistoryModel
from features.order.models import OrderModel
from features.product.models import ProductModel
from utilities.email.main_email import gmail_order_email_sender
from utilities.enums import EmailTemplate
from utilities.module_utils import get_user_by_id


def get_product_by_sku(
    db: Session, user_id: int, business_id: int, sku_num: str, quantity:str
) -> dict | list:
    try:
        if not (
            product := db.query(ProductModel)
            .where(ProductModel.sku_no == sku_num)
            .first()
        ):
            raise HTTPException(
                status_code=404,
                detail={
                    "status": False,
                    "message": constants.NOT_PPRDUCT,
                },
            )
        print(product.name + " " + product.sku_no)

        if not (user := db.query(UserModel).where(UserModel.id == user_id).first()):
            raise HTTPException(
                status_code=404,
                detail={
                    "status": False,
                    "message": constants.USER_NOT_FOUND,
                },
            )

        new_order = OrderModel(
            user_id=user_id,
            vendor_id=business_id,
            product_id=product.id,
            name=product.name,
            quantity=quantity,
            category=product.category,
            description=product.description,
            image_url=product.image_url,
            price=product.price,
            status="pending",
            delivery_address=user.delivery_address,
        )

        db.add(new_order)
        db.commit()
        db.refresh(new_order)
        user = get_user_by_id(db=db, user_id=new_order.vendor_id)
        gmail_order_email_sender(
            user.full_name, new_order, user.email, EmailTemplate.ORDER_EMAIL.value
        )
        db.query(ChatHistoryModel).filter_by(user_id=user_id).update(
            {ChatHistoryModel.is_confirm: False}
        )
        return {"status": True, "message": constants.SUCCESSFULLY_ADDED}

    except HTTPException:
        return HTTPException(
            status_code=400,
            detail={
                "status": False,
                "message": constants.SOMETHING_WRONG,
            },
        )


# ! Text File Functios
def read_chat_txt(vendor_id: int) -> str:
    with open(
        f"features/chatbot/business_details/vendor_chats/vendor_chat_{vendor_id}.txt",
        "r",
        encoding="utf-8",
    ) as file:
        # Read the lines of the file into a list
        lines = file.readlines()
    # Combine the lines into a multiline string
    multiline_string = "".join(lines)
    return multiline_string


def read_business_details_txt(vendor_id: int) -> str:
    with open(
        f"features/chatbot/business_details/vendor_business/business_details_{vendor_id}.txt",
        "r",
        encoding="utf-8",
    ) as file:
        # Read the lines of the file into a list
        lines = file.readlines()
    # Combine the lines into a multiline string
    multiline_string = "".join(lines)
    return multiline_string


def format_business_description(vendor_id: int, product_list: list | dict) -> str:
    """Reads the business description file, formats it, and returns the result."""

    with open(
        "features/chatbot/business_details/business_description.txt",
        "r",
        encoding="UTF-8",
    ) as file:
        all_lines = file.read()

    formatted_text = all_lines.format(
        product_list=product_list,
        chat=read_chat_txt(vendor_id),
        business_details=read_business_details_txt(vendor_id),
    )
    return formatted_text


def upload_chat(vendor_id: int, file: UploadFile) -> dict:
    with open(
        f"features/chatbot/business_details/vendor_chats/vendor_chat_{vendor_id}.txt",
        "wb",
    ) as f:
        f.write(file.file.read())
        return {
            "status": True,
            "message": constants.FILE_UPLOAD,
            "filename": file.filename,
        }


def upload_business_details(vendor_id: int, file: UploadFile) -> dict:
    with open(
        f"features/chatbot/business_details/vendor_business/business_details_{vendor_id}.txt",
        "wb",
    ) as f:
        f.write(file.file.read())
        return {
            "status": True,
            "message": constants.FILE_UPLOAD,
            "filename": file.filename,
        }


# ! Database Functions
def load_conversation_from_db(
    db: Session, user_id: int, business_id: int
) -> list:
    """
    Load conversation history from the database.

    Args:
        db (Session): Database session.
        user_id (int): User ID.
        business_id (int): Business ID.

    Returns:
        list: List containing the conversation history.
    """
    if (
        result := db.query(ChatHistoryModel)
        .filter(
            ChatHistoryModel.user_id == user_id,
            ChatHistoryModel.vendor_id == business_id,
        )
        .first()
    ):
        conversation_text = result.conversation_text
        return json.loads(conversation_text)
    return []


def save_conversation_to_db(
    db: Session,
    user_id: int,
    business_id: int,
    conversation_history: list[str],
) -> None:
    """
    Save conversation history to the database.

    Args:
        db (Session): Database session.
        user_id (int): User ID.
        business_id (int): Business ID.
        conversation_history (list[str]): List containing the conversation history.
    """
    
    if (
        existing_conversation := db.query(ChatHistoryModel)
        .filter(
            ChatHistoryModel.user_id == user_id,
            ChatHistoryModel.vendor_id == business_id,
        )
        .first()
    ):
        existing_conversation = json.loads(existing_conversation.conversation_text)
        existing_conversation.extend(conversation_history)
        
        db.query(ChatHistoryModel).where(
            (ChatHistoryModel.user_id == user_id)
            & (ChatHistoryModel.vendor_id == business_id),
        ).update(
            {
                ChatHistoryModel.conversation_text: json.dumps(existing_conversation),
                ChatHistoryModel.updated_at: datetime.utcnow(),
            }
        )
    else:
        chat = ChatHistoryModel(
            user_id=user_id,
            vendor_id=business_id,
            conversation_text=json.dumps(conversation_history),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        db.add(chat)

    db.commit()


def get_chat(db: Session, user_id: int, vendor_id: int) -> dict:
    if (
        result := db.query(ChatHistoryModel)
        .filter(
            ChatHistoryModel.user_id == user_id,
            ChatHistoryModel.vendor_id == vendor_id,
        )
        .first()
    ):
        return {
            "status": True,
            "message": constants.USER_CHAT,
            "data": json.loads(result.conversation_text),
        }
    raise HTTPException(
        status_code=404,
        detail={
            "status": False,
            "message": constants.USER_CHAT_NOT_FOUND,
        },
    )




def get_chats_data(db: Session) -> dict:
    try:
        chats = db.query(ChatHistoryModel).all()
        chats_list = []
        for chat in chats:
            chat_obj = {}
            chat_obj["id"] = chat.id
            chat_obj["user_id"] = chat.user_id
            chat_obj["vendor_id"] = chat.vendor_id

            chats_list.append(chat_obj)
        return {"status": True, "message": constants.CHAT_LIST, "data": chats_list}
    
    
    except HTTPException:
        return HTTPException(
            status_code=400,
            detail={
                "status": False,
                "message": constants.SOMETHING_WRONG,
            },
        )
