from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import User

class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'name', 'email', 'password_hash',
            'role_id', 'address', 'phone', 'city_id', 'created_by_user_id'
        ]
        extra_kwargs = {
            'password_hash': {'write_only': True}
        }

    def create(self, validated_data):
        validated_data['password_hash'] = make_password(validated_data['password_hash'])
        return super().create(validated_data) 