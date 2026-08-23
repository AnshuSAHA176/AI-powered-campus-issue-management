from rest_framework import serializers

from .models import Complaint,ComplaintImage

from django.db import transaction
from .complaint_analyze import ai_analyzer
from django.db.models import Count,Q
from apps.account.models import OfficerProfile
class ComplainCreateSerializer(serializers.ModelSerializer):
    images=serializers.ListField(child=serializers.ImageField(),write_only=False,required=False)
    class Meta:
        model=Complaint
        fields=[
            'reporter',
            'title',
            'description',
            'location_type',
            'building',
            'room_number',
            'landmark',
            'assigned_officer',
            'images',
            'complaint_id',
            

        ]
        extra_kwargs = {
    "assigned_officer": {"read_only": True},
    'reporter':{"read_only": True}
}
    def create(self, validated_data):
               images=validated_data.pop('images',[])
               validated_data.pop("reporter", None)
               title=validated_data.get('title')
               description=validated_data.get('description')
               location_type=validated_data.get('location_type')
               building=validated_data.get('building')
               room_number=validated_data.get('room_number')
               landmark=validated_data.get('landmark')
               result=ai_analyzer(
                              title=title,
                              description=description,
                              location_type=location_type,
                              building=building,
                              room_number=room_number,
                              landmark=landmark,

                                   )
               officer=OfficerProfile.objects.annotate(
                     active_count=Count(
                           "assigned_complaints"
                     ),
                     filter=Q(
                           assigned_complaints__status_in=[
                                 'pending',
                                 'in_progress'
                           ]
                           
                           
                     )

               ).order_by('active_count').first()
               with transaction.atomic():
                         
                         
                         complaint=Complaint.objects.create(
                                   reporter=self.context['request'].user,
                                   **validated_data,
                                   **result
                              )
                         for image in images:
                                   ComplaintImage.objects.create(
                                        complaint=complaint,
                                        image=image
                                   )
               return complaint








         
class CompliantImageSerializer(serializers.ModelSerializer):
     
     class Meta:
          model=ComplaintImage
          fields=[
               
               'image',
               'uploaded_at'
               
               
          ]

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
     
               



