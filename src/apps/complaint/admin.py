from django.contrib import admin
from .models import Complaint,ComplaintImage,ComplaintSimilarity
admin.site.register(Complaint)
admin.site.register(ComplaintImage)
admin.site.register(ComplaintSimilarity)
