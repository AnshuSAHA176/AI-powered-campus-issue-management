from django.db.models.signals import post_save,pre_save,post_delete

from django.dispatch import receiver
from .models import Complaint,ComplaintStatusHistory
from django.core.cache import cache
from channels.layers import get_channel_layer

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



@receiver(post_save,sender= Complaint)
def update_officer_work_status(sender, instance, **kwargs):
    ACTIVE_STATUSES = [
    Complaint.Status.ASSIGNED,
    Complaint.Status.ACCEPTED,
    Complaint.Status.INSPECTION,
    Complaint.Status.IN_PROGRESS,
    Complaint.Status.REOPENED,
]
    if not instance.assigned_officer:
        return 
    if instance.status in [
        Complaint.Status.RESOLVED,
        Complaint.Status.CLOSED,
        Complaint.Status.REJECTED,
    ]:
        officer_profile=instance.assigned_officer.officer_profile
        complaint=Complaint.objects.filter(
            assigned_officer=instance.assigned_officer,
            status__in=ACTIVE_STATUSES
        ).exists()
        if not complaint:
            officer_profile.in_work=False
            officer_profile.save(update_fields=["in_work"])


@receiver([post_delete,post_save],sender=Complaint)
def invalidate_dashboard_cache(sender, instance, **kwargs):
     cache.delete(key=f'dashbord:{instance.reporter_id}')


@receiver(post_save,sender=Complaint)
def notification(sender,created,instance,**kwargs):
    channel_layer = get_channel_layer()
    if created:
        if instance.assigned_officer:
            group_name=f"user_{instance.assigned_officer_id}"
            event={
                "type":"assigned_officer_message"
            }