"""Models of Auth"""
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.orm import relationship

from db.db_mixin import Timestamp
from db.db_setup import Base


class UserModel(Timestamp, Base):
    """User Model class.

    Args:
        Base (declarative_base)
        Timestamp (Datetime)
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    phone = Column(String(15), index=True)
    password = Column(Text, nullable=False)
    is_verify = Column(Boolean, default=False)
    user_role = Column(String(15), nullable=False)
    otp = Column(String(6))
    otp_expire = Column(DateTime, default=datetime.utcnow, nullable=False)
    delivery_address = Column(String(500))
    whatsapp_no = Column(String(20), index=True,)
    instagram_id = Column(String(50), index=True,)
    facebook_id = Column(String(50), index=True,)

    user_orders = relationship("OrderModel", back_populates="order_owner")
    user_product = relationship("ProductModel", back_populates="product_user")


class WhatsappUserModel(Timestamp, Base):
    """whatsapp_users class.

    Args:
        Base (declarative_base)
        Timestamp (Datetime)
    """

    __tablename__ = "whatsapp_users"

    id = Column(Integer, primary_key=True, index=True)
    user_no = Column(String(20), index=True)
    vendor_no = Column(String(20), index=True)
    name = Column(String(100))
    phone = Column(String(15))
    delivery_address = Column(String(500))
