"""Dependency of product"""
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from configuration import constants
from features.product.models import ProductModel
from features.product.schemas import AddProduct
from utilities.module_utils import check_product_sku_no, get_user_by_id


def get_products(db: Session) -> dict:
    try:
        products = db.query(ProductModel).all()
        product_list = []
        for product in products:
            result = {
                "id": product.id,
                "vendor_id": product.vendor_id,
                "name": product.name,
                "category": product.category,
                "description": product.description,
                "image_url": product.image_url,
                "available": product.available,
                "price": product.price,
                "sku": product.sku_no,
                "brand": product.brand,
                "created_at": product.created_at,
                "updated_at": product.updated_at,
            }
            product_list.append(result)

        return {
            "status": True,
            "message": constants.PPRDUCT_LIST_LOADED,
            "data": product_list,
        }

    except HTTPException:
        return HTTPException(
            status_code=400,
            detail={
                "status": False,
                "message": constants.SOMETHING_WRONG,
            },
        )


def get_product_by_id(db: Session, product_id: int) -> dict:
    try:
        if not (
            product := db.query(ProductModel)
            .filter(ProductModel.id == product_id)
            .first()
        ):
            raise HTTPException(
                status_code=404,
                detail={
                    "status": False,
                    "message": constants.NOT_PPRDUCT,
                },
            )
        product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
        product_list = []
        result = {
            "id": product.id,
            "vendor_id": product.vendor_id,
            "sku_no": product.sku_no,
            "name": product.name,
            "category": product.category,
            "brand": product.brand,
            "description": product.description,
            "image_url": product.image_url,
            "available": product.available,
            "price": product.price,
            "created_at": product.created_at,
            "updated_at": product.updated_at,
        }
        product_list.append(result)
        return {
            "status": True,
            "message": constants.PPRDUCT_LIST_LOADED,
            "data": product_list,
        }

    except HTTPException:
        return HTTPException(
            status_code=400,
            detail={
                "status": False,
                "message": constants.SOMETHING_WRONG,
            },
        )


def add_product_into_database(db: Session, product_data: AddProduct) -> dict:
    try:
        if not get_user_by_id(db=db, user_id=product_data.vendor_id):
            raise HTTPException(
                status_code=404,
                detail={
                    "status": False,
                    "message": constants.VENDOR_NOT_FOUND,
                },
            )

        if check_product_sku_no(db=db, sku_no=product_data.sku_no):
            raise HTTPException(
                status_code=409,
                detail={
                    "status": False,
                    "message": constants.SKU_ALREADY_EXIST,
                },
            )

        new_product = ProductModel(
            **product_data.model_dump(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        db.add(new_product)
        db.commit()
        db.refresh(new_product)

        return {
            "status": True,
            "message": constants.SUCCESSFULLY_ADDED,
            "data": {
                "id": new_product.id,
                "vendor_id": new_product.vendor_id,
                "sku_no": new_product.sku_no,
                "name": new_product.name,
                "category": new_product.category,
                "brand": new_product.brand,
                "description": new_product.description,
                "image_url": new_product.image_url,
                "price": new_product.price,
            },
        }

    except HTTPException:
        return HTTPException(
            status_code=400,
            detail={
                "status": False,
                "message": constants.SOMETHING_WRONG,
            },
        )

def update_product(db: Session, product_id: int, product_data: AddProduct) -> dict:
    try:
        # Check if the product exists
        product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
        if not product:
            raise HTTPException(
                status_code=404,
                detail={
                    "status": False,
                    "message": constants.NOT_PRODUCT,
                },
            )
        
        # Check if the vendor exists
        if not get_user_by_id(db=db, user_id=product_data.vendor_id):
            raise HTTPException(
                status_code=404,
                detail={
                    "status": False,
                    "message": constants.VENDOR_NOT_FOUND,
                },
            )

        # Check if the updated SKU number is already used by another product
        if product_data.sku_no != product.sku_no and check_product_sku_no(db=db, sku_no=product_data.sku_no):
            raise HTTPException(
                status_code=409,
                detail={
                    "status": False,
                    "message": constants.SKU_ALREADY_EXIST,
                },
            )

        # Update the product data
        product.vendor_id = product_data.vendor_id
        product.sku_no = product_data.sku_no
        product.name = product_data.name
        product.category = product_data.category
        product.brand = product_data.brand
        product.description = product_data.description
        product.image_url = product_data.image_url
        product.available = product_data.available
        product.price = product_data.price
        product.updated_at = datetime.utcnow()

        db.commit()

        return {
            "status": True,
             "message": constants.PRODUCT_UPDATED_SUCCESSFULLY,
            "data": {
                "id": product.id,
                "vendor_id": product.vendor_id,
                "sku_no": product.sku_no,
                "name": product.name,
                "category": product.category,
                "brand": product.brand,
                "description": product.description,
                "image_url": product.image_url,
                "available": product.available,
                "price": product.price,
                "created_at": product.created_at,
                "updated_at": product.updated_at,
            },
        }

    except HTTPException as e:
        return {
            "status": False,
            "message": str(e.detail['message']),
        }



def check_product_existence(db: Session, product_id: int) -> bool:
    """
    Check if the product exists in the database.

    Args:
        db (Session): SQLAlchemy database session.
        product_id (int): ID of the product to check.

    Returns:
        bool: True if the product exists, False otherwise.
    """
    product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if not product:
        return False
    return True


def delete_product(db: Session, product_id: int) -> dict:
    """
    Delete a product from the database.

    Args:
        db (Session): SQLAlchemy database session.
        product_id (int): ID of the product to delete.

    Returns:
        dict: A dictionary containing the status of the deletion operation.
    """
    try:
        # Retrieve the product
        product = db.query(ProductModel).filter(ProductModel.id == product_id).first()

        # If the product doesn't exist, raise an HTTPException
        if not product:
            raise HTTPException(
                status_code=404,
                detail={
                    "status": False,
                    "message": constants.NOT_PRODUCT,
                },
            )

        # Delete the product from the database
        db.delete(product)
        db.commit()

        return {
            "status": True,
            "message": constants.PRODUCT_DELETED_SUCCESSFULLY,
            "data": {
                "id": product.id,
                "name": product.name,
            },
        }
    except HTTPException as e:
        return {
            "status": False,
            "message": str(e.detail['message']),
        }