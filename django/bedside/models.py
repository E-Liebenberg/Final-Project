from django.db import models

class BedsideUnit(models.Model):
    bed_id = models.CharField(max_length=32, unique=True)  # e.g. bedsidev3
    friendly_name = models.CharField(max_length=64, blank=True)

class Alert(models.Model):
    class Type(models.TextChoices):
        CODE_BLUE   = "code_blue",   "Code Blue"
        NURSE_CALL  = "nurse_call",  "Nurse Call"
        NO_MOVEMENT = "no_movement", "No Movement"

    unit        = models.ForeignKey(BedsideUnit, on_delete=models.CASCADE)
    alert_type  = models.CharField(max_length=20, choices=Type.choices)
    active      = models.BooleanField(default=True)
    acknowledged= models.BooleanField(default=False)
    timestamp   = models.DateTimeField(auto_now_add=True)

class SensorReading(models.Model):
    unit        = models.ForeignKey(BedsideUnit, on_delete=models.CASCADE)
    temperature = models.FloatField()
    humidity    = models.FloatField()
    recorded_at = models.DateTimeField(auto_now_add=True)

class RFIDTagLog(models.Model):
    unit        = models.ForeignKey(BedsideUnit, on_delete=models.CASCADE)
    tag_uid     = models.CharField(max_length=32)
    scanned_at  = models.DateTimeField(auto_now_add=True)
