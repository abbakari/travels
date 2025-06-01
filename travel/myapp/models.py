from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class User(AbstractUser):
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)

class Destination(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='destinations/')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.CharField(max_length=50)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

class Package(models.Model):
    name = models.CharField(max_length=100)
    destinations = models.ManyToManyField(Destination)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.CharField(max_length=50)
    image = models.ImageField(upload_to='packages/')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    package = models.ForeignKey(Package, on_delete=models.CASCADE)
    booking_date = models.DateTimeField(default=timezone.now)
    travel_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    guests = models.PositiveIntegerField(default=1)
    special_requests = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.package.name}"

class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.subject
    
from django.db import models
from django.utils import timezone

class SystemSetting(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    duration_in_minutes = models.IntegerField(default=1)  # Duration until expiration
    is_active = models.BooleanField(default=True)

    @property
    def expiration_time(self):
        """Calculate expiration time based on created_at and duration."""
        return self.created_at + timezone.timedelta(minutes=self.duration_in_minutes)

    def __str__(self):
        return f"Active: {self.is_active} - Expires at {self.expiration_time.strftime('%Y-%m-%d %H:%M:%S')}"
