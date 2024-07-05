from sqlalchemy import Column, Integer, String, Text

from db.db_mixin import Timestamp
from db.db_setup import Base


class ContactFormModel(Timestamp, Base):
    """Contact Form Model class.

    Args:
        Base (declarative_base)
        Timestamp (Datetime)
    """

    __tablename__ = "contact_forms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    subject = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
