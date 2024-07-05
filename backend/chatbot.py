import os
import logging
from dotenv import load_dotenv
from config import *
from typing import Dict, Any

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain



def chat_openai(model_name: str) -> ChatOpenAI:
    """
    Creates and returns an LLM object with appropriate error handling.

    Args: model_name (str): Name of the LLM model to create.
    Returns: ChatOpenAI: The created LLM object.
    """
    load_dotenv()
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
    if not OPENAI_API_KEY:
        raise ValueError("Missing API key")
    try:
        # create the LLM object
        chat_model = ChatOpenAI(
            model=model_name,
            openai_api_key=OPENAI_API_KEY,
        )
        return chat_model
    except Exception as error:
        if "Invalid API key" in str(error):
            raise ValueError("Invalid API key provided.") from error
        else:

            raise RuntimeError("Unexpected error:", error) from error


def chat_gemini(model_name: str) -> ChatGoogleGenerativeAI:
    """
    Creates and returns an LLM object with appropriate error handling.

    Args: model_name (str): Name of the LLM model to create.
    Returns: ChatGoogleGenerativeAI: The created LLM object.
    """

    load_dotenv()

    GOOGLE_API_KEY = os.environ.get("YOUR_API_KEY")
    if not GOOGLE_API_KEY:
        raise ValueError("Missing API key")

    try:
        # create the LLM object
        chat_model = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=GOOGLE_API_KEY,
            generation_config=generation_config,  
            safety_settings=safety_settings,
            convert_system_message_to_human=True,
        )
        return chat_model

    except Exception as error:
        if "Invalid API key" in str(error):
            raise ValueError("Invalid API key provided.") from error
        else:
            raise RuntimeError("Unexpected error:", error) from error   



def chat_prompt_template(
        variables: Dict[str, str], 
        system_message_template: str) -> ChatPromptTemplate:
    
    """
    Creates a formatted chat prompt template.

    Args:
        variables (Dict[str, str]): Dictionary containing 'name', 'relation', and 'chat'.
        system_message_template (str): The template for the system message.
    Returns: ChatPromptTemplate: A formatted chat prompt template.
    """
    
    try:
        # System Message - Template Text & Variable Dictionary  
        system_message_prompt = SystemMessagePromptTemplate.from_template(system_message_template)
        formatted_system_message = system_message_prompt.prompt.format(**variables)

        # Create the ChatPromptTemplate
        chat_prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content=formatted_system_message
                ),
                MessagesPlaceholder(variable_name="chat_history"),
                HumanMessagePromptTemplate.from_template("{question}")
            ]
        )

        return chat_prompt
    
    except KeyError as error:
        logging.error(f"Missing variable in 'variables' dictionary: {error}")
    except Exception as error:
        logging.error(f"An error occurred: {error}")
 

# Chain
def conversation_chain(config: Dict[str, Any]) -> LLMChain:
    """
    Creates a conversation chain.

    Args:
    config (Dict[str, Any]): 
    A dictionary containing configuration parameters 
    for the conversation chain, including user details.

    Returns:
    Returns an instance of LLMChain
    """
    try:
        memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

        conversation = LLMChain(
            # llm=chat_gemini('gemini-pro'),
            llm=chat_openai('gpt-3.5-turbo'),
            prompt=chat_prompt_template(
                {'name': config.get('name', ''), 
                 'relation': config.get('relation', ''),
                 'chat': config.get('converted_format', '')},
                system_message_template=config.get('system_message', '')
            ),
            verbose=False,
            memory=memory
        )
        return conversation, memory

    except Exception as error:
        logging.error(f"Error creating conversation chain: {error}")
    

# def message_to_dict(message):
#     if isinstance(message, HumanMessage):
#         return {"type": "Human", "content": message.content}
#     elif isinstance(message, AIMessage):
#         return {"type": "AI", "content": message.content}
#     else:
#         return {"type": "Unknown", "content": str(message)}

def message_to_dict(message):
    if isinstance(message, HumanMessage):
        return {"Human": message.content}
    elif isinstance(message, AIMessage):
        return {"AI": message.content}
    else:
        return {"type": "Unknown", "content": str(message)}


# chain, memory = conversation_chain(config)
    
# while True:
#     follow_up = input("input: ")
#     answer = chain.invoke(input=follow_up)
#     formatted_messages = [message_to_dict(message) for message in memory.buffer_as_messages]
    
#     json_data = json.dumps(formatted_messages, indent=4)
    
#     # history after each interaction
#     save_chat_history(formatted_messages, 1, 1)  # user_id, bot_id
    
#     print("output: ", answer['text'])


