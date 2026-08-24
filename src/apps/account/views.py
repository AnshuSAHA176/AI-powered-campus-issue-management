from rest_framework import generics
from rest_framework.permissions import AllowAny,IsAuthenticated,IsAdminUser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken,AccessToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import User,StudentProfile,OfficerProfile
from .serializer import (
    RegisterSerializer,
    LoginSerializer,
    StudentProfileSerializer,
    OfficerProfileSerializer
)
from django.shortcuts import get_object_or_404
from django.db.models import Q,F,Avg,Max,Min

class RegisterView(generics.CreateAPIView):
    throttle_scope='register'
    permission_classes=[AllowAny]
    queryset=User.objects.all()
    serializer_class=RegisterSerializer


class LoginView(APIView):
    permission_classes=[AllowAny]
    throttle_scope = 'login'
    def post(self,request):
        serializer=LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user=serializer.validated_data['user']
        refresstoken=RefreshToken.for_user(user)
        accesstoken=refresstoken.access_token
        return Response({
            "access":str(accesstoken),
            "refresh":str(refresstoken)

        })

class ProfileView(generics.RetrieveUpdateAPIView):
    authentication_classes = [
        JWTAuthentication,
    ]

    permission_classes=[IsAuthenticated]
    
   
    def get_object(self):
        if self.request.user.role == User.RoleChoices.STUDENT:
            return get_object_or_404(StudentProfile,user=self.request.user)
        elif self.request.user.role == User.RoleChoices.OFFICER:
            return get_object_or_404(OfficerProfile,user=self.request.user)
    def get_serializer_class(self):
        if self.request.user.role == User.RoleChoices.STUDENT:
            return  StudentProfileSerializer
        elif self.request.user.role == User.RoleChoices.OFFICER:
            return OfficerProfileSerializer


# {
#   "total_issues": 12,
#   "open_issues": 4,
#   "resolved_issues": 7,
#   "pending_issues": 1,
#   "recent_issues": [],
#   "issues_by_category": {},
#   "issues_by_status": {}
# }



