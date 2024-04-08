from django.db.models.signals import post_save
from django.dispatch import receiver

from feed.models import User, Profile, Follower


@receiver(post_save, sender=User, dispatch_uid="test_data")
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        Follower.objects.create(follower=instance, following=instance)
