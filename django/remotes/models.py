from django.db import models

# Create your models here.
class Remote(models.Model):
    remote_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    mac_address = models.CharField(max_length=17, blank=True, null=True)
    ip_address = models.GenericIPAddressField(protocol='both', unpack_ipv4=True, blank=True, null=True)
    ward = models.CharField(max_length=100)
    bed = models.CharField(max_length=100)
    assigned_to = models.CharField(max_length=100, blank=True, null=True)  # Optional patient name

    def __str__(self):
        rid = self.remote_id or "Unassigned"
        return f"{self.ward} - {self.bed} [{rid}]"