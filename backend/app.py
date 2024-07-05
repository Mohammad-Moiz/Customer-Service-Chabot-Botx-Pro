import os
import json
import datetime
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_login import LoginManager, login_required, logout_user, current_user
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

from sqlalchemy import JSON
from langchain_core.messages import AIMessage, HumanMessage

from utility_functions import remove_date_and_time, convert_into_list_of_dictionary
from prompts import system_message
from chatbot import conversation_chain, message_to_dict
from models import db, User, Profile, ChatHistory
from services import login_service, signup_service, upload_profile_service, get_profile_history_service, get_current_user_service

load_dotenv()

app = Flask(__name__)
CORS(app)

host = os.getenv("POSTGRES_HOST")
port = os.getenv("POSTGRES_PORT")
username = os.getenv("POSTGRES_USERNAME")
password = os.getenv("POSTGRES_PASSWORD")
database = os.getenv("POSTGRES_DB")


app.config[
    "SQLALCHEMY_DATABASE_URI"
] = f"postgresql://{username}:{password}@{host}/{database}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SECRET_KEY'] = 'secretkeyforauthentication'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(minutes=15, hours=6)

jwt = JWTManager(app)
bcrypt = Bcrypt(app)
db.init_app(app)
bcrypt.init_app(app)
login_manager = LoginManager(app) 


def save_chat_history(chat_history_data, user_id, bot_id):
    
    # Retrieve existing chat history
    existing_chat = ChatHistory.query.filter_by(bot_id=bot_id).first()

    if existing_chat:
        
        existing_data = json.loads(existing_chat.chat_history)
        # print(existing_data)
        new_data = json.loads(chat_history_data)
        combined_data = existing_data + new_data

        # Update the existing record
        existing_chat.chat_history = json.dumps(combined_data, indent=4)
    else:
        
        # Create a new record if it doesn't exist
        combined_data = json.loads(chat_history_data)
        new_chat_history = ChatHistory(chat_history=json.dumps(combined_data, indent=4), bot_id=bot_id, user_id=user_id)
        db.session.add(new_chat_history)

    db.session.commit()

def load_chat_history(bot_id):
    
    # Retrieve the chat history for the given bot_id
    chat_history_record = ChatHistory.query.filter_by(bot_id=bot_id).first()
    
    if chat_history_record:
        return chat_history_record.chat_history
    else:
        return None

def reply(question, config, user_id, bot_id):

    chain, memory = conversation_chain(config)
    
    output = chain.invoke(question)
    formatted_messages = [message_to_dict(message) for message in memory.buffer_as_messages]
    json_data = json.dumps(formatted_messages, indent=4)
    save_chat_history(json_data, user_id=user_id, bot_id=bot_id)
    # print("yahan pay",json_data)
    
    return output['text']


# Manage login 
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Login Api
@app.route("/login", methods=['POST'])
def login():
    data = request.json
    return login_service(data)


# Signup Api
@app.route("/signup", methods=['POST'])
def signup():
    data = request.json
    return signup_service(data)


# Logout Api
@app.route("/logout", methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logout successful'}), 200


# Upload Profile Api
@app.route("/upload", methods=['POST', 'GET'])
@jwt_required()
def upload_file():
    current_user_id = get_jwt_identity()
    return upload_profile_service(request, current_user_id)


# Profile history
@app.route("/profile_history", methods=['GET'])
@jwt_required()
def get_profile_history():
    current_user_id = get_jwt_identity()
    return get_profile_history_service(current_user_id)


@app.route("/current_user", methods=['GET'])
@jwt_required()
def get_current_user():
    current_user_id = get_jwt_identity()
    return get_current_user_service(current_user_id)


@app.route('/chat_history/<bot_id>', methods=['GET'])
def history(bot_id):

    chat = load_chat_history(bot_id=bot_id)
    
    return {'chat_history': chat }
    


# Chat Api
@app.route('/data/<bot_id>', methods=['POST','GET'])
@jwt_required()
def chat(bot_id):
    user_id = get_jwt_identity()

    print(user_id)
    print(bot_id)

    data = request.get_json()
    if not data or 'message' not in data:
        return {'error': 'Missing message'}, 400

    bot = db.session.query(Profile).filter(Profile.id == bot_id).all()
    for file in bot:
        name = file.name
        role = file.role
        file = file.filename
        print(f'Name: {name}\nRelation: {role}\nFile: {file}\n')
    
    clean_text = remove_date_and_time(f'uploads/{file}')
    converted_format = convert_into_list_of_dictionary(clean_text)

    # print(converted_format)

    config = {
        'name': name, 
        'relation': role,
        'converted_format': converted_format,
        'system_message': system_message,
    }

    human_input = data['message']
    output_text = reply(human_input, config, user_id, bot_id)
    print(output_text)
    return {'message': output_text }, 200


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)