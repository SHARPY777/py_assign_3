import secrets

from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Company


@receiver(post_save, sender=User)
def create_company_profile(sender, instance, created, **kwargs):
    # `created` is True only when the User row is inserted for the first
    # time (i.e. instance._state.adding was True during save()); the ORM
    # flips _state.adding back to False just before post_save fires.
    if created:
        Company.objects.create(
            user=instance,
            company_name=instance.email,  # overwritten by view
            api_key=secrets.token_urlsafe(32)
        )
