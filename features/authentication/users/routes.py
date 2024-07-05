"""Authentication routes for api."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from configuration import constants
from db.db_setup import get_db
from features.authentication.dependency import (
    check_password,
    create_user,
    forgot_password_email,
    resend_otp,
    reset_password,
    user_verification,
)
from features.authentication.schemas import (
    ForgotPassword,
    Login,
    OTPverification,
    Register,
    ResendOTP,
    ResetUserPassword,
)
from utilities.module_utils import check_if_user_exist, get_user_by_email

# from typing import Any


userAuth = APIRouter()


@userAuth.post("/user/register", tags=["User"])
async def register_user(
    user: Register,
    db: Session = Depends(get_db),
) -> dict:
    """Register the user.

    Args:
        user (Login): Schema of user
        db (Session, optional): Defaults to Depends(get_db).

    Returns:
        dict[str, str]: will return info from db.
    """

    if check_if_user_exist(db=db, user_email=user.email):
        raise HTTPException(
            status_code=400,
            detail={
                "status": False,
                "message": constants.ALREADY_REGISTERED,
            },
        )

    return create_user(db=db, user=user)


@userAuth.post("/user/otp_verification", tags=["User"])
async def user_opt_verification(
    user: OTPverification,
    db: Session = Depends(get_db),
) -> dict:
    if not (db_user := get_user_by_email(db=db, email=user.email)):
        raise HTTPException(
            status_code=404,
            detail={
                "status": False,
                "message": constants.USER_NOT_FOUND,
            },
        )
    return user_verification(db=db, user=user, db_user=db_user)


@userAuth.post("/user/signin", tags=["User"])
async def signin_user(
    user: Login,
    db: Session = Depends(get_db),
) -> dict:
    """Sign the user.

    Returns:
        User: Will return user info.
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


@userAuth.post("/user/forgot_password_email", tags=["User"])
async def user_forgot_password_email(
    user: ForgotPassword,
    db: Session = Depends(get_db),
) -> dict:
    if not (db_user := get_user_by_email(db=db, email=user.email)):
        raise HTTPException(
            status_code=404,
            detail={
                "status": False,
                "message": constants.USER_NOT_FOUND,
            },
        )
    return forgot_password_email(db=db, user=user, db_user=db_user)


@userAuth.post("/user/reset_password", tags=["User"])
async def reset_user_password(
    user: ResetUserPassword,
    db: Session = Depends(get_db),
) -> dict:
    if not (db_user := get_user_by_email(db=db, email=user.email)):
        raise HTTPException(
            status_code=404,
            detail={
                "status": False,
                "message": constants.USER_NOT_FOUND,
            },
        )
    return reset_password(db=db, user=user, db_user=db_user)


@userAuth.post("/user/resend_otp", tags=["User"])
async def user_resend_otp(
    user: ResendOTP,
    db: Session = Depends(get_db),
) -> dict:
    if not (db_user := get_user_by_email(db=db, email=user.email)):
        raise HTTPException(
            status_code=404,
            detail={
                "status": False,
                "message": constants.USER_NOT_FOUND,
            },
        )
    return resend_otp(db=db, user=user, db_user=db_user)
