from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_bcrypt import Bcrypt
from sqlalchemy import JSON

db = SQLAlchemy()
bcrypt = Bcrypt()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')


class Profile(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(255), nullable=False) 
    filename = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('files', lazy=True))

    def __init__(self, filename, user_id, user, name, role):
        self.filename = filename
        self.user_id = user_id
        self.user = user
        self.name = name
        self.role = role


class ChatHistory(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    chat_history = db.Column(JSON, nullable=False)
    bot_id = db.Column(db.Integer, db.ForeignKey('profile.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('chat_histories', lazy=True))
    bot = db.relationship('Profile', backref=db.backref('chat_histories', lazy=True))

    def __init__(self, chat_history, bot_id, user_id):
        self.chat_history = chat_history
        self.bot_id = bot_id
        self.user_id = user_id
