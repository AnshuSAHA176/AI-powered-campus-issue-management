from rest_framework import serializers
from .models import User,StudentProfile,OfficerProfile
from django.contrib.auth import authenticate
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=[
        
            'email',
            'role',
            'password'

        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }
    def create(self, validated_data):

        user=User.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    email=serializers.EmailField()
    password=serializers.CharField(write_only=True)
    def validate(self, attrs):
        user=authenticate(email=attrs['email'],password=attrs['password'])
        if user !=None:
            attrs['user']=user
            return attrs
        else:
            raise serializers.ValidationError("wrong email and password")


class StudentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model=StudentProfile
        fields=[
            'student_id',
            'full_name',
            'department',
            'semester',
            'profile_image',
        ]

class OfficerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model=OfficerProfile
        fields=[
            'employ_id',
            'full_name',
            'department',
            'phone_number',
            'profile_picture',
            'designation',
        ]