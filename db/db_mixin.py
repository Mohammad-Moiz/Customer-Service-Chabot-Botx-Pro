"""Mixin of created adn updated datetime."""
from datetime import datetime

from sqlalchemy import Column, DateTime
from sqlalchemy.orm import declarative_mixin


@declarative_mixin
class Timestamp:
    """Class will add two columns created_at and updated_at in the table."""

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
