"""page"""

from __future__ import annotations
from sqlalchemy.orm import Session
from features.botx_business.ChatBotBrain import run_conversation
from features.botx_business.dependency import (
    format_business_description,
    load_conversation_from_db,
    save_conversation_to_db,
)
from typing import Any

def chat_function(db: Session, user_id: int, business_id: int, user_input: Any) -> Any:
    """_summary_

    Args:
        user_id (_type_): _description_
        business_id (_type_): _description_
        user_input (_type_): _description_

    Returns:
        _type_: _description_
    """    
     # Load conversation history from the database
    history = load_conversation_from_db(db, user_id=user_id, business_id=business_id)
    
    # Ensure history is initialized as a list
    if not isinstance(history, list):
        history = []
    
    # Append user prompt to history
    history.append(f"User: {user_input}")
    
    # Construct prompt with history
    prompt = "\n".join(history) + "\nAI:"
    
    # Run the model
    result = run_conversation(db, business_id, prompt)
    final_answer = result['choices'][0]['message']['content']
    
    # Append AI response to history
    history.append(f"AI: {final_answer}")

    # Save updated conversation history to the database
    save_conversation_to_db(db, user_id=user_id, business_id=business_id, user_input=user_input, ai_response=final_answer)

    # Optional token and cost calculation
    tok = result.usage.total_tokens
    cost = tok * 0.002 / 1000
    
    # Check and manage history size
    if tok >= 1000:
        history.pop(0)  # Remove oldest entry
        print('old history deleted')

    print(final_answer)
    
    return final_answer#, history, tok, cost