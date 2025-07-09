from django.db import models
from categories.models import Category, Brand
from django.contrib.auth.models import User

class Product(models.Model):
    name = models.CharField(max_length=100)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    description = models.TextField(max_length=1000, blank=True)
    image = models.TextField(blank=True)
    active = models.BooleanField(default=True)
    stock = models.PositiveIntegerField(default=0)
    min_stock = models.PositiveIntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name

    @property
    def is_below_min_stock(self):
        return self.stock < self.min_stock

class Audit(models.Model):
    ACTION_CHOICES = (
        (1, 'CREATED'),
        (2, 'UPDATED'),
        (3, 'DELETED'),
    )

    TABLE_CHOICES = (
        ('Name', 'Name'),
        ('Category', 'Category'),
        ('Brand', 'Brand'),
        ('Description', 'Description'),
        ('Stock', 'Stock'),
    )

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action_id = models.PositiveSmallIntegerField(choices=ACTION_CHOICES)
    affected_table = models.CharField(max_length=100, choices=TABLE_CHOICES)
    date = models.DateTimeField(auto_now_add=True)
    description = models.TextField()

    def __str__(self):
        return f"{self.get_action_id_display()} by {self.user} on {self.affected_table}"
