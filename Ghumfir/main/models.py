from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import UniqueConstraint
from django.utils import timezone
from django.conf import settings

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, max_length=100)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)

    mobile_no = models.CharField(max_length=15, null=True, blank=True)
    profile_picture = models.ImageField(upload_to='Profile', null=True, blank=True)
    points = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []  

    objects = CustomUserManager()

    def __str__(self):
        return self.email
    
class EmergencyEmail(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    emergency_email = models.EmailField()

    def __str__(self):
        return f"{self.user.email} - {self.emergency_email}"
    
class Memory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='memories')
    location_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.first_name} at {self.location_name}"

class MemoryMedia(models.Model):
    MEMORY_MEDIA_TYPES = [
        ('image', 'Image'),
        ('video', 'Video'),
    ]

    memory = models.ForeignKey(Memory, on_delete=models.CASCADE, related_name='media')
    file = models.FileField(upload_to='Memories')
    media_type = models.CharField(max_length=10, choices=MEMORY_MEDIA_TYPES)

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.media_type} for {self.memory.location_name}"
    
class GuideProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    primary_location = models.CharField(max_length=250)
    secondary_location = models.CharField(max_length=250, null=True, blank=True)
    EXPERIENCE_YEARS = [
        ('no experience', 'No Experience'),
        ('1-3 yrs', '1-3 Yrs'),
        ('3-5 yrs', '3-5 Yrs'),
        ('above 5 yrs', 'Above 5 Yrs')
    ]
    experience = models.CharField(max_length=20, choices=EXPERIENCE_YEARS)
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=0.0)
    description = models.TextField(null=True, blank=True)
    languages = models.CharField(max_length=350)
    specialization = models.CharField(max_length=150, null=True, blank=True)
    rate_per_hour = models.DecimalField(max_digits=8, decimal_places=2)
    Licenced = models.BooleanField(default=False)
    trip_completed = models.PositiveIntegerField(default=0)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.user.email
    
class Place(models.Model):
    DESTINATION_TYPE_CHOICES = [
    ("cultural", "Cultural"),
    ("natural", "Natural"),
    ("historical", "Historical"),
    ("adventure", "Adventure"),
    ("religious", "Religious"),
    ("mix", "Mixed/Other"),
    ]


    DIFFICULTY_CHOICES = [
    ("easy", "Easy"),
    ("moderate", "Moderate"),
    ("hard", "Hard"),
    ("extreme", "Extreme"),
    ]


    POPULARITY_CHOICES = [
    ("very_low", "Very Low"),
    ("low", "Low"),
    ("medium", "Medium"),
    ("high", "High"),
    ("very_high", "Very High"),
    ]


    name = models.CharField("Place Name", max_length=200, unique=True)
    region = models.CharField("Region/District", max_length=200, blank=True)
    destination_type = models.CharField(
    "Type of Destination", max_length=20, choices=DESTINATION_TYPE_CHOICES, default="mix"
    )
    popularity = models.CharField(
    "Popularity", max_length=20, choices=POPULARITY_CHOICES, default="medium"
    )

    best_season = models.CharField("Best Season to Visit", max_length=100, blank=True)
    starting_point = models.CharField("Starting Point", max_length=200, blank=True)
    route_overview = models.TextField("Route Overview", blank=True)
    ending_point = models.CharField("Ending Point", max_length=200, blank=True)
    duration_days = models.PositiveIntegerField("Duration (Days)", null=True, blank=True, help_text="Approximate number of days")

    altitude_m = models.IntegerField("Altitude/Elevation (Meters)", null=True, blank=True)
    difficulty = models.CharField(
    "Difficulty Level", max_length=20, choices=DIFFICULTY_CHOICES, default="moderate"
    )

    transportation_access = models.TextField("Transportation Access", blank=True,
    help_text="How to reach: road, flight, trek, etc.")
    lodges_hotels = models.TextField("Available Lodges/Hotels", blank=True)
    food_availability = models.CharField("Food Availability", max_length=200, blank=True)
    permit_required = models.BooleanField("Permit Required", default=False)
    emergency_facilities = models.TextField("Emergency Facilities", blank=True)

    adventure_type = models.CharField(max_length=200, blank=True, null=True)
    cultural_attractions = models.TextField(blank=True, null=True)
    language_customs = models.TextField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    local_community = models.CharField(max_length=200, blank=True, null=True)
    not_to_miss_spots = models.TextField(blank=True, null=True)
    photography_hotspots = models.TextField(blank=True, null=True)
    unique_traditions = models.TextField(blank=True, null=True)
    wildlife_highlights = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
    
class PlaceUpdate(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    place = models.ForeignKey(Place, on_delete=models.CASCADE)
    update = models.CharField(max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.place.name} - {self.user.email}: {self.update[:30]}"
