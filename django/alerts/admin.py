from django.contrib import admin
from .models import Alert

@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ('remote', 'alert_type', 'timestamp', 'acknowledged')
    list_filter = ('alert_type', 'acknowledged', 'timestamp')
