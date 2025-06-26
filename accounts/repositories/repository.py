# accounts/repository/user_repository.py
from accounts.models import User
from django.core.exceptions import ObjectDoesNotExist

class UserRepository:

    @staticmethod
    def get_user_by_email(email):
        try:
            return User.objects.get(email=email)
        except ObjectDoesNotExist:
            return None

    @staticmethod
    def create_user(data):
        return User.objects.create(**data)
