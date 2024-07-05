"""Pydentic give base model for schema"""
from pydantic import BaseModel


class AddPromotion(BaseModel):
    """Add_Product model.

    Args:
        BaseModel (pydantic): pydantic type model
    """

    product_id: int
    vendor_id: int

    class Config:
        from_attributes = True
