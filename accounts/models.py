# accounts/models.py
from django.db import models

class User(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=50, unique=True)
    password_hash = models.TextField()
    role_id = models.IntegerField()
    address = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    city_id = models.IntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by_user_id = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name
