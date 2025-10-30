import os
from django.db import models
import uuid
from django.utils import timezone
from django.contrib.auth.models import User

class Project(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
    )
    
    # HVAC System Type Choices
    HVAC_CHOICES = (
        ('individual', 'Individual'),
        ('cassette', 'Cassette'),
        ('split_ac', 'Split AC'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    fixtures = models.JSONField(
        default=dict,
        blank=True,
        help_text="JSON field to store fixture configuration for the project"
    )

    # Section 1: General Information
    address = models.TextField(
        blank=True, 
        null=True,
        default="Shop No 1, Ground Floor, House No 3, Survey 390, 796, MG Road, Pune, Maharashtra",
        help_text="Enter the full address of the site"
    )
    location_reference = models.CharField(
        max_length=255, 
        blank=True, 
        null=True,
        default="LKST212-MG road, Pune",
        help_text="Reference code or location name"
    )

    # Section 2: Site Details
    total_carpet_area = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        blank=True, 
        null=True,
        default=2186,
        help_text="Total carpet area in sq.ft."
    )
    floor_level = models.CharField(
        max_length=255, 
        blank=True, 
        null=True,
        default="Ground floor",
        help_text="Specify the floor or level of the site"
    )
    electricity_load = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        blank=True, 
        null=True,
        default=30,
        help_text="Electricity load capacity in KW"
    )
    electricity_meter_location = models.CharField(
        max_length=255, 
        blank=True, 
        null=True,
        default="Basement Floor",
        help_text="Location of the electricity meter"
    )

    # Section 3: HVAC and Utilities
    hvac_system_type = models.CharField(
        max_length=50, 
        choices=HVAC_CHOICES, 
        blank=True, 
        null=True,
        default='individual',
        help_text="Type of HVAC system"
    )
    ac_outdoor_units_location = models.CharField(
        max_length=255, 
        blank=True, 
        null=True,
        default="Back wall of the store",
        help_text="Location of AC outdoor units"
    )
    drainage_facility = models.BooleanField(
        default=False,
        help_text="Drainage facility available within premises"
    )
    water_connection = models.BooleanField(
        default=False,
        help_text="Water connection available within premises"
    )

    # Section 4: Site Orientation and Access
    main_entrance_direction = models.CharField(
        max_length=50, 
        blank=True, 
        null=True,
        default="West",
        help_text="Direction of the main entrance"
    )
    nearest_airport = models.CharField(
        max_length=255, 
        blank=True, 
        null=True,
        default="Pune International Airport",
        help_text="Name of the nearest airport"
    )
    airport_distance = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        blank=True, 
        null=True,
        default=9.5,
        help_text="Distance to nearest airport in KM"
    )
    nearest_railway_station = models.CharField(
        max_length=255, 
        blank=True, 
        null=True,
        default="Pune Railway Station",
        help_text="Name of the nearest railway station"
    )
    railway_station_distance = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        blank=True, 
        null=True,
        default=2.2,
        help_text="Distance to nearest railway station in KM"
    )

    # Section 5: Additional Facilities
    washroom = models.CharField(
        max_length=500, 
        blank=True, 
        null=True,
        default="Common washroom available",
        help_text="Washroom availability details"
    )
    remarks = models.TextField(
        blank=True, 
        null=True,
        help_text="Additional remarks or notes about the site"
    )

    # Section 6: Room Measurements
    room_measurements = models.JSONField(
        default=dict,
        blank=True,
        help_text="JSON field to store room measurements with walls data"
    )

    merch_mix_min = models.JSONField(
        default=dict,
        blank=True,
        help_text="JSON field to store minimum merch mix configuration"
    )
    merch_mix_max = models.JSONField(
        default=dict,
        blank=True,
        help_text="JSON field to store maximum merch mix configuration"
    )
    updated_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='updated_projects'
    )

    
class ProjectFile(models.Model):
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='project_files/%Y/%m/%d/')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.project.name} - {self.filename}"
    
    @property
    def filename(self):
        return os.path.basename(self.file.name)
    
    @property
    def file_type(self):
        _, ext = os.path.splitext(self.file.name)
        return ext.lower().lstrip('.')
    
    @property
    def is_image(self):
        return self.file_type in ['png', 'jpg', 'jpeg']
    
    @property
    def is_processed_file(self):
        return self.file_type.lower() == 'fcstd'
    
    def get_processed_files(self):
        """Get all processed files related to this file"""
        base_name = os.path.splitext(self.filename)[0]
        return ProjectFile.objects.filter(
            project=self.project,
            file__contains=base_name,
            file__endswith='.FCStd'
        ).exclude(id=self.id)
    
    def has_processed_files(self):
        """Check if this file has any processed versions"""
        return self.get_processed_files().exists()

class SiteMedia(models.Model):
    """Model to store site pictures and videos"""
    
    MEDIA_TYPE_CHOICES = (
        ('image', 'Image'),
        ('video', 'Video'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='site_media')
    file = models.FileField(upload_to='site_media/%Y/%m/%d/')
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.project.name} - Site {self.media_type} - {self.filename}"
    
    @property
    def filename(self):
        return os.path.basename(self.file.name)
    
    @property
    def file_type(self):
        _, ext = os.path.splitext(self.file.name)
        return ext.lower().lstrip('.')
    
    @property
    def is_image(self):
        return self.file_type in ['png', 'jpg', 'jpeg']
    
    @property
    def is_video(self):
        return self.file_type in ['mp4']
    
    def save(self, *args, **kwargs):
        # Auto-set media_type based on file extension
        if self.is_image:
            self.media_type = 'image'
        elif self.is_video:
            self.media_type = 'video'
        super().save(*args, **kwargs)
