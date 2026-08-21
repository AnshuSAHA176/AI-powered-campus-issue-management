from rest_framework import serializers

from .models import Complaint,ComplaintImage







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

        ]
        extra_kwargs = {
    "assigned_officer": {"read_only": True},
    'reporter':{"read_only": True}
}
    def create(self, validated_data):
        images=validated_data.pop('images', [])
        complaint=Complaint.objects.create(**validated_data)
        
        for image in images:
                ComplaintImage.objects.create(
                      
                      complaint=complaint,image=image
                      )
        return complaint

class CompliantImageSerializer(serializers.ModelSerializer):
     title=serializers.CharField(source='complaint.title')
     class Meta:
          model=ComplaintImage
          fields=[
               'title',
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
               'room_number'
                'landmark'
          ]

class CompliantAssisgedOfficerSerializer(serializers.ModelSerializer):
     class Meta:
          model=Complaint
          fields=[
               'status',
               'resolution_note'
          ]
