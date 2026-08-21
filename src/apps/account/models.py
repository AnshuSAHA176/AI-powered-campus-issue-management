from django.db import models

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
import uuid
from .cutom_user_manageger import Customemanager


class User(AbstractBaseUser,PermissionsMixin):
    

    class RoleChoices(models.TextChoices):
        STUDENT=('student','student')
        OFFICER=('officer','Officer')
        ADMIN=('admin','Admin')


    objects=Customemanager()
    id=models.UUIDField(primary_key=True,default=uuid.uuid4)   

    
    email = models.EmailField(
        verbose_name="email address",
        max_length=255,
        unique=True,
    )
    
    is_active = models.BooleanField(
        default=True
    )

    is_staff = models.BooleanField(
        default=False
    )

    username=None
    USERNAME_FIELD = "email"
    role=models.CharField(max_length=20 ,choices=RoleChoices.choices,default=RoleChoices.STUDENT)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    REQUIRED_FIELDS = []



    def __str__(self):
        return self.email



class StudentProfile(models.Model):

    id=models.UUIDField(primary_key=True,default=uuid.uuid4)

    user=models.OneToOneField(User,on_delete=models.CASCADE,related_name="student_profile")

    student_id=models.CharField(max_length=200,unique=True,null=True,blank=True)

    full_name=models.CharField(max_length=300,blank=True,null=True)

    department=models.CharField(max_length=200,null=True,blank=True)

    semester=models.PositiveIntegerField(null=True,blank=True)

    profile_image=models.ImageField(upload_to='profile',blank=True,null=True)

    created_at = models.DateTimeField(
            auto_now_add=True,
        )
    
    updated_at = models.DateTimeField(
            auto_now=True,
        )
    def __str__(self):
        return f"{self.full_name} id-{self.student_id}"

class OfficerProfile(models.Model):

    id=models.UUIDField(primary_key=True,default=uuid.uuid4)

    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name="officer_profile")

    employ_id=models.CharField(max_length=200,unique=True,null=True,blank=True)

    full_name=models.CharField(max_length=300,blank=True,null=True)

    phone_number=models.IntegerField(null=True,blank=True)

    department=models.CharField(max_length=200,null=True,blank=True)
    
    designation = models.CharField(
        max_length=100,
    )

    profile_picture = models.ImageField(
        upload_to="profiles/officers/",
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )
    def __str__(self):
        return  f"{self.full_name} id-{self.student_id}"