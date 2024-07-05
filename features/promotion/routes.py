"""Authentication routes for api."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.db_setup import get_db

# from features.product.dependency import get_product_by_id, get_products
from features.promotion.dependency import (
    get_promotion_product,
    set_product_promotion_endpoint,
    get_promotion_products_details,
)
from features.promotion.schemas import AddPromotion

promotion = APIRouter()


@promotion.post("/promotion/set_product_promotion/", tags=["Promotion"])
def add_product(promotion_data: AddPromotion, db: Session = Depends(get_db)) -> dict:
    return set_product_promotion_endpoint(db=db, promotion_data=promotion_data)


# @promotion.get("/promotion/send_emails/", tags=["Promotion"])
# async def get_promotion_products_details_endpoint(
#     db: Session = Depends(get_db),
# ) -> dict:
#     return get_promotion_products_details(db=db)


@promotion.get("/promotion/get_promotion_product/", tags=["Promotion"])
def get_promotion_product_endpoint(db: Session = Depends(get_db)) -> dict:
    return get_promotion_product(db=db)
