from pydantic import BaseModel


class ShopOrderCreateSchema(BaseModel):
    user_id: int
    vendor_id: int
    product_id: int
    name: str
    category: str
    description: str
    image_url: str
    price: float
    status: str
    delivery_address: str

    class Config:
        rom_attributes = True


class OrderUpdateStatusSchema(BaseModel):
    status: str

    class Config:
        from_attributes = True
