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
from django.db.models import Q,F,Avg,Max,Min,Count
from ..complaint.serializers import ComplaintTitleSerializer
from ..complaint.models import Complaint
from django.core.cache import cache




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





class StudentDashBord(APIView):

    permission_classes=[IsAuthenticated]
    authentication_classes=[JWTAuthentication]
    
    def get(self , request):
            cache_key=f'dashbord:{request.user.id}'
            cache_data=cache.get(cache_key)

            if cache_data is not None:
                return Response(cache_data)
            
            complaint=Complaint.objects.filter(reporter=request.user)

            compliant_data=complaint.aggregate(
                total_issues=Count('id'),
                open_issues=Count('id',filter=~Q(status='resolved')),
                resolved_issues=Count('id',filter=Q(status='resolved')),
                pending_issues=Count('id',filter=Q(status='pending')),


            )
            issues_by_category=complaint.values('category').annotate(count=Count('category'))
            issues_by_status=complaint.values('status').annotate(count=Count('status'))

            recent_issues=complaint.order_by('-created_at')[:6]
            data = {
                    "total_issues": compliant_data['total_issues'],
                    "open_issues": compliant_data['open_issues'],
                    "resolved_issues": compliant_data['resolved_issues'],
                    "pending_issues": compliant_data['pending_issues'],
                    "recent_issues":  ComplaintTitleSerializer(
                                recent_issues,
                                many=True
                            ).data,
                    "issues_by_category": issues_by_category,
                    "issues_by_status": issues_by_status
                    }
            cache.set(
                cache_key,
                data,
                timeout=60*15
            )
            return Response( 

                data

                )
    

