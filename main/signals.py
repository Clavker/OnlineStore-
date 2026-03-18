from django.db.models.signals import post_save
from django.dispatch import receiver
from users.models import User
from .models import Customer

@receiver(post_save, sender=User)
def create_customer_profile(sender, instance, created, **kwargs):
    """Автоматически создаём профиль Customer при создании User"""
    if created:
        Customer.objects.create(
            user=instance,
            phone="",
            country="",
            city="",
            street_address=""
        )
