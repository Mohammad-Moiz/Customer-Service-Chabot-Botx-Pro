from sqlalchemy import Boolean, Column, Integer, Text, String

from db.db_mixin import Timestamp
from db.db_setup import Base


class WhatsappChatHistoryModel(Timestamp, Base):
    __tablename__ = "whatsapp_chat_history"

    id = Column(Integer, primary_key=True)
    user_no = Column(String(20), index=True, nullable=False)
    vendor_id = Column(Integer, nullable=False)
    is_confirm = Column(Boolean, default=False)
    conversation_text = Column(Text, nullable=False)


class WhatsappTempOrderModel(Timestamp, Base):
    __tablename__ = "whatsapp_temp_order"

    id = Column(Integer, primary_key=True)
    user_no = Column(String(20), index=True, nullable=False)
    vendor_id = Column(Integer, nullable=False)
    sku_no = Column(Text, nullable=False)
    quantity = Column(Text, nullable=False)