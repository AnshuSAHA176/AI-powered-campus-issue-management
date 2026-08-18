from django.contrib import admin
from .models import StudentProfile,OfficerProfile,User


admin.site.register(User)
admin.site.register(StudentProfile)
admin.site.register(OfficerProfile)