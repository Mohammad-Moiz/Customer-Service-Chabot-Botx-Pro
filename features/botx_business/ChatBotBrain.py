"""page"""

import openai
import json, os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
from features.botx_business.functions_actions import get_product_details, get_available_products
from features.product.models import ProductModel
from features.botx_business.dependency import format_business_description

def get_product_list(db: Session, business_id)-> list:
    # Create a list of messages for the chat model
    products = (
        db.query(ProductModel)
        .where((ProductModel.vendor_id == business_id) & (ProductModel.available) & (ProductModel.category == 'furniture'))
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

#define main chatcompletion - Chatbot whit functions call
def run_conversation(db: Session, business_id: int, prompt):
    # Step 1: send the conversation and available functions to GPT
    product_list = get_product_list(db = db, business_id = business_id)
    system_prompt = format_business_description(business_id, product_list)
    messages = [
        {"role": "system", "content": f"{system_prompt}"},
        {"role": "user", "content": f"{prompt}?"}, ]
    
    functions = [
        {
            "name": "get_available_products",
            "description": "Usefull to provide available products according to category in our stock now.",
            "parameters": {
                "type": "object",
                "properties": {
                    "category":{
                        "type":"string",
                        "description": "category to search available products in stock, e.g. furniture, cell phone accessories"
                    },
                    
                },
                "required": ["category"],
            },
        },
        
        {
            "name": "get_product_details",
            "description": "Get the details of products using sku of that products",
            "parameters": {
                "type": "object",
                "properties": {
                    "sku": {
                        "type": "string",
                        "description": "list of sku_no to search details of products in our stock, e.g. [16298202, 16294810]",
                    },
                },
                "required": ["sku"],
            },
        },
    ]
    

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages=messages,
        functions=functions,
        function_call="auto", 
    )
    response_message = response["choices"][0]["message"]

    # Step 2: check if GPT wanted to call a function
    if response_message.get("function_call"):
        # Step 3: call the function
        
        available_functions = {
            "get_product_details": get_product_details, 
            "get_available_products":get_available_products,

        }  # can have multiple functions

        function_name = response_message["function_call"]["name"]
        fuction_to_call = available_functions[function_name]
        function_args = json.loads(response_message["function_call"]["arguments"])
        

        #I got this solution because first I put all args togheter and-> TypeError: websearch() got an unexpected keyword argument 'location'
        if function_name == "get_product_details":
            function_response = fuction_to_call(
                sku_no=function_args.get("sku"),
                db=db,
                business_id=business_id
            )
        
        elif function_name == "get_available_products":
            function_response = fuction_to_call(
                category=function_args.get("category"),
                db = db,
                business_id = business_id,
                product_list = str(product_list),
            )

        else:
            function_response = None

        # Step 4: send the info on the function call and function response to GPT
        messages.append(response_message)  # extend conversation with assistant's reply
        messages.append(
            {
                "role": "function",
                "name": function_name,
                "content": function_response,
            }
        )  # extend conversation with function response

        second_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
            messages=messages,
        )  # get a new response from GPT where it can see the function response

        #print(second_response)
        return second_response
    
    else:
        return response
