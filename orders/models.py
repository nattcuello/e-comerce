from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


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



class CardInfo(models.Model):
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE)
    card_holder = models.CharField(max_length=100)
    card_number = models.CharField(max_length=100)
    expiration = models.DateField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.card_holder} - {self.card_number[-4:]}"


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('confirmed', 'Confirmado'),
        ('processing', 'En proceso'),
        ('shipped', 'Enviado'),
        ('delivered', 'Entregado'),
        ('cancelled', 'Cancelado'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE)
    order_number = models.CharField(max_length=20, unique=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.ForeignKey(PaymentStatus, on_delete=models.CASCADE)
    estimated_delivery = models.DateField(null=True, blank=True)
    fiscal_condition = models.ForeignKey(FiscalCondition, on_delete=models.CASCADE)
    shipping_address = models.CharField(max_length=255, blank=True)
    shipping_city = models.CharField(max_length=100, blank=True)
    shipping_postal_code = models.CharField(max_length=20, blank=True)
    shipping_phone = models.CharField(max_length=20, blank=True)
    notes = models.TextField(blank=True)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Order #{self.order_number or self.id}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"ORD{str(self.id or '').zfill(6)}"
        self.total = self.get_total()
        super().save(*args, **kwargs)

    def get_total_standard(self):
        return sum(item.subtotal for item in self.standard_items.filter(is_active=True))

    def get_total_card(self):
        return sum(item.subtotal for item in self.card_items.filter(is_active=True))

    def get_total(self):
        return self.get_total_standard() + self.get_total_card() + self.shipping_cost + self.tax_amount


class OrderDetail(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="standard_items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)

    @property
    def subtotal(self):
        if self.unit_price is None or self.quantity is None:
            return 0
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
    def unit_price_with_offer(self):
        if self.unit_price is None:
            return 0
        return self.unit_price - self.discount if self.offer else self.unit_price

    @property
    def subtotal(self):
        price = self.unit_price_with_offer
        if price is None or self.quantity is None:
            return 0
        return price * self.quantity

    @property
    def total_installments(self):
        sub = self.subtotal
        if not self.installments:
            return sub
        return sub / self.installments