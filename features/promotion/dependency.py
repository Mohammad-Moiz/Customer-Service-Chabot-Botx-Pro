"""Dependency of product"""
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

# from dependency import get_db
from configuration import constants
from features.authentication.models import UserModel
from features.product.models import ProductModel
from features.promotion.models import PromotionModel
from features.promotion.schemas import AddPromotion
from utilities.email.main_email import send_email


def set_product_promotion_endpoint(db: Session, promotion_data: AddPromotion) -> dict:
    try:
        new_product = PromotionModel(
            **promotion_data.model_dump(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        db.add(new_product)
        db.commit()


        promotion_products = (
            db.query(ProductModel)
            .join(PromotionModel, ProductModel.id == new_product.product_id)
            .filter(ProductModel.id == PromotionModel.product_id).all()
        )
        products = []
        for product in promotion_products:
            result = {}
            result["name"] = product.name
            result["vendor_id"] = product.vendor_id
            result["category"] = product.category
            result["description"] = product.description
            result["image_url"] = product.image_url
            result["price"] = product.price
            products.append(result)


        print(products)
        users = db.query(UserModel).filter(UserModel.user_role == 'USER').all()
        print(users)
        
        for user in users:
            send_email(user.email,user.full_name, products[0].get('name'))
        


        return {
            "status": True,
            "message": constants.SUCCESSFULLY_ADDED,
        }
    

        

    except HTTPException:
        return HTTPException(
            status_code=400,
            detail={
                "status": False,
                "message": constants.SOMETHING_WRONG,
            },
        )


def get_promotion_products_details(db: Session) -> dict:
    try:
        promotion_products = (
            db.query(ProductModel)
            .join(PromotionModel, ProductModel.id == PromotionModel.product_id)
            .all()
        )
        products = []
        for product in promotion_products:
            result = {}
            result["name"] = product.name
            result["vendor_id"] = product.vendor_id
            result["category"] = product.category
            result["description"] = product.description
            result["image_url"] = product.image_url
            result["price"] = product.price
            products.append(result)

        users = db.query(UserModel).all()
        for user in users:
            send_email(user.email, products)

        return {"status": True, "message": constants.EMAIL_SENT, "data": products}
    except HTTPException:
        return HTTPException(
            status_code=400,
            detail={
                "status": False,
                "message": constants.SOMETHING_WRONG,
            },
        )


def get_promotion_product(db: Session) -> dict:
    try:
        promotion_products = (
            db.query(ProductModel)
            .join(PromotionModel, ProductModel.id == PromotionModel.product_id)
            .all()
        )
        products = []
        for product in promotion_products:
            result = {}
            result["name"] = product.name
            result["category"] = product.category
            result["description"] = product.description
            result["image_url"] = product.image_url
            result["price"] = product.price
            result["vendor_id"] = product.vendor_id
            products.append(result)

        return {
            "status": True,
            "message": constants.PROMOTION_LIST_LOADED,
            "data": products,
        }
    except HTTPException:
        return HTTPException(
            status_code=400,
            detail={
                "status": False,
                "message": constants.SOMETHING_WRONG,
            },
        )
