# profiles/services.py
from profiles.models import Profile

from django.shortcuts import get_object_or_404

class ProfileService:
    @staticmethod
    def get_profile_by_user(user):
        return get_object_or_404(Profile, user=user)

    @staticmethod
    def update_profile(user, data):
        profile = ProfileService.get_profile_by_user(user)
        for attr, value in data.items():
            setattr(profile, attr, value)
        profile.save()
        return profile
