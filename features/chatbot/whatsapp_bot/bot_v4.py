"""page"""

from __future__ import annotations
from sqlalchemy.orm import Session
from features.chatbot.whatsapp_bot.ChatBotBrain import run_conversation
from features.chatbot.whatsapp_bot.dependency import (
    load_conversation_from_db,
    save_conversation_to_db,
)


def chat_function(db: Session, user_no: str, business_id: int, user_input: str) -> str:
    """_summary_

    Args:
        user_no (_type_): _description_
        business_id (_type_): _description_
        user_input (_type_): _description_

    Returns:
        _type_: _description_
    """    
    history = load_conversation_from_db(db, user_no=user_no, business_id=business_id)
    message_count = 10
    history = history[-message_count:]
    temp_dialogue = []

    history.append(f"User: {user_input}")
    temp_dialogue.append(f"User: {user_input}")
    prompt = "\n".join(history) + "\nAI:"

    result = run_conversation(db, business_id, user_no, prompt)
    final_answer = result['choices'][0]['message']['content']
    
    temp_dialogue.append(f"AI: {final_answer}")

    save_conversation_to_db(db, user_no=user_no, business_id=business_id, conversation_history=temp_dialogue)

    # Optional token and cost calculation
    tok = result.usage.total_tokens
    cost = tok * 0.002 / 1000
 

    print(final_answer)
    
    return final_answer#, history, tok, cost