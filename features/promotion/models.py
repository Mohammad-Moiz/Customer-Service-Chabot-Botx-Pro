# app/features/promotion/models.py
from sqlalchemy import Column, Integer

from db.db_mixin import Timestamp
from db.db_setup import Base


class PromotionModel(Timestamp, Base):
    """Promotion Model class.

    Args:
        Base (declarative_base)
        Timestamp (Datetime)
    """

    __tablename__ = "promotions"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, nullable=False)
    vendor_id = Column(Integer, nullable=False)
