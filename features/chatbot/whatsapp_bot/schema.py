"""_summary_"""

from pydantic import BaseModel


class ChatInput(BaseModel):
    """_summary_

    Args:
        BaseModel (_type_): _description_
    """

    user_no: str
    business_id: str
    user_input: str


class Chat(BaseModel):
    """_summary_

    Args:
        BaseModel (_type_): _description_
    """

    user_no: str
    vendor_id: str

    class Config:
        from_attributes = True


class AddWhatsappUser(BaseModel):
    # """Add_Product model.

    # Args:
    #     BaseModel (pydantic): pydantic type model
    # """

    user_no: str
    vendor_no: str
    name: str
    phone: str
    delivery_address: str

    class Config:
        from_attributes = True
