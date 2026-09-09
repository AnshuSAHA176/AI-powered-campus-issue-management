from django.db.models.signals import post_save,pre_save,post_delete

from django.dispatch import receiver
from .models import Complaint,ComplaintStatusHistory
from django.core.cache import cache
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

@receiver(pre_save, sender=Complaint)
def previos_data(sender, instance,  **kwargs):
    if not instance.pk:
        instance._old_status=None
        instance._priority=None
        return 
    try:
        precvious_data=Complaint.objects.get(pk=instance.pk)
        instance._old_status=precvious_data.status
        instance._priority=precvious_data.priority
    except Complaint.DoesNotExist:
        instance._old_status=None
        instance._priority=None



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


@receiver(post_save, sender=Complaint)
def officer_notification(sender, created, instance, **kwargs):
    message=None
    if not created:
        return

    channel_layer = get_channel_layer()

    # No officer assigned
    if not instance.assigned_officer:

        group_name = f"user_{instance.reporter_id}"

        event = {
            "type": "unassigned_officer_message",
            "message": (
                "🔔 Your new complaint is currently unassigned\n"
                f"Complaint: {instance.title}\n"
                "We will notify you when an officer is assigned."
            )
        }

        async_to_sync(channel_layer.group_send)(
            group_name,
            event
        )

        return

    else:
        group_name = f"user_{instance.assigned_officer_id}"
        message = '🔔 New complaint assigned'

        if instance._priority and instance._priority != instance.priority:
            message = '⚠️ Priority changed'

        if instance.status == Complaint.Status.REOPENED:
            message = '🔄 Complaint reopened — action required'
        if ins
        
    if message:
        event = {
                "type": "assigned_officer_message",
                "message": (
                    f"{message}\n"
                    f"Complaint: {instance.title}\n"
                    f"Created by: {instance.reporter.student_profile.full_name}"
                )
            }

        async_to_sync(channel_layer.group_send)(
                group_name,
                event
            )


@receiver(post_save, sender=Complaint)
def student_notification(sender, created, instance, **kwargs):
    channel_layer=get_channel_layer()
    group_name=f"user_{instance.reporter_id}"
    message=None
    if created:
        message=f'You Complaint with id {instance.complaint_id} successfully created'
        
    else:
        if instance.status ==Complaint.Status.ACCEPTED:
            message="✅ Your complaint has been accepted."
        elif instance.status == Complaint.Status.ASSIGNED:
            message = "🔔 Officer has been assigned to your complaint."
        elif instance.status == Complaint.Status.INSPECTION:
            message =  "🔍 An officer has started inspecting your complaint."
        elif instance.status == Complaint.Status.IN_PROGRESS:
            message =  "🛠️ Work has started on your complaint."
        elif instance.status == Complaint.Status.RESOLVED:
            
            message = f"✅ Your complaint has been resolved.\n Resolution Note:- {instance.resolution_note}"
        elif instance.status == Complaint.Status.CLOSED:
            message = "📁 Your complaint has been closed."
        elif instance.status == Complaint.Status.REJECTED:
            message = '❌ Your complaint was rejected.'
        elif instance.status == Complaint.Status.REOPENED:
            message = "🔄 Your complaint has been reopened."
        if instance._priority and instance._priority != instance.priority:
            message = '⚠️ "Your complaint priority changed to High/Critical."'
    if message:
        event = {
            "type":"student_notification",
            "message":f'''
                        {message}
                        f"Complaint: {instance.title}\n"
                        f"Complaint ID : {instance.complaint_id}"
                        '''
        }
        async_to_sync(channel_layer.group_send)(
            group_name,
            event
        )
        