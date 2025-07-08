from django.db import models


class Product(models.Model):
    name =  models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

class User(models.Model):
    user =  models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=100)
    payment_status = models.CharField(max_length=50)
    estimated_delivery = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
 
    def __str__(self):
        return f"Order #{self.id}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)

    @property
    def subtotal(self):
        return self.unit_price * self.quantity
