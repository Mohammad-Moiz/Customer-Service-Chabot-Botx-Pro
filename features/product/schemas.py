"""Pydentic give base model for schema"""
from pydantic import BaseModel


class AddProduct(BaseModel):
    # """Add_Product model.

    # Args:
    #     BaseModel (pydantic): pydantic type model
    # """

    vendor_id: int
    sku_no: str
    name: str
    category: str
    brand: str
    description: str
    image_url: str
    available: bool
    price: int

    class Config:
        from_attributes = True

    def model_dump(self):
        """
        Dump the model data to a dictionary.
        """
        return self.dict()
