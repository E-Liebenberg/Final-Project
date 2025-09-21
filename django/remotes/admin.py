from django.contrib import admin
from .models import Remote

@admin.register(Remote)
class RemoteAdmin(admin.ModelAdmin):
    list_display = ('remote_id', 'mac_address', 'ward', 'bed', 'assigned_to')
    search_fields = ('remote_id', 'mac_address', 'ward', 'bed', 'assigned_to')
    list_filter = ('ward',)