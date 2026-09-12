from rest_framework import serializers

from .models import Complaint, ComplaintImage,ComplaintSimilarity
from .complaint_analyze import after_complaint_created
from .storage import temp_storage

from django.db import transaction
from django.db.models import Count
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from apps.account.models import OfficerProfile


class CompliantImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = ComplaintImage
        fields = [
            "image",
            "uploaded_at",
        ]


class ComplainCreateSerializer(serializers.ModelSerializer):

    image_uploads = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=True,
    )

    assigned_officer = serializers.CharField(
        source="assigned_officer.officer_profile.full_name",
        read_only=True,
    )

    class Meta:
        model = Complaint
        fields = [
            "reporter",
            "title",
            "description",
            "location_type",
            "building",
            "room_number",
            "landmark",
            "assigned_officer",
            "image_uploads",
            "complaint_id",
        ]

        extra_kwargs = {
            "reporter": {
                "read_only": True,
            },
        }

    def create(self, validated_data):

        images = validated_data.pop("image_uploads", [])

        # Reporter comes from request.user
        validated_data.pop("reporter", None)

        ACTIVE_STATUSES = [
            Complaint.Status.ASSIGNED,
            Complaint.Status.ACCEPTED,
            Complaint.Status.INSPECTION,
            Complaint.Status.IN_PROGRESS,
            Complaint.Status.REOPENED,
        ]

        # --------------------------------
        # Save uploaded images temporarily
        # --------------------------------

        temp_paths = []

        try:

            for image in images:
                path = temp_storage.save(
                    f"temporary/{image.name}",
                    image,
                )

                temp_paths.append(path)

            # --------------------------------
            # Database transaction
            # --------------------------------

            with transaction.atomic():

                # --------------------------------
                # 1. Lock all officer rows
                # --------------------------------

                officers = list(
                    OfficerProfile.objects
                    .select_for_update()
                    .select_related("user")
                    .all()
                )

                officer = None

                if officers:

                    # --------------------------------
                    # 2. Calculate active complaints
                    # --------------------------------

                    officer_ids = [
                        officer.user_id
                        for officer in officers
                    ]

                    counts = (
                        Complaint.objects
                        .filter(
                            assigned_officer_id__in=officer_ids,
                            status__in=ACTIVE_STATUSES,
                        )
                        .values("assigned_officer_id")
                        .annotate(
                            active_count=Count("id")
                        )
                    )

                    # Example:
                    #
                    # {
                    #     12: 4,
                    #     15: 2,
                    #     18: 7
                    # }

                    count_map = {
                        item["assigned_officer_id"]: item["active_count"]
                        for item in counts
                    }

                    # --------------------------------
                    # 3. Find least-loaded officer
                    # --------------------------------

                    officer = min(
                        officers,
                        key=lambda officer: (
                            officer.in_work,
                            count_map.get(
                                officer.user_id,
                                0,
                            ),
                            officer.pk,
                        ),
                    )

                # --------------------------------
                # 4. Assign officer
                # --------------------------------

                if officer:

                    validated_data["assigned_officer"] = officer.user

                    validated_data["status"] = (
                        Complaint.Status.ASSIGNED
                    )

                    officer.in_work = True

                    officer.save(
                        update_fields=["in_work"]
                    )

                # --------------------------------
                # 5. Create complaint
                # --------------------------------

                complaint = Complaint.objects.create(
                    reporter=self.context["request"].user,
                    **validated_data,
                )

                # --------------------------------
                # 6. Start Celery AFTER commit
                # --------------------------------

                transaction.on_commit(
                    lambda
                    complaint_id=str(complaint.complaint_id),
                    paths=temp_paths.copy():
                        after_complaint_created(
                            complaint_id,
                            paths,
                        )
                )

        except Exception:

            # --------------------------------
            # Delete temporary files
            # if database transaction fails
            # --------------------------------

            for path in temp_paths:
                temp_storage.delete(path)

            raise

        return complaint






         


class ComplaintTitleSerializer(serializers.ModelSerializer):
   
    class Meta:
        model=Complaint
        fields=[
            "complaint_id",
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
        model = Complaint
        fields = [
            "title",
            "description",
            "building",
            "room_number",
            "landmark",
        ]

    def update(self, instance, validated_data):

        # --------------------------------
        # Store OLD values before updating
        # --------------------------------

        old_data = {
            "title": instance.title,
            "description": instance.description,
            "building": instance.building,
            "room_number": instance.room_number,
            "landmark": instance.landmark,
        }

        # --------------------------------
        # Find changed fields
        # --------------------------------

        changed_fields = [
            field
            for field, new_value in validated_data.items()
            if old_data.get(field) != new_value
        ]

        # --------------------------------
        # Update complaint
        # --------------------------------

        for field, value in validated_data.items():
            setattr(instance, field, value)

        instance.save(
            update_fields=list(validated_data.keys())
        )

        # --------------------------------
        # Notify assigned officer
        # --------------------------------

        if changed_fields and instance.assigned_officer_id:

            channel_layer = get_channel_layer()

            group_name = f"user_{instance.assigned_officer_id}"

            event = {
                "type": "officer_notification",
                "notification_type": "complaint.details_updated",
                "message": (
                    "📝 Complaint details updated\n"
                    f"Complaint: {instance.title}\n"
                    f"Complaint ID: {instance.complaint_id}\n"
                    f"Updated fields: {', '.join(changed_fields)}"
                ),
            }

            async_to_sync(
                channel_layer.group_send
            )(
                group_name,
                event
            )

        return instance


ALLOWED_TRANSITIONS = {
    "pending": ["assigned", "rejected"],
    "assigned": ["accepted", "rejected"],
    "accepted": ["inspection", "in_progress"],
    "inspection": ["in_progress"],
    "in_progress": ["resolved"],
    "resolved": ["closed", "reopened"],
    "closed": [],
    "rejected": [],
    "reopened": ["assigned"],
}


class CompliantAssisgedOfficerSerializer(serializers.ModelSerializer):
     class Meta:
          model=Complaint
          fields=[
               'status',
               'resolution_note'
          ]
     def validate(self, attrs):
          compliant_status=self.instance.status
          if attrs.get("status") == "resolved" and not attrs.get("resolution_note"):
                         raise serializers.ValidationError(
                              "You must provide resolution_note"
                         )
          
          current_status = self.instance.status
          new_status = attrs.get("status")

          if new_status not in ALLOWED_TRANSITIONS.get(current_status, []):
                raise serializers.ValidationError({
                    "status": (
                        f"Invalid status transition: "
                        f"'{current_status}' → '{new_status}'. "
                        f"Allowed transitions: "
                        f"{', '.join(ALLOWED_TRANSITIONS.get(current_status, [])) or 'none'}."
                    )
                })
          
                        
          
          return attrs
     def update(self, instance, validated_data):
          
          if validated_data.get("status") == Complaint.Status.RESOLVED:
            validated_data["resolved_at"] = timezone.now()
          return super().update(instance, validated_data)
               



class SemilarCompliantSerializer(serializers.ModelSerializer):
    complaint_id=serializers.CharField(
        source='similar_complaint.complaint_id'
    )
    complaint_title=serializers.CharField(
        source='similar_complaint.title'
    )
    class Meta:
        model=ComplaintSimilarity
        fields=[
            'complaint_id',
            'complaint_title',
            'similarity_score',
        ]
