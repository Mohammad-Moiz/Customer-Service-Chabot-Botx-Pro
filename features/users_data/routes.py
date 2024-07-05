"""Authentication routes for api."""


from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.db_setup import get_db

from .dependency import get_user

user_data = APIRouter()


@user_data.get("/user_data/get_user", tags=["User_data"])
async def get_user_list(db: Session = Depends(get_db)) -> dict:
    users = get_user(db=db)
    return users
