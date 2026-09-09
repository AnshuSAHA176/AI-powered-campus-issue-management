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
from django.db.models import Q,Count,When,Value,Case,IntegerField

from ..complaint.serializers import ComplaintTitleSerializer
from ..complaint.models import Complaint
from django.core.cache import cache
from rest_framework.permissions import BasePermission
from ..complaint.serializers import ComplaintTitleSerializer
from django.utils import timezone
from datetime import timedelta

class IsOfficer(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.RoleChoices.OFFICER



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
            issues_by_category = list(
            complaint
            .values("category")
            .annotate(count=Count("category"))
        )

            issues_by_status = list(
                    complaint
                    .values("status")
                    .annotate(count=Count("status"))
                )

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
    

class OfficerDashbordView(APIView):
    
    permission_classes=[IsOfficer]
    authentication_classes=[JWTAuthentication]
    def get(self,request):

        ACTIVE_STATUSES = [
            Complaint.Status.ASSIGNED,
            Complaint.Status.ACCEPTED,
            Complaint.Status.INSPECTION,
            Complaint.Status.IN_PROGRESS,
            Complaint.Status.REOPENED,
        ]
        complaint = Complaint.objects.filter(assigned_officer=request.user)
        summery = complaint.aggregate(
            total_assigned=Count('id'),
            active = Count(
                'id',
                filter=
                Q(status__in=ACTIVE_STATUSES)),
            pending=Count(
                'id',filter=Q(status=Complaint.Status.PENDING)
            ),
            in_progress=Count('id',filter=Q(status=Complaint.Status.IN_PROGRESS)),
            inspection=Count('id',filter=Q(status=Complaint.Status.INSPECTION)),
            resolved=Count('id',filter=Q(status=Complaint.Status.RESOLVED)),
            closed=Count('id',filter=Q(status=Complaint.Status.CLOSED)),
            urgent = Count(
                    "id",
                filter=Q(priority__in=["high", "critical"])
            ),

            critical = Count(
                "id",
                filter=Q(priority="critical")
            ), 
            )
        issues_by_status = list(complaint.values('status').annotate(count=Count('status')))
       
        issues_by_priority = list(complaint.values('priority').annotate(count = Count('priority')))

        issues_by_category = list(complaint.values('category').annotate(count = Count('category')))
        priority_order = Case(
            When(priority="critical", then=Value(1)),
            When(priority="high", then=Value(2)),
            When(priority="medium", then=Value(3)),
            When(priority="low", then=Value(4)),
            default=Value(5),
            output_field=IntegerField(),
        )
        needs_attention = (
            complaint.filter(status__in=ACTIVE_STATUSES)
            .annotate(priority_order=priority_order)
            .order_by('priority_order','created_at')
                           )[:4]
        recent_complaints = complaint.order_by('-created_at')[:4]
        now= timezone.now()
        week_start=now - timedelta(days=now.weekday())
        week_start = week_start.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0
        )
        month_start = now.replace(
                day=1,
                hour=0,
                minute=0,
                second=0,
                microsecond=0
            )
        resolved_this_week = complaint.filter(Q(created_at__gte=week_start)&Q(status=Complaint.Status.RESOLVED)).count()
        resolved_this_month = complaint.filter(Q(created_at__gte=month_start)&Q(status=Complaint.Status.RESOLVED)).count()



        return Response(
            {
    "summary": {
        "total_assigned":  summery['total_assigned'],
        "active": summery['active'],
        "pending": summery['pending'],
        "in_progress": summery['in_progress'],
        "inspection": summery['inspection'],
        "resolved":  summery['resolved'],
        "closed":  summery['closed'],
        "urgent": summery['urgent'],
        "critical": summery['critical']
    },

    "issues_by_status": issues_by_status,

    "issues_by_priority": issues_by_priority,

    "issues_by_category": issues_by_category,

    "needs_attention":ComplaintTitleSerializer(needs_attention,many=True).data,

    "recent_complaints": ComplaintTitleSerializer(recent_complaints,many=True).data,

    "performance": {
        "resolved_this_week": resolved_this_week,
        "resolved_this_month": resolved_this_month
    }
}
        )