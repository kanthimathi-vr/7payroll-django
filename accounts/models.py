from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    # This role determines access levels
    ROLE_CHOICES = [
        ('ADMIN', 'Admin'),
        ('EMPLOYEE', 'Employee'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='EMPLOYEE')
    # No other fields needed here; employee-specific data goes in EmployeeProfile.
    
    def __str__(self):
        return self.username