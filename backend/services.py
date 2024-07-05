from flask_jwt_extended import create_access_token
from models import User, Profile, db, bcrypt
import os

def login_service(data):
    email = data.get('email')
    password = data.get('password')
    
    user = User.query.filter_by(email=email).first()

    if user and bcrypt.check_password_hash(user.password, password):
        access_token = create_access_token(identity=user.id)
        return {'message': 'Login successful', 'access_token': access_token}, 200
    else:
        return {'message': 'Invalid email or password'}, 401

def signup_service(data):
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    existing_user_email = User.query.filter_by(email=email).first()

    if existing_user_email:
        return {'message': 'Email already exists'}, 400

    new_user = User(username=username, email=email, password=password)
    db.session.add(new_user)
    db.session.commit()

    return {'message': 'Signup successful'}, 200

def upload_profile_service(request, current_user_id):
    try:
        user = User.query.get(current_user_id)

        name = request.form.get('name')
        role = request.form.get('role')

        # Check token validity
        if not current_user_id or current_user_id != user.id:
            return {'message': 'Unauthorized'}, 401

        if 'file' not in request.files:
            return {'message': 'No file part'}, 400

        file = request.files['file']
        if file.filename == '':
            return {'message': 'No selected file'}, 400

        file_path = os.path.join(os.path.abspath("uploads"), file.filename)
        file.save(file_path)

        new_profile = Profile(filename=file.filename, user_id=current_user_id, user=user, name=name, role=role)
        db.session.add(new_profile)
        db.session.commit()

        return {'message': 'File uploaded successfully'}, 200

    except Exception as error:
        print(f"Error: {error}")


def get_profile_history_service(current_user_id):
    
    if current_user_id:
        profiles = Profile.query.filter(Profile.user.has(id=current_user_id)).all()
        profile_history = [{'id': profile.id, 'filename': profile.filename, 'name':profile.name, 'role':profile.role} for profile in profiles]
        return {'profile_history': profile_history}
    
    else:
        return {'error': 'User not authenticated'}


def get_current_user_service(current_user_id):
    user = User.query.get(current_user_id)
    return {'username': user.username, 'email': user.email}, 200