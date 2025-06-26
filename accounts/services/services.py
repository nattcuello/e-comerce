from accounts.repositories.repository import UserRepository
from django.contrib.auth.hashers import check_password
import jwt
from datetime import datetime, timedelta
from django.conf import settings

def authenticate_user(email, password):
    user = UserRepository.get_user_by_email(email)
    if user and check_password(password, user.password_hash):
        return user
    return None

def generate_jwt_for_user(user):
    payload = {
        'user_id': user.id,
        'role_id': user.role_id,
        'exp': datetime.utcnow() + timedelta(hours=1),
        'iat': datetime.utcnow()
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return token
