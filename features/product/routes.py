"""Authentication routes for api."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from configuration import constants
from db.db_setup import get_db
from features.product.dependency import (
    add_product_into_database,
    check_product_existence,
    delete_product,
    get_product_by_id,
    get_products,
    update_product
)
from features.product.schemas import AddProduct
from utilities.module_utils import get_user_role

product = APIRouter()


@product.post("/product/add_product", tags=["Product"])
def add_product(product_data: AddProduct, db: Session = Depends(get_db)) -> dict:
    if not get_user_role(db=db, user_id=product_data.vendor_id) == "VENDOR":
        raise HTTPException(
            status_code=404,
            detail={
                "status": False,
                "message": constants.VENDOR_NOT_FOUND,
            },
        )
    data = add_product_into_database(db=db, product_data=product_data)
    return data


@product.get("/product/get_products", tags=["Product"])
async def get_products_list(db: Session = Depends(get_db)) -> dict:
    products = get_products(db=db)
    return products


@product.get("/product/get_product/{product_id}", tags=["Product"])
async def get_product(product_id: int, db: Session = Depends(get_db)) -> dict:
    return get_product_by_id(db=db, product_id=product_id)



@product.put("/product/update_product/{product_id}", tags=["Product"])
def update_product_route(
    product_id: int,
    product_data: AddProduct,
    db: Session = Depends(get_db)
) -> dict:
    updated_product = update_product(db=db, product_id=product_id, product_data=product_data)
    return updated_product



@product.delete("/product/delete_product/{product_id}", tags=["Product"])
def delete_product_route(
    product_id: int,
    db: Session = Depends(get_db)
) -> dict:
    # Check if the product exists
    if not check_product_existence(db=db, product_id=product_id):
        raise HTTPException(
            status_code=404,
            detail={
                "status": False,
                "message": "Product not found.",
            },
        )
    
    # Delete the product
    deleted_product = delete_product(db=db, product_id=product_id)
    return deleted_product