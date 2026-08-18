from django.db import models

import uuid

from django.conf import settings
from django.db import models
from config import settings

class Complaint(models.Model):
    class LocationType(models.TextChoices):
            CLASSROOM = "classroom", "Classroom"
            LAB = "lab", "Laboratory"
            HOSTEL = "hostel", "Hostel"
            CANTEEN = "canteen", "Canteen"
            LIBRARY = "library", "Library"
            WASHROOM = "washroom", "Washroom"
            PLAYGROUND = "playground", "Playground"
            OFFICE = "office", "Office"
            ROAD = "road", "Campus Road"
            OTHER = "other", "Other"
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ASSIGNED = "assigned", "Assigned"
        ACCEPTED = "accepted", "Accepted"
        INSPECTION = "inspection", "Inspection"
        IN_PROGRESS = "in_progress", "In Progress"
        RESOLVED = "resolved", "Resolved"
        CLOSED = "closed", "Closed"
        REJECTED = "rejected", "Rejected"
        REOPENED = "reopened", "Reopened"

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        CRITICAL = "critical", "Critical"

    class Category(models.TextChoices):
        ELECTRICAL = "electrical", "Electrical"
        WATER = "water", "Water"
        CLEANLINESS = "cleanliness", "Cleanliness"
        INFRASTRUCTURE = "infrastructure", "Infrastructure"
        SECURITY = "security", "Security"
        INTERNET = "internet", "Internet"
        CLASSROOM = "classroom", "Classroom"
        HOSTEL = "hostel", "Hostel"
        OTHER = "other", "Other"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    # --------------------------------------------------------
    # Reporter
    # --------------------------------------------------------

    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="complaints",
    )

    # --------------------------------------------------------
    # Complaint information
    # --------------------------------------------------------

    title = models.CharField(
        max_length=255,
    )

    description = models.TextField()

    category = models.CharField(
        max_length=30,
        choices=Category.choices,
        default=Category.OTHER,
    )

    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.MEDIUM,
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.PENDING,
    )

    # --------------------------------------------------------
    # Location
    # --------------------------------------------------------

   

    location_type = models.CharField(
        max_length=30,
        choices=LocationType.choices,
        default=LocationType.OTHER,
    )

    building = models.CharField(
        max_length=150,
        blank=True,
    )

    room_number = models.CharField(
        max_length=50,
        blank=True,
    )

    landmark = models.CharField(
        max_length=255,
        blank=True,
    )

    assigned_officer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_complaints",
    )

    # --------------------------------------------------------
    # Resolution
    # --------------------------------------------------------

    resolution_note = models.TextField(
        blank=True,
    )

    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    closed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    # --------------------------------------------------------
    # AI analysis
    # --------------------------------------------------------

    ai_category = models.CharField(
        max_length=100,
        blank=True,
    )

    ai_priority = models.CharField(
        max_length=20,
        blank=True,
    )

    ai_confidence = models.FloatField(
        null=True,
        blank=True,
    )

    ai_summary = models.TextField(
        blank=True,
    )

    # --------------------------------------------------------
    # Timestamps
    # --------------------------------------------------------

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-created_at"]

        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["priority"]),
            models.Index(fields=["category"]),
            models.Index(fields=["reporter"]),
            models.Index(fields=["assigned_officer"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.title} - {self.status}"




class ComplaintImage(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    complaint = models.ForeignKey(
        Complaint,
        on_delete=models.CASCADE,
        related_name="images",
    )

    image = models.ImageField(
        upload_to="complaints/",
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return f"Image for {self.complaint.title}"




class ComplaintStatusHistory(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    complaint = models.ForeignKey(
        Complaint,
        on_delete=models.CASCADE,
        related_name="status_history",
    )

    old_status = models.CharField(
        max_length=30,
        blank=True,
    )

    new_status = models.CharField(
        max_length=30,
    )

    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
    )

    note = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return (
            f"{self.complaint.title}: "
            f"{self.old_status} → {self.new_status}"
        )