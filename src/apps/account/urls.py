from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    ProfileView,
    StudentDashBord,
    OfficerDashbordView
   
    )



urlpatterns=[
    path("register/",RegisterView.as_view(),name= "register"),
    path("login/",LoginView.as_view(),name="login"),
    path("profile/",ProfileView.as_view(),name="profile"),
    path('dashbord/',StudentDashBord.as_view(),name='student dashbord'),
    path('dashbord_officer/',OfficerDashbordView.as_view(),name='officer dashbord'),
    
]