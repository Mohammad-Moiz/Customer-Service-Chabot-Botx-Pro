from sqlalchemy import Boolean, Column, Integer, Text

from db.db_mixin import Timestamp
from db.db_setup import Base


class ChatHistoryModel(Timestamp, Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    vendor_id = Column(Integer, nullable=False)
    is_confirm = Column(Boolean, default=False)
    conversation_text = Column(Text, nullable=False)

class TempOrderModel(Timestamp, Base):
    __tablename__ = "temp_order"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    vendor_id = Column(Integer, nullable=False)
    sku_no = Column(Text, nullable=False)
    quantity = Column(Text, nullable=False)
