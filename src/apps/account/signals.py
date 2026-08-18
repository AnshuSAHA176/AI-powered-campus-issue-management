from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User,StudentProfile,OfficerProfile


@receiver(sender=User,signal=post_save)
def create_profile(sender,instance,created,**kwargs):
    if not created:
        return 
    if instance.role == User.RoleChoices.STUDENT:
        StudentProfile.objects.create(user=instance)

    elif instance.role == User.RoleChoices.OFFICER:
        OfficerProfile.objects.create(user=instance)

