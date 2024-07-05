"""page"""

import openai
from configuration import configure, constants

openai.api_key = configure.openai_api_key


def initialize_chat_model(messages, functions):
    """_summary_

    Returns:
        _type_: _description_
    """
    # Initialize and return the chat model
    return openai.ChatCompletion.create(
        model=constants.GPT_API_NAME,
        temperature=constants.GPT_MODEL_TEMPERATURE,
        messages=messages,
        functions=functions,
        function_call="auto",
    )


def initialize_function_model(messages):
    """_summary_

    Returns:
        _type_: _description_
    """
    # Initialize and return the function model
    return openai.ChatCompletion.create(
        model=constants.GPT_API_NAME,
        temperature=constants.GPT_MODEL_TEMPERATURE,
        messages=messages,
    )