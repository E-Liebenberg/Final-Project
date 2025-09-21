# theatre/models.py

from django.db import models
from django.utils import timezone

class TheatreLog(models.Model):
    theatre_id = models.CharField(max_length=50)
    topic = models.CharField(max_length=100)
    value = models.CharField(max_length=255)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.theatre_id}: {self.topic} → {self.value}"

class Theatre(models.Model):
    theatre_id = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.theatre_id