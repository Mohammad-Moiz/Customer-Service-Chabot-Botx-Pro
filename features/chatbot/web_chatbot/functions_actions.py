"""openai functions call - actions"""

import json
from datetime import datetime
from sqlalchemy.orm import Session
from features.product.models import ProductModel
from features.authentication.models import UserModel
from features.chatbot.web_chatbot.models import TempOrderModel
from features.chatbot.web_chatbot.dependency import get_product_by_sku


def product_details(db: Session, business_id, sku)-> list:
    # Create a list of messages for the chat model
    products = (
        db.query(ProductModel)
        .where((ProductModel.vendor_id == business_id) & (ProductModel.sku_no == sku))
        .all()
    )
    product_detail = []

    for product in products:
        result = {
            "sku_no": product.sku_no,
            "name": product.name,
            "brand": product.brand,
            "description": product.description,
            "image_url": product.image_url,
            "price": product.price,
        }
        product_detail.append(result)
    
    return product_detail


def get_product_list(db: Session, business_id) -> list:
    # Create a list of messages for the chat model
    products = (
        db.query(ProductModel)
        .where(
            (ProductModel.vendor_id == business_id) & (ProductModel.available),
        )
        .all()
    )
    product_list = []

    for product in products:
        result = {
            "sku_no": product.sku_no,
            "name": product.name,
            "category": product.category,
            "brand": product.brand,
            "image_url": product.image_url,
            "price": product.price,
        }
        product_list.append(result)

    return product_list


def get_product_category(db: Session, business_id) -> list:
    unique_categories = set()
    products = (
        db.query(ProductModel)
        .filter(
            (ProductModel.vendor_id == business_id) & (ProductModel.available)
        )
        .all()
    )
    for product in products:
        unique_categories.add(product.category)
    category_list = list(unique_categories)

    return category_list

def get_products_according_to_categories(db: Session, business_id, categories_list) -> list:
    products = (
        db.query(ProductModel)
        .filter(
            (ProductModel.vendor_id == business_id) & 
            (ProductModel.available) & 
            (ProductModel.category.in_(categories_list))
        )
        .all()
    )
    product_list = []

    for product in products:
        result = {
            "sku_no": product.sku_no,
            "name": product.name,
            "brand": product.brand,
            "image_url": product.image_url,
            "price": product.price,
        }
        product_list.append(result)

    return product_list


def update_temp_order(db: Session, user_id, business_id, sku_no, quantity):
    if (
        db.query(TempOrderModel)
        .filter(
            TempOrderModel.user_id == user_id,
            TempOrderModel.vendor_id == business_id,
        )
        .first()
    ):
        db.query(TempOrderModel).where(
            (TempOrderModel.user_id == user_id)
            & (TempOrderModel.vendor_id == business_id),
        ).update(
            {
                TempOrderModel.sku_no: json.dumps(sku_no),
                TempOrderModel.quantity: json.dumps(quantity),
                TempOrderModel.updated_at: datetime.utcnow(),
            }
        )
    else:
        temp_order = TempOrderModel(
            user_id=user_id,
            vendor_id=business_id,
            sku_no=json.dumps(sku_no),
            quantity=json.dumps(quantity),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        db.add(temp_order)

    db.commit()


def load_order_list_from_db(
    db: Session, user_id: int, business_id: int
):
    """
    Load order products list with quantities from the database.

    Args:
        db (Session): Database session.
        user_id (int): User ID.
        business_id (int): Business ID.

    Returns:
        list: List containing the ordered products with quantities.
    """
    if (
        result := db.query(TempOrderModel)
        .filter(
            TempOrderModel.user_id == user_id,
            TempOrderModel.vendor_id == business_id,
        )
        .first()
    ):
        sku_no = result.sku_no
        quantity = result.quantity
        sku_no_list = json.loads(sku_no)
        quantity_list = json.loads(quantity)
        
    return sku_no_list, quantity_list

def get_address(db: Session, id):
    user = (
        db.query(UserModel)
        .filter(UserModel.id == id)
        .first()
    )

    if user and user.delivery_address:
        return user.delivery_address
    else:
        return "None"
    
def product_details_for_skus(db: Session, business_id, skus) -> list:
    all_product_details = []

    for sku in skus:
        product_detail = product_details(db, business_id, sku)
        all_product_details.extend(product_detail)

    return all_product_details


def get_product_details(db: Session, business_id, sku_no):
    print(sku_no)
    product_description = product_details_for_skus(db, business_id, sku_no)
    print(product_description)
    return str(product_description)


def get_all_available_products(db: Session, business_id: int):
    products = str(get_product_list(db, business_id))
    print(products)
    return products


def get_available_category(db: Session, business_id: int):
    categories = get_product_category(db, business_id)
    print(categories)
    return str(categories)


def get_products_according_to_category(category: list, db: Session, business_id: int):
    categories_list = [item.lower() for item in category]
    print(f'category: {categories_list}')
    products_of_categories = get_products_according_to_categories(db, business_id, categories_list)
    print(products_of_categories)
    return str(products_of_categories)


def get_order(sku_no, quantity, db: Session, user_id: int, business_id: int):
    print(sku_no)
    print(quantity)
    update_temp_order(db, user_id, business_id, sku_no, quantity)
    address = get_address(db, user_id)
    if address == "None":
        print('No Previous Address stored')
        return 'Ask customer: your order is noted and now you have to provide us your delivery address'
    else:
        print(address)
        return f'Now ask to customer: "your order is noted and your previous delivery address is {address}, did you want to confirm order?"'

def get_delivery_address(address, db: Session, user_id: int):
    db.query(UserModel).filter_by(id=user_id).update(
        {UserModel.delivery_address: address}
    )
    print(f'Address updated in db: {address}')
    return 'thanks for providing delivery address'


def get_order_confirmation(db: Session, user_id: int, business_id: int):
    print('Order Confirmed')
    sku_no_list, quantity_list = load_order_list_from_db(db=db, user_id=user_id, business_id=business_id)
    seen = set()
    unique_sku_no = []

    for item in sku_no_list:
        if item not in seen:
            unique_sku_no.append(item)
            seen.add(item)

    for sku, qty in zip(unique_sku_no, quantity_list):
        print(f'product_sku: {sku}', f' quantity: {qty}')
        get_product_by_sku(db=db, user_id=user_id, business_id=business_id, sku_num=sku, quantity=qty)

    return 'your order is confirmed'