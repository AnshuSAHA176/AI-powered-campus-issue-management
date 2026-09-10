from django.urls import path
from .views import AgentView



urlpatterns = [

    path('',AgentView.as_view(),name='agnet')
]