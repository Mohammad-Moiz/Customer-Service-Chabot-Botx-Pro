"""Authentication routes for api."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from configuration import constants
from db.db_setup import get_db
from features.authentication.dependency import (
    check_password,
    create_vendor,
    get_vendors,
)
from features.authentication.schemas import Login, Register
from utilities.module_utils import check_if_user_exist, get_user_by_email

# from typing import Any


vendorAuth = APIRouter()


@vendorAuth.post("/vendor/register", tags=["Vendor"])
async def register_vendor(
    vendor: Register,
    db: Session = Depends(get_db),
) -> dict:
    """Register the vendor.

    Args:
        vendor (Login): Schema of vendor
        db (Session, optional): Defaults to Depends(get_db).

    Returns:
        dict[str, str]: will return info from db.
    """

    if check_if_user_exist(db=db, user_email=vendor.email):
        raise HTTPException(
            status_code=400,
            detail={
                "status": False,
                "message": constants.ALREADY_REGISTERED,
            },
        )

    return create_vendor(db=db, user=vendor)


@vendorAuth.post("/vendor/signin", tags=["Vendor"])
async def signin_vendor(
    user: Login,
    db: Session = Depends(get_db),
) -> dict:
    """Sign the vendor.

    Returns:
        vendor: Will return vendor info.
    """
    if not (db_user := get_user_by_email(db=db, email=user.email)):
        raise HTTPException(
            status_code=404,
            detail={
                "status": False,
                "message": constants.USER_NOT_FOUND,
            },
        )
    if not db_user.is_verify:
        raise HTTPException(
            status_code=401,
            detail={
                "status": False,
                "message": constants.USER_NOT_VERIFY,
            },
        )
    return check_password(password=user.password, user=db_user)


@vendorAuth.get("/vendors/list", tags=["Vendor"])
async def get_products_list(db: Session = Depends(get_db)) -> dict:
    vendors = get_vendors(db=db)
    return vendors
