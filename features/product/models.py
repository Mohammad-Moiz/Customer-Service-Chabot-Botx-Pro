"""Models of Product"""


from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from db.db_mixin import Timestamp
from db.db_setup import Base


class ProductModel(Timestamp, Base):
    """Product Model class.

    Args:
        Base (declarative_base)
        Timestamp (Datetime)
    """

    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    sku_no = Column(String(20), unique=True, nullable=False)
    name = Column(String(225), index=True, nullable=False)
    category = Column(String(225), index=True, nullable=False)
    brand = Column(String(225), nullable=False)
    description = Column(Text, nullable=False)
    image_url = Column(String(225), nullable=False)
    available = Column(Boolean, default=False)
    price = Column(Integer, nullable=False)

    product_user = relationship("UserModel", back_populates="user_product")
