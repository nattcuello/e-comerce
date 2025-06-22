
from .models import Profile

class ProfileRepository:
    @staticmethod
    def create_profile(user):
        return Profile.objects.create(user=user)

    @staticmethod
    def get_by_user(user):
        return Profile.objects.filter(user=user).first()
