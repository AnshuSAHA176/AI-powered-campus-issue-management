from django.urls import path
from .views import ComplaintCreateView,ComplaintCURDView,SimilarCompliants

urlpatterns=[
    path('',ComplaintCreateView.as_view(),name="complaint_add"),
    path('<str:complaint_id>/',ComplaintCURDView.as_view(),name='RUD oparetions'),
    path('similar/<str:compliant_id>/',SimilarCompliants.as_view(),name='RUD oparetions')
]
