# accounts/models.py

from django.contrib.auth.models import User
from django.db import models

class Profile(models.Model):
    ROLE_CHOICES = [
        ('admin_clerk', 'Admin Clerk'),
        ('nurse', 'Nurse'),
        ('doctor', 'Doctor'),
        ('patient', 'Patient'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"
