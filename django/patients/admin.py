from django.contrib import admin
from .models import Patient

class PatientAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'patient_number', 'dob', 'ward', 'bed', 'admitted', 'gender')  # Customize the fields to show
    search_fields = ('first_name', 'last_name', 'patient_number')  # Enable search by name or patient number
    list_filter = ('admitted', 'ward', 'gender')  # Enable filtering by these fields
    ordering = ('-admitted',)  # Order patients by the admission date (latest first)

# Register the Patient model with custom PatientAdmin
admin.site.register(Patient, PatientAdmin)
