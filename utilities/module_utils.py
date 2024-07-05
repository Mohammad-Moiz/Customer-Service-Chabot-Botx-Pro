from pydantic import EmailStr
from sqlalchemy.orm import Session

from features.authentication.models import UserModel
from features.product.models import ProductModel


# ! Users Fuctions
def check_if_user_exist(db: Session, user_email: EmailStr) -> UserModel:
    return (
        db.query(UserModel)
        .filter(
            UserModel.email == user_email,
        )
        .first()
    )


def get_user_by_email(db: Session, email: EmailStr) -> UserModel:
    return db.query(UserModel).filter(UserModel.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> UserModel:
    return (
        db.query(UserModel)
        .filter(
            UserModel.id == user_id,
        )
        .first()
    )


def get_user_role(db: Session, user_id: int) -> UserModel:
    return (
        db.query(UserModel)
        .filter(
            UserModel.id == user_id,
        )
        .first()
        .user_role
    )


# ! Product Fuctions
def get_product_by_id(db: Session, product_id: int) -> ProductModel:
    return (
        db.query(ProductModel)
        .filter(
            ProductModel.id == product_id,
        )
        .first()
    )


def check_product_sku_no(db: Session, sku_no: int) -> ProductModel:
    return (
        db.query(ProductModel)
        .filter(
            ProductModel.sku_no == sku_no,
        )
        .first()
    )
