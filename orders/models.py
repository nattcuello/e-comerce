from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)


class State(models.Model):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)


class PaymentMethod(models.Model):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)


class PaymentStatus(models.Model):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)


class Persona(models.Model):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)


class Company(models.Model):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)


class FiscalCondition(models.Model):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)


class IvaCondition(models.Model):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)


class CardInfo(models.Model):
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE)
    card_holder = models.CharField(max_length=100)
    card_number = models.CharField(max_length=100)
    expiration = models.DateField()
    is_active = models.BooleanField(default=True)


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.ForeignKey(PaymentStatus, on_delete=models.CASCADE)
    estimated_delivery = models.DateField(null=True, blank=True)
    fiscal_condition = models.ForeignKey(FiscalCondition, on_delete=models.CASCADE)
    iva_condition = models.ForeignKey(IvaCondition, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Order #{self.id}"


class OrderDetail(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="standard_items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)

    @property
    def subtotal(self):
        return self.unit_price * self.quantity


class OrderDetailCard(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="card_items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    card_info = models.ForeignKey(CardInfo, on_delete=models.CASCADE)
    cuotas = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField()
    installments = models.PositiveIntegerField()
    offer = models.BooleanField(default=False)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # monto fijo
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)

    @property
    def subtotal(self):
        effective_price = self.unit_price - self.discount if self.offer else self.unit_price
        return effective_price * self.quantity

    @property
    def total_installments(self):
        return self.subtotal / self.installments if self.installments > 0 else self.subtotal

    @property
    def unit_price_with_offer(self):
        return self.unit_price - self.discount if self.offer else self.unit_price
