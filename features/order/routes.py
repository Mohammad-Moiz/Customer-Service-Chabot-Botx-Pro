"""Authentication routes for api."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from configuration import constants
from db.db_setup import get_db
from features.order.dependency import (
    create_order,
    get_order_by_id,
    get_order_list_by_db,
    get_recent_shop_orders,
    update_order_status,
)
from features.order.schemas import OrderUpdateStatusSchema, ShopOrderCreateSchema
from utilities.module_utils import get_product_by_id, get_user_by_id

order = APIRouter()


@order.get("/order/get_orders", tags=["Order"])
async def get_order_list(db: Session = Depends(get_db)) -> dict:
    return get_order_list_by_db(db=db)


@order.post("/order/create_orders", tags=["Order"])
def create_shop_order(
    order_data: ShopOrderCreateSchema, db: Session = Depends(get_db)
) -> dict:
    if not get_user_by_id(db=db, user_id=order_data.user_id):
        raise HTTPException(
            status_code=404,
            detail={
                "status": False,
                "message": constants.USER_NOT_FOUND,
            },
        )
    if not get_product_by_id(db=db, product_id=order_data.product_id):
        raise HTTPException(
            status_code=404,
            detail={
                "status": False,
                "message": constants.PRODUCT_NOT_FOUND,
            },
        )

    return create_order(db=db, order_data=order_data)


@order.get("/order/recent", tags=["Order"])
async def get_recent_shop_orders_endpoint(db: Session = Depends(get_db)) -> dict:
    return get_recent_shop_orders(db=db)


@order.get("/order/{order_id}", tags=["Order"])
async def get_order(order_id: int, db: Session = Depends(get_db)) -> dict:
    return get_order_by_id(db=db, order_id=order_id)


@order.put("/order/update_status/{order_id}", tags=["Order"])
def update_order_status_endpoint(
    order_id: int,
    new_status_data: OrderUpdateStatusSchema,
    db: Session = Depends(get_db),
) -> dict:
    return update_order_status(
        db=db, order_id=order_id, new_status=new_status_data.status
    )
