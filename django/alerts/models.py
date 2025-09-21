from django.db import models

# Create your models here.
from remotes.models import Remote

class Alert(models.Model):
    ALERT_TYPES = [
        ('code_blue', 'Code Blue'),
        ('motion', 'Motion'),
        ('sound', 'Sound'),
        ('nurse_call', 'Nurse Call'),
    ]

    remote = models.ForeignKey(Remote, on_delete=models.CASCADE)
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)
    acknowledged = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.remote} - {self.alert_type} at {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"