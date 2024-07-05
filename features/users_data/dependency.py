"""Dependency of user"""


from fastapi import HTTPException
from sqlalchemy.orm import Session

from configuration import constants
from features.authentication.models import UserModel


def get_user(db: Session) -> dict:
    try:
        if not (users := db.query(UserModel).all()):
            raise HTTPException(
                status_code=404,
                detail={
                    "status": False,
                    "message": constants.USER_NOT_FOUND,
                },
            )
        user_list = []

        for user in users:
            result = {
                "id": user.id,
                "full_name": user.full_name,
                "email": user.email,
                "phone": user.phone,
                "is_verify": user.is_verify,
                "user_role": user.user_role,
                "created_at": user.created_at,
                "updated_at": user.updated_at,
            }
            if result["user_role"] == "USER":
                user_list.append(result)

        return {
            "status": True,
            "message": constants.USER_LIST_LOADED,
            "data": user_list,
        }

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail={
                "status": False,
                "message": constants.SOMETHING_WRONG,
            },
        ) from e
