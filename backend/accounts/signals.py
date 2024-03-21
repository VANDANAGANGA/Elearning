# your_app_name/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Course, Room

@receiver(post_save, sender=Course)
def create_room(sender, instance, created, **kwargs):
    """
    Signal receiver function to create a Room instance when a Course is saved.
    """
    if created:
        Room.objects.create(course=instance, teacher=instance.teacher)
