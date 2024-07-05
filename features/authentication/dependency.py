"""Dependency of Auth"""

import random
import string
from datetime import datetime, timedelta

from fastapi import HTTPException

# from sqlalchemy import or_
from sqlalchemy.orm import Session

from configuration import constants
from features.authentication.models import UserModel
from features.authentication.schemas import (
    ForgotPassword,
    OTPverification,
    Register,
    ResendOTP,
    ResetUserPassword,
)
from utilities.email.main_email import gmail_html_email_sender
from utilities.enums import EmailTemplate, UserRole
from utilities.hashed_password import get_hashed_password, verify_password


def check_password(password: str, user: UserModel) -> dict:
    if not verify_password(password, user.password):
        raise HTTPException(
            status_code=401,
            detail={
                "status": False,
                "message": constants.INVALID_USER,
            },
        )

    return {
        "status": True,
        "message": constants.USER_LOGIN,
        "data": {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "phone": user.phone,
            "user_role": user.user_role,
        },
    }


def get_users(db: Session, skip: int = 0, limit: int = 100) -> UserModel:
    return db.query(UserModel).offset(skip).limit(limit).all()


def create_user(db: Session, user: Register) -> dict:
    try:
        now = datetime.utcnow()
        future_time = now + timedelta(minutes=10)

        otp = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))

        db_user = UserModel(
            full_name=user.full_name,
            email=user.email,
            phone=user.phone,
            password=get_hashed_password(user.password),
            user_role=UserRole.USER.name,
            otp=otp,
            otp_expire=future_time,
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        gmail_html_email_sender(
            user.full_name, otp, user.email, EmailTemplate.REGISTER.value
        )

        return {
            "status": True,
            "message": constants.USER_REGISTERED,
            "data": {
                "id": db_user.id,
                "full_name": db_user.full_name,
                "email": db_user.email,
                "phone": db_user.phone,
                "user_role": db_user.user_role,
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


def create_vendor(db: Session, user: Register) -> dict:
    try:
        now = datetime.utcnow()
        future_time = now + timedelta(minutes=10)

        otp = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))

        db_user = UserModel(
            full_name=user.full_name,
            email=user.email,
            phone=user.phone,
            password=get_hashed_password(user.password),
            user_role=UserRole.VENDOR.name,
            whatsapp_no=user.whatsapp_no,
            otp=otp,
            otp_expire=future_time,
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        gmail_html_email_sender(
            user.full_name, otp, user.email, EmailTemplate.REGISTER.value
        )

        return {
            "status": True,
            "message": constants.USER_REGISTERED,
            "data": {
                "id": db_user.id,
                "full_name": db_user.full_name,
                "email": db_user.email,
                "phone": db_user.phone,
                "user_role": db_user.user_role,
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


def user_verification(db: Session, user: OTPverification, db_user: UserModel) -> dict:
    if datetime.utcnow() > db_user.otp_expire:
        raise HTTPException(
            status_code=401,
            detail={
                "status": False,
                "message": constants.OTP_EXPIRE,
            },
        )

    if user.otp != db_user.otp:
        raise HTTPException(
            status_code=401,
            detail={
                "status": False,
                "message": constants.OTP_NOT_MATCH,
            },
        )
    db.query(UserModel).filter_by(email=user.email).update(
        {UserModel.is_verify: True, UserModel.updated_at: datetime.utcnow()}
    )
    db.commit()

    return {
        "status": True,
        "message": constants.USER_VERIFY,
        "data": {
            "id": db_user.id,
            "full_name": db_user.full_name,
            "email": db_user.email,
            "phone": db_user.phone,
            "user_role": db_user.user_role,
        },
    }


def forgot_password_email(
    db: Session, user: ForgotPassword, db_user: UserModel
) -> dict:
    try:
        now = datetime.utcnow()
        future_time = now + timedelta(minutes=10)

        otp = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))

        db.query(UserModel).filter_by(email=user.email).update(
            {
                UserModel.otp: otp,
                UserModel.updated_at: datetime.utcnow(),
                UserModel.otp_expire: future_time,
            }
        )
        db.commit()

        gmail_html_email_sender(
            db_user.full_name, otp, db_user.email, EmailTemplate.FORGET_PASS.value
        )

        return {
            "status": True,
            "message": constants.OTP_SEND,
        }

    except HTTPException:
        return HTTPException(
            status_code=400,
            detail={
                "status": False,
                "message": constants.SOMETHING_WRONG,
            },
        )


def reset_password(db: Session, user: ResetUserPassword, db_user: UserModel) -> dict:
    try:
        db.query(UserModel).filter_by(email=user.email).update(
            {
                UserModel.password: get_hashed_password(user.password),
                UserModel.updated_at: datetime.utcnow(),
            }
        )
        db.commit()

        return {
            "status": True,
            "message": constants.PASSWORD_CHANGE,
            "data": {
                "id": db_user.id,
                "full_name": db_user.full_name,
                "email": db_user.email,
                "phone": db_user.phone,
                "user_role": db_user.user_role,
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


def resend_otp(db: Session, user: ResendOTP, db_user: UserModel) -> dict:
    try:
        now = datetime.utcnow()
        future_time = now + timedelta(minutes=10)

        otp = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))

        db.query(UserModel).filter_by(email=user.email).update(
            {
                UserModel.otp: otp,
                UserModel.updated_at: datetime.utcnow(),
                UserModel.otp_expire: future_time,
            }
        )
        db.commit()

        gmail_html_email_sender(
            db_user.full_name, otp, db_user.email, EmailTemplate.RESEDN_OTP.value
        )

        return {
            "status": True,
            "message": constants.OTP_SEND,
        }

    except HTTPException:
        return HTTPException(
            status_code=400,
            detail={
                "status": False,
                "message": constants.SOMETHING_WRONG,
            },
        )


def get_vendors(db: Session) -> dict:
    try:
        vendors = db.query(UserModel).filter(UserModel.user_role == "VENDOR").all()
        vendors_list = []
        for vendor in vendors:
            vendor_obj = {}
            vendor_obj["id"] = vendor.id
            vendor_obj["full_name"] = vendor.full_name
            vendor_obj["email"] = vendor.email
            vendor_obj["phone"] = vendor.phone
            vendors_list.append(vendor_obj)
        return {"status": True, "message": constants.VENDOR_LIST, "data": vendors_list}
    except HTTPException:
        return HTTPException(
            status_code=400,
            detail={
                "status": False,
                "message": constants.SOMETHING_WRONG,
            },
        )
