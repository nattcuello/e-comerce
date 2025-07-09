from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Product, Audit
from django.contrib.auth.models import User

@receiver(post_save, sender=Product)
def log_product_save(sender, instance, created, **kwargs):
    action = 1 if created else 2
    Audit.objects.create(
        user=instance.user,
        action_id=action,
        affected_table='Product',
        description=f'Product "{instance.name}" was {"created" if created else "updated"}.'
    )

@receiver(post_delete, sender=Product)
def log_product_delete(sender, instance, **kwargs):
    Audit.objects.create(
        user=instance.user,
        action_id=3,
        affected_table='Product',
        description=f'Product "{instance.name}" was deleted.'
    )
