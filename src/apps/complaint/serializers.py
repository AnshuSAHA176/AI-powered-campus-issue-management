from rest_framework import serializers

from .models import Complaint,ComplaintImage

from django.db import transaction





class ComplainCreateSerializer(serializers.ModelSerializer):
    images=serializers.ListField(child=serializers.ImageField(),write_only=True,required=False)
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
            'complaint_id'

        ]
        extra_kwargs = {
    "assigned_officer": {"read_only": True},
    'reporter':{"read_only": True}
}
    def create(self, validated_data):
               images=validated_data.pop('images',[])
               validated_data.pop("reporter", None)
               
               complaint=Complaint.objects.create(
                         reporter=self.context['request'].user,
                         **validated_data
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
     
               



