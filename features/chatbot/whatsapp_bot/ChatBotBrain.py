"""page"""

import json
from sqlalchemy.orm import Session
from features.chatbot.whatsapp_bot.functions_actions import (
    get_product_details,
    get_all_available_products,
    get_order,
    get_customer_name_phone_delivery_address,
    get_order_confirmation,
)
from features.product.models import ProductModel
from features.chatbot.whatsapp_bot.dependency import format_business_description
from features.chatbot.whatsapp_bot.open_ai_config import initialize_chat_model, initialize_function_model


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
            "brand": product.brand,
            "image_url": product.image_url,
            "price": product.price,
        }
        product_list.append(result)

    return product_list


# define main chatcompletion - Chatbot whit functions call
def run_conversation(db: Session, business_id: int, user_no: str, prompt):
    # Step 1: send the conversation and available functions to GPT
    product_list = get_product_list(db=db, business_id=business_id)
    system_prompt = format_business_description(business_id, product_list)
    messages = [
        {"role": "system", "content": f"{system_prompt}"},
        {"role": "user", "content": f"{prompt}?"},
    ]

    functions = [
        {
            "name": "get_all_available_products",
            "description": "Usefull to get all available products in our stock now and provide it to customer.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
        {
            "name": "get_product_details",
            "description": "Get the details of products using sku of that products",
            "parameters": {
                "type": "object",
                "properties": {
                    "sku": {
                        "type": "array",
                        "description": "list of sku_no to search details of products in our stock, e.g. ['16298202', '16294810']",
                        "items": {"type": "string"},
                    },
                },
                "required": ["sku"],
            },
        },
        {
            "name": "get_order",
            "description": "Get the order by using sku's of products and quantities",
            "parameters": {
                "type": "object",
                "properties": {
                    "sku": {
                        "type": "array",
                        "description": "list of sku no's to take order of products from our stock, e.g. ['16298202', '16294810']",
                        "items": {"type": "string"},
                    },
                    "quantity": {
                        "type": "array",
                        "description": "list of products quantities to take order of products, e.g. ['2', '3']",
                        "items": {"type": "string"},
                    },
                },
                "required": ["sku", "quantity"],
            },
        },
        {
            "name": "get_customer_name_phone_delivery_address",
            "description": "Usefull to get the name, phone no and delivery Address of the customer",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "name of the customer, (e.g. huzaifa, jack)",
                    },
                    "phone_no": {
                        "type": "string",
                        "description": "phone or contact number of the customer, (e.g. 03216098981, +923212639741)",
                    },
                    "address": {
                        "type": "string",
                        "description": "delivery Address of the customer, (e.g. 127/45 clifton phase 5 karachi)",
                    },
                },
                "required": [],
            },
        },
        {
            "name": "get_order_confirmation",
            "description": "if customer confirm the order and delivery address so it is essential to always must call this function 'get_order_confirmation' to notify vendor",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    ]

    response = initialize_chat_model(messages=messages, functions=functions)
    response_message = response["choices"][0]["message"]

    # Step 2: check if GPT wanted to call a function
    if response_message.get("function_call"):
        # Step 3: call the function

        available_functions = {
            "get_all_available_products": get_all_available_products,
            "get_product_details": get_product_details,
            "get_order": get_order,
            "get_customer_name_phone_delivery_address": get_customer_name_phone_delivery_address,
            "get_order_confirmation": get_order_confirmation,
        }  # can have multiple functions

        function_name = response_message["function_call"]["name"]
        fuction_to_call = available_functions[function_name]
        function_args = json.loads(response_message["function_call"]["arguments"])
        print(f'functions: {function_name}')

        # I got this solution because first I put all args togheter and-> TypeError: websearch() got an unexpected keyword argument 'location'
        if function_name == "get_all_available_products":
            function_response = fuction_to_call(
                db=db,
                business_id=business_id,
            )

        elif function_name == "get_product_details":
            function_response = fuction_to_call(
                sku_no=function_args.get("sku"),
                db=db,
                business_id=business_id,
            )

        if function_name == "get_order":
            function_response = fuction_to_call(
                sku_no=function_args.get("sku"),
                quantity=function_args.get("quantity"),
                db=db,
                user_no=user_no,
                business_id=business_id,
            )

        if function_name == "get_customer_name_phone_delivery_address":
            function_response = fuction_to_call(
                name=function_args.get("name"),
                phone_no=function_args.get("phone_no"),
                address=function_args.get("address"),
                db=db,
                user_no=user_no,
            )

        elif function_name == "get_order_confirmation":
            function_response = fuction_to_call(
                db=db,
                user_no=user_no,
                business_id=business_id,
            )

        else:
            function_response = ''

        # Step 4: send the info on the function call and function response to GPT
        messages.append(response_message)  # extend conversation with assistant's reply
        messages.append(
            {
                "role": "function",
                "name": function_name,
                "content": function_response,
            }
        )  # extend conversation with function response

        second_response = initialize_function_model(messages=messages) # get a new response from GPT where it can see the function response

        # print(second_response)
        return second_response

    else:
        return response
