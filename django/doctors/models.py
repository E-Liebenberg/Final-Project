from django.db import models
from django.contrib.auth.models import User
from patients.models import Patient

# Create your models here.
class DoctorNote(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='doctor_notes')
    doctor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    content = models.TextField()

    def __str__(self):
        return f"Doctor note for {self.patient} by {self.doctor} on {self.timestamp.strftime('%Y-%m-%d %H:%M')}"


