from django.urls import path
from .views import ComplaintCreateView,ComplaintCURDView

urlpatterns=[
    path('add/',ComplaintCreateView.as_view(),name="complaint_add"),
    path('',ComplaintCURDView.as_view(),name='RUD oparetions')
]
