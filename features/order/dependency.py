"""Dependency of product"""

from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from configuration import constants
from features.order.models import OrderModel
from features.order.schemas import ShopOrderCreateSchema
from utilities.email.main_email import gmail_order_email_sender
from utilities.enums import EmailTemplate
from utilities.module_utils import get_user_by_id


def get_order_list_by_db(db: Session) -> dict:
    try:
        recent_orders = db.query(OrderModel).all()
        order_list = []
        for order in recent_orders:
            result = {
                "id": order.id,
                "product_id": order.product_id,
                "user_id": order.user_id,
                "vendor_id": order.vendor_id,
                "name": order.name,
                "category": order.category,
                "description": order.description,
                "image_url": order.image_url,
                "price": order.price,
                "status": order.status,
                "delivery_address": order.delivery_address,
                "created_at": order.created_at,
                "updated_at": order.updated_at,
            }
            order_list.append(result)

        return {
            "status": True,
            "message": constants.ORDER_LIST_LOADED,
            "data": order_list,
        }
    except HTTPException:
        return HTTPException(
            status_code=400,
            detail={
                "status": False,
                "message": constants.SOMETHING_WRONG,
            },
        )


def get_recent_shop_orders(db: Session) -> dict:
    try:
        recent_orders = (
            db.query(OrderModel).order_by(OrderModel.created_at.desc()).limit(10).all()
        )
        order_list = []
        for order in recent_orders:
            result = {
                "id": order.id,
                "product_id": order.product_id,
                "user_id": order.user_id,
                "vendor_id": order.vendor_id,
                "name": order.name,
                "category": order.category,
                "description": order.description,
                "image_url": order.image_url,
                "price": order.price,
                "status": order.status,
                "delivery_address": order.delivery_address,
                "created_at": order.created_at,
                "updated_at": order.updated_at,
            }
            order_list.append(result)

        return {
            "status": True,
            "message": constants.ORDER_LIST_LOADED,
            "data": order_list,
        }
    except HTTPException:
        return HTTPException(
            status_code=400,
            detail={
                "status": False,
                "message": constants.SOMETHING_WRONG,
            },
        )


def create_order(db: Session, order_data: ShopOrderCreateSchema) -> dict:
    try:
        new_order = OrderModel(
            **order_data.model_dump(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        db.add(new_order)
        db.commit()
        db.refresh(new_order)
        user = get_user_by_id(db=db, user_id=new_order.user_id)
        gmail_order_email_sender(
            user.full_name, new_order, user.email, EmailTemplate.ORDER_EMAIL.value
        )

        return {"status": True, "message": constants.SUCCESSFULLY_ADDED}
    except HTTPException:
        return HTTPException(
            status_code=400,
            detail={
                "status": False,
                "message": constants.SOMETHING_WRONG,
            },
        )


def get_order_by_id(db: Session, order_id: int) -> dict:
    try:
        order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
        order_list = []
        result = {
            "id": order.id,
            "product_id": order.product_id,
            "user_id": order.user_id,
            "vendor_id": order.vendor_id,
            "name": order.name,
            "category": order.category,
            "description": order.description,
            "image_url": order.image_url,
            "price": order.price,
            "status": order.status,
            "delivery_address": order.delivery_address,
            "created_at": order.created_at,
            "updated_at": order.updated_at,
        }
        order_list.append(result)
        return {
            "status": True,
            "message": constants.ORDER_LIST_LOADED,
            "data": order_list,
        }

    except HTTPException:
        return HTTPException(
            status_code=400,
            detail={
                "status": False,
                "message": constants.SOMETHING_WRONG,
            },
        )


def update_order_status(db: Session, order_id: int, new_status: str) -> dict:
    if not (order := db.query(OrderModel).filter(OrderModel.id == order_id).first()):
        return HTTPException(
            status_code=400,
            detail={
                "status": False,
                "message": constants.SOMETHING_WRONG,
            },
        )
    order.status = new_status
    db.commit()

    return {"status": True, "message": "Product status updated successfully"}
