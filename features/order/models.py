"""Models of Orders"""
from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from db.db_mixin import Timestamp
from db.db_setup import Base


class OrderModel(Timestamp, Base):
    """Order Model class.

    Args:
        Base (declarative_base)
        Timestamp (Datetime)
    """

    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    user_no = Column(String(20), index=True)
    vendor_id = Column(Integer, nullable=False)
    name = Column(String(225), index=True, nullable=False)
    quantity = Column(String(225), index=True, nullable=False)
    category = Column(String(225), index=True, nullable=False)
    description = Column(Text, nullable=False)
    image_url = Column(String(225), nullable=False)
    price = Column(Integer, nullable=False)
    status = Column(String(100), default="pending", nullable=False)
    delivery_address = Column(String(500))

    order_owner = relationship("UserModel", back_populates="user_orders")
