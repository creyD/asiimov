from django.db import models
# For tracking Authors and Editors
from django.contrib.auth.models import User
# For catching the save method for keeping user objects in sync
from django.db.models.signals import post_save
from django.dispatch import receiver


# For storing user info like steamID (...)
class Gamer(models.model):
    system_user = models.OneToOneField(User, on_delete=models.CASCADE)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.gamer.save()
