#openai functions call - actions
import openai
import os
from dotenv import load_dotenv
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
from sqlalchemy.orm import Session
from features.product.models import ProductModel
from features.order.models import OrderModel

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


def product_details_for_skus(db: Session, business_id, skus) -> list:
    all_product_details = []

    for sku in skus:
        product_detail = product_details(db, business_id, sku)
        all_product_details.extend(product_detail)

    return all_product_details


def get_product_details(db: Session, business_id, sku_no):
    sku_list = sku_no.split(",")
    sku_list = [skus.strip() for skus in sku_list]
    print(sku_list)
    product_description = product_details_for_skus(db, business_id, sku_list)
    quantities = get_product_quantities(db, business_id, sku_list)
    return str(product_description), quantities


def get_available_products(category, db: Session, business_id: int, product_list: str):
    print(product_list)
    print(category)
    return str(product_list)


def get_product_quantities(db: Session, user_id: int) -> list:
    product_quantities = []

    orders_with_products = db.query(OrderModel, ProductModel.sku_no, OrderModel.quantity) \
                             .join(ProductModel, OrderModel.product_id == ProductModel.id) \
                             .filter(OrderModel.user_id == user_id) \
                             .all()

    for order, sku_no, quantity in orders_with_products:
        product_quantities.append({
            "sku_no": sku_no,
            "quantity": quantity
        })
    
    return product_quantities

