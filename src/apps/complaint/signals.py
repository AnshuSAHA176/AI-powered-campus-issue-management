from django.db.models.signals import post_save,pre_save

from django.dispatch import receiver
from .models import Complaint,ComplaintStatusHistory

@receiver(pre_save, sender=Complaint)
def previos_data(sender, instance,  **kwargs):
    if not instance.pk:
        instance._old_status=None
        return 
    try:
        precvious_data=Complaint.objects.get(pk=instance.pk)
        instance._old_status=precvious_data.status
    except Complaint.DoesNotExist:
        instance._old_status=None



@receiver(post_save,sender=Complaint)
def statushistorysave(sender, instance, created, **kwargs):
    if not created:
        if instance._old_status and instance._old_status!=instance.status:
            ComplaintStatusHistory.objects.create(
                complaint=instance,
                old_status=instance._old_status,
                new_status=instance.status
            )

