from django.db import models
from django.contrib.auth.models import User
from remotes.models import Remote
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.conf import settings

def generate_patient_number(length=6):
    prefix = getattr(settings, 'PATIENT_NUMBER_PREFIX', 'PAT')
    return f"{prefix}{get_random_string(length=length, allowed_chars='0123456789')}"

GENDER_CHOICES = [
    ('M', 'Male'),
    ('F', 'Female'),
    ('O', 'Other'),
]

class Patient(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    patient_number = models.CharField(max_length=20, unique=True, editable=False, default='')
    first_name = models.CharField(max_length=100, default='Unknown')
    last_name = models.CharField(max_length=100, default='Unknown')
    national_id = models.CharField(max_length=50, unique=False, null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)
    country = models.CharField(max_length=100, default="Unknown")

    medical_condition = models.TextField(blank=True)
    stock_used = models.TextField(blank=True)
    stock_billed = models.TextField(blank=True)

    ward = models.CharField(max_length=50)
    bed = models.CharField(max_length=10)
    rfid_tag = models.CharField(max_length=100, unique=True, null=True, blank=True)
    admitted = models.BooleanField(default=False)
    remote = models.OneToOneField(Remote, null=True, blank=True, on_delete=models.SET_NULL)

    doctor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='patients')

    created_at = models.DateTimeField(default=timezone.now)  # TEMPORARY


    def save(self, *args, **kwargs):
        if not self.patient_number:
            self.patient_number = generate_patient_number()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.patient_number})"

class NurseNote(models.Model):
    NOTE_TYPES = [
        ('medication', 'Medication Given'),
        ('vitals', 'Vital Signs'),
        ('request', 'Patient Request'),
        ('general', 'General Note'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='nurse_notes')
    nurse = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    note_type = models.CharField(max_length=20, choices=NOTE_TYPES, default='general')
    content = models.TextField()

    def __str__(self):
        return f"{self.note_type} for {self.patient} by {self.nurse} on {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

