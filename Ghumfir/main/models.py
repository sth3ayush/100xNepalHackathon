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