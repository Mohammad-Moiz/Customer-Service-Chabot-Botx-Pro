"""page"""

import json
from sqlalchemy.orm import Session
from features.chatbot.web_chatbot.functions_actions import (
    get_product_details,
    get_all_available_products,
    get_order,
    get_delivery_address,
    get_order_confirmation,
)
from features.product.models import ProductModel
from features.chatbot.web_chatbot.dependency import format_business_description
from features.chatbot.web_chatbot.open_ai_config import initialize_chat_model, initialize_function_model


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
def run_conversation(db: Session, business_id: int, user_id: int, prompt):
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
            "name": "get_delivery_address",
            "description": "Usefull to get the delivery Address of the customer",
            "parameters": {
                "type": "object",
                "properties": {
                    "address": {
                        "type": "string",
                        "description": "delivery Address of the customer",
                    },
                },
                "required": ["address"],
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
            "get_delivery_address": get_delivery_address,
            "get_order_confirmation": get_order_confirmation,
        }  # can have multiple functions

        function_name = response_message["function_call"]["name"]
        fuction_to_call = available_functions[function_name]
        function_args = json.loads(response_message["function_call"]["arguments"])

        # I got this solution because first I put all args togheter and-> TypeError: websearch() got an unexpected keyword argument 'location'
        temp = ""
        if function_name == "get_all_available_products":
            function_response = fuction_to_call(
                db=db,
                business_id=business_id,
            )
            temp = temp + function_response

        elif function_name == "get_product_details":
            function_response = fuction_to_call(
                sku_no=function_args.get("sku"),
                db=db,
                business_id=business_id,
            )
            temp = temp + function_response

        if function_name == "get_order":
            function_response = fuction_to_call(
                sku_no=function_args.get("sku"),
                quantity=function_args.get("quantity"),
                db=db,
                user_id=user_id,
                business_id=business_id,
            )
            temp = temp + function_response

        elif function_name == "get_delivery_address":
            function_response = fuction_to_call(
                address=function_args.get("address"),
                db=db,
                user_id=user_id,
            )
            temp = temp + function_response

        elif function_name == "get_order_confirmation":
            function_response = fuction_to_call(
                db=db,
                user_id=user_id,
                business_id=business_id,
            )
            temp = temp + function_response

        else:
            function_response = None

        function_response = temp
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
