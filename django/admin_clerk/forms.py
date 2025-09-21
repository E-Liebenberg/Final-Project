from django import forms
from patients.models import Patient

class RFIDAssignForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['rfid_tag']


class PatientEditForm(forms.ModelForm):
    class Meta:
        model = Patient
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'}),
        }
        exclude = ['user','patient_number', 'remote', 'created_at', 'medical_condition', 'doctor_notes', 'stock_used','stock_billed' ]  # Exclude non-editable/auto fields

class AdminAdmitForm(forms.ModelForm):
    class Meta:
        model = Patient
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'}),
        }
        exclude = ['user','patient_number', 'remote', 'created_at', 'medical_condition', 'doctor_notes', 'stock_used','stock_billed' ]  # Exclude non-editable/auto fields