from rest_framework import serializers

from .models import Complaint,ComplaintImage

from django.db import transaction
from .complaint_analyze import after_complaint_created

from django.db.models import Count,Q
from apps.account.models import OfficerProfile
from django.utils import timezone
from .storage import temp_storage
class CompliantImageSerializer(serializers.ModelSerializer):
     
     class Meta:
          model=ComplaintImage
          fields=[
               
               'image',
               'uploaded_at'
               
               
          ]

class ComplainCreateSerializer(serializers.ModelSerializer):

    image_uploads = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=True
    )

    assigned_officer = serializers.CharField(
        source="assigned_officer.officer_profile.full_name",
        read_only=True
    )

    class Meta:
        model = Complaint
        fields = [
            'reporter',
            'title',
            'description',
            'location_type',
            'building',
            'room_number',
            'landmark',
            'assigned_officer',
            'image_uploads',
            'complaint_id',
        ]
        extra_kwargs = {
            'reporter': {"read_only": True},
        }

    def create(self, validated_data):
        images = validated_data.pop('image_uploads', [])
        validated_data.pop("reporter", None)

        ACTIVE_STATUSES = [
            Complaint.Status.ASSIGNED,
            Complaint.Status.ACCEPTED,
            Complaint.Status.INSPECTION,
            Complaint.Status.IN_PROGRESS,
            Complaint.Status.REOPENED,
        ]

        temp_paths = [
            temp_storage.save(f"temporary/{image.name}", image)
            for image in images
        ]

        try:
            with transaction.atomic():
                officer = (
                    OfficerProfile.objects
                    .select_for_update(skip_locked=True)
                    .annotate(
                        active_count=Count(
                            "user__assigned_complaints",
                            filter=Q(user__assigned_complaints__status__in=ACTIVE_STATUSES)
                        ),
                    )
                    .order_by('in_work', 'active_count', 'pk')
                    .first()
                )

                if officer:
                    validated_data["assigned_officer"] = officer.user
                    validated_data["status"] = Complaint.Status.ASSIGNED
                    officer.in_work = True
                    officer.save(update_fields=["in_work"])

                complaint = Complaint.objects.create(
                    reporter=self.context['request'].user,
                    **validated_data,
                )

                transaction.on_commit(
                    lambda complaint_id=complaint.complaint_id, paths=temp_paths:
                        after_complaint_created(complaint_id, paths)
                )
        except Exception:
            # complaint was never created (or txn rolled back) — clean up orphaned temp files
            for path in temp_paths:
                temp_storage.delete(path)
            raise

        return complaint







         


class ComplaintTitleSerializer(serializers.ModelSerializer):
   
    class Meta:
        model=Complaint
        fields=[
             "title",
             'category',
             'status',
             'building',
             'priority'

        ]

class ComplaintDetailsSerializer(serializers.ModelSerializer):
     images=CompliantImageSerializer(
          many=True,
          read_only=True,
          
     )
     assigned_officer=serializers.CharField(
           source='assigned_officer.officer_profile.full_name',
           read_only=True
     )

     class Meta:
          model=Complaint

          fields="__all__"

class ComplaintOwnerUpdateSerializer(serializers.ModelSerializer):
     class Meta:
          model=Complaint
          fields=[
               'title',
               'description',
               'building',
               'room_number',
                'landmark'
          ]

     def update(self, instance, validated_data):
          for item , valu in validated_data.items():
               setattr(instance,item,valu)
          instance.save()
          return instance






class CompliantAssisgedOfficerSerializer(serializers.ModelSerializer):
     class Meta:
          model=Complaint
          fields=[
               'status',
               'resolution_note'
          ]
     def validate(self, attrs):
          if attrs.get("status") == "resolved" and not attrs.get("resolution_note"):
               raise serializers.ValidationError(
                    "You must provide resolution_note"
               )

          return attrs
     def update(self, instance, validated_data):
          if validated_data.get("status") == Complaint.Status.RESOLVED:
            validated_data["resolved_at"] = timezone.now()
          return super().update(instance, validated_data)
               



