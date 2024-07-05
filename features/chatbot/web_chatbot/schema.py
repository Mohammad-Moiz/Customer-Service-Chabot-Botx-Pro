"""_summary_"""

from pydantic import BaseModel


class ChatInput(BaseModel):
    """_summary_

    Args:
        BaseModel (_type_): _description_
    """

    user_id: str
    business_id: str
    user_input: str


class Chat(BaseModel):
    """_summary_

    Args:
        BaseModel (_type_): _description_
    """

    user_id: str
    vendor_id: str

    class Config:
        from_attributes = True
