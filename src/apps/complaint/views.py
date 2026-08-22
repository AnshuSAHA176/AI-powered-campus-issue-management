from rest_framework import generics
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from .models import Complaint
from .serializers import (
                          ComplainCreateSerializer,
                          ComplaintTitleSerializer,
                          ComplaintOwnerUpdateSerializer,
                          CompliantAssisgedOfficerSerializer,
                          ComplaintDetailsSerializer
                          )

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import viewsets

from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response


class IsComplaintOwner(BasePermission):
     def has_permission(self, request, view):
          return request.user.is_authenticated and request.user.role == 'student'
     def has_object_permission(self, request, view, obj):
          return obj.reporter == request.user


class IsAssingedOfficer(BasePermission):
     def has_permission(self, request, view):
          return request.user.is_authenticated and request.user.role =='officer'
     def has_object_permission(self, request, view, obj):
          return obj.assigned_officer == request.user


class ComplaintCreateView(generics.ListCreateAPIView):
    authentication_classes=[
         JWTAuthentication
    ]
    permission_classes=[IsAuthenticated]
    

    def get_serializer_class(self):
        if self.request.method == "POST":
                return ComplainCreateSerializer
        
        return ComplaintTitleSerializer
    def get_queryset(self):
         return Complaint.objects.filter(reporter=self.request.user).prefetch_related('images')
    def perform_create(self, serializer):
         return serializer.save(reporter=self.request.user)




class ComplaintCURDView(generics.RetrieveUpdateDestroyAPIView):
     authentication_classes=[
          JWTAuthentication
     ]
     lookup_field='complaint_id'
     lookup_url_kwarg='complaint_id'

     def get_queryset(self):
          user=self.request.user
          if user.role=='student':
               return Complaint.objects.filter(reporter=user).prefetch_related('images') 
          elif user.role == 'officer':
               return Complaint.objects.filter(assigned_officer=user).prefetch_related('images') 
          return Complaint.objects.prefetch_related('images')
     def get_permissions(self):
          user=self.request.user
          if user.role=='student':
               return [IsComplaintOwner()]
          elif user.role == 'officer':
               return [IsAssingedOfficer()]
          elif user.role == 'admin':
               return [IsAdminUser()]
          return [IsAuthenticated()]
     def perform_destroy(self, instance):
          if instance.reporter==self.request.user or self.request.user.role == 'admin':
               instance.delete()
               
          else:
               raise PermissionDenied('You do not have permission to perfrom this action')
     def get_serializer_class(self):
         if self.request.method in ["PUT", "PATCH"]:
              if self.request.user.role=='student':
                   return ComplaintOwnerUpdateSerializer
              elif self.request.user.role == 'officer':
                   return CompliantAssisgedOfficerSerializer
              else:
                   return ComplaintDetailsSerializer

         return ComplaintDetailsSerializer


class ComplaintViewSet(viewsets.ViewSet):
     permission_classes=[IsAuthenticated]
     def list(self, request):
        complaint=Complaint.objects.prefetch_related('images')
        serializer=ComplaintTitleSerializer(complaint,many=True)
        return Response({
             "complaint":serializer.data
        })