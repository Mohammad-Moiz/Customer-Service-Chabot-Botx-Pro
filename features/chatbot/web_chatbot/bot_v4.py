"""page"""

from __future__ import annotations
from sqlalchemy.orm import Session
from features.chatbot.web_chatbot.ChatBotBrain import run_conversation
from features.chatbot.web_chatbot.dependency import (
    load_conversation_from_db,
    save_conversation_to_db,
)


def chat_function(db: Session, user_id: int, business_id: int, user_input: Any) -> Any:
    """_summary_

    Args:
        user_id (_type_): _description_
        business_id (_type_): _description_
        user_input (_type_): _description_

    Returns:
        _type_: _description_
    """    
    history = load_conversation_from_db(db, user_id=user_id, business_id=business_id)
    message_count = 10
    history = history[-message_count:]
    temp_dialogue = []

    history.append(f"User: {user_input}")
    temp_dialogue.append(f"User: {user_input}")
    prompt = "\n".join(history) + "\nAI:"

    result = run_conversation(db, business_id, user_id, prompt)
    final_answer = result['choices'][0]['message']['content']
    
    temp_dialogue.append(f"AI: {final_answer}")

    save_conversation_to_db(db, user_id=user_id, business_id=business_id, conversation_history=temp_dialogue)

    # Optional token and cost calculation
    tok = result.usage.total_tokens
    cost = tok * 0.002 / 1000
 

    print(final_answer)
    
    return final_answer#, history, tok, cost